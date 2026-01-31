"""
LangGraph workflow definition for agent orchestration.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agents.state import AgentState, create_initial_state
from agents.router import route_message, get_next_agent
from agents.customer_agent import customer_agent
from agents.inventory_agent import inventory_agent
from agents.supplier_agent import supplier_agent
from agents.order_agent import order_agent
from agents.workload_agent import workload_agent
from agents.bottleneck_agent import bottleneck_agent
from database.connection import database
from datetime import datetime
import uuid


# Create memory checkpointer for conversation persistence
memory = MemorySaver()


def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph workflow for agent orchestration.
    """
    # Define the graph with our state schema
    graph = StateGraph(AgentState)
    
    # Add nodes for each agent
    graph.add_node("router", route_message)
    graph.add_node("customer_agent", customer_agent)
    graph.add_node("order_agent", order_agent)
    graph.add_node("inventory_agent", inventory_agent)
    graph.add_node("supplier_agent", supplier_agent)
    graph.add_node("workload_agent", workload_agent)
    graph.add_node("bottleneck_agent", bottleneck_agent)
    
    # Set entry point
    graph.set_entry_point("router")
    
    # Add conditional edges from router to specialized agents
    graph.add_conditional_edges(
        "router",
        get_next_agent,
        {
            "customer_agent": "customer_agent",
            "order_agent": "order_agent",
            "inventory_agent": "inventory_agent",
            "supplier_agent": "supplier_agent",
            "workload_agent": "workload_agent",
            "bottleneck_agent": "bottleneck_agent",
        }
    )
    
    # All agents end after processing
    graph.add_edge("customer_agent", END)
    graph.add_edge("order_agent", END)
    graph.add_edge("inventory_agent", END)
    graph.add_edge("supplier_agent", END)
    graph.add_edge("workload_agent", END)
    graph.add_edge("bottleneck_agent", END)
    
    return graph


# Compile the graph with checkpointing
agent_graph = create_agent_graph().compile(checkpointer=memory)


async def run_agent(
    message: str,
    conversation_id: str | None = None,
    conversation_type: str = "consumer",
    supplier_id: str | None = None
) -> dict:
    """
    Run the agent graph with a user message.
    
    Args:
        message: The user's message
        conversation_id: Existing conversation ID or None for new conversation
        conversation_type: "consumer" or "supplier"
        supplier_id: Supplier ID if this is a supplier conversation
    
    Returns:
        dict with response and conversation_id
    """
    from langchain_core.messages import HumanMessage, AIMessage
    
    # Generate or use existing conversation ID
    if not conversation_id:
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
    
    # Load existing conversation state or create new
    config = {"configurable": {"thread_id": conversation_id}}
    
    # First, load existing messages from database (if any)
    conversations_collection = database.get_collection("conversations")
    existing_conv = await conversations_collection.find_one({"conversation_id": conversation_id})
    
    # Convert database messages to langchain format
    existing_messages = []
    restored_supplier_id = None
    if existing_conv:
        # Restore supplier_id from the existing conversation if it exists
        restored_supplier_id = existing_conv.get("supplier_id")
        print(f"🔍 DEBUG: Restored supplier_id={restored_supplier_id} from conversation {conversation_id}")
        
        for msg in existing_conv.get("messages", []):
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                existing_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                existing_messages.append(AIMessage(content=content))
    
    # Use restored supplier_id if available, otherwise use the one passed to the function
    effective_supplier_id = restored_supplier_id or supplier_id
    
    # Get current state if exists in memory, otherwise create new
    try:
        current_state = agent_graph.get_state(config)
        if current_state.values:
            state = dict(current_state.values)
            # Merge database messages with in-memory messages, preferring database as source of truth
            state["messages"] = existing_messages + [HumanMessage(content=message)]
            # Ensure supplier_id is set correctly
            if effective_supplier_id:
                state["supplier_id"] = effective_supplier_id
        else:
            state = create_initial_state(conversation_id, conversation_type, effective_supplier_id)
            state["messages"] = existing_messages + [HumanMessage(content=message)]
    except Exception:
        state = create_initial_state(conversation_id, conversation_type, effective_supplier_id)
        state["messages"] = existing_messages + [HumanMessage(content=message)]
    
    # Run the graph
    result = await agent_graph.ainvoke(state, config)
    
    # Save conversation to database
    await save_conversation(
        conversation_id=conversation_id,
        conversation_type=conversation_type,
        supplier_id=supplier_id,
        messages=result.get("messages", []),
        context=result.get("context", {})
    )
    
    # Log agent activity
    await log_activity(
        agent_name=result.get("current_agent", "unknown"),
        action="message_processed",
        details=f"Processed message in conversation {conversation_id}",
        conversation_id=conversation_id
    )
    
    return {
        "response": result.get("final_response", "I apologize, but I couldn't process your request."),
        "conversation_id": conversation_id,
        "context": result.get("context", {}),
        "current_agent": result.get("current_agent")
    }


async def save_conversation(
    conversation_id: str,
    conversation_type: str,
    supplier_id: str | None,
    messages: list,
    context: dict
):
    """Save or update conversation in database, preserving existing messages."""
    conversations_collection = database.get_collection("conversations")
    
    # First, get existing conversation to preserve existing messages
    existing_conv = await conversations_collection.find_one({"conversation_id": conversation_id})
    existing_messages = existing_conv.get("messages", []) if existing_conv else []
    
    # Convert new messages to serializable format
    serialized_new_messages = []
    for msg in messages:
        if hasattr(msg, 'type') and hasattr(msg, 'content'):
            serialized_new_messages.append({
                "role": "user" if msg.type == "human" else "assistant",
                "content": msg.content,
                "timestamp": datetime.utcnow()
            })
    
    # Merge messages: keep existing + add truly new messages
    # A message is "new" if its content doesn't already exist in the conversation
    existing_contents = {m.get("content", "") for m in existing_messages}
    final_messages = list(existing_messages)  # Start with existing
    
    for new_msg in serialized_new_messages:
        if new_msg["content"] not in existing_contents:
            final_messages.append(new_msg)
            existing_contents.add(new_msg["content"])
    
    await conversations_collection.update_one(
        {"conversation_id": conversation_id},
        {
            "$set": {
                "conversation_id": conversation_id,
                "type": conversation_type,
                "supplier_id": supplier_id,
                "messages": final_messages,
                "context": context,
                "is_active": True,
                "updated_at": datetime.utcnow()
            },
            "$setOnInsert": {
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )


async def log_activity(
    agent_name: str,
    action: str,
    details: str,
    conversation_id: str | None = None,
    order_id: str | None = None
):
    """Log agent activity."""
    activities_collection = database.get_collection("agent_activities")
    
    activity = {
        "agent_name": agent_name,
        "action": action,
        "details": details,
        "conversation_id": conversation_id,
        "order_id": order_id,
        "timestamp": datetime.utcnow(),
        "success": True
    }
    
    await activities_collection.insert_one(activity)


async def get_conversation_history(conversation_id: str) -> dict | None:
    """Get conversation history by ID."""
    conversations_collection = database.get_collection("conversations")
    
    conversation = await conversations_collection.find_one({
        "conversation_id": conversation_id
    })
    
    if conversation:
        conversation["_id"] = str(conversation["_id"])
    
    return conversation
