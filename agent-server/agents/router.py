"""
Router Agent - Routes incoming messages to appropriate specialized agents.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agents.state import AgentState
from config import settings


def get_llm():
    """Get configured LLM instance."""
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3
    )


ROUTER_SYSTEM_PROMPT = """You are an intelligent router for an MSME (Micro, Small, and Medium Enterprise) that sells jewelry, kitchen appliances, and makeup products.

Your job is to analyze the user's message and determine which specialized agent should handle it.

Available agents:
1. CUSTOMER_AGENT - For product inquiries, browsing products, checking availability, getting product information
2. ORDER_AGENT - For placing orders, confirming orders, providing delivery details, tracking orders
3. INVENTORY_AGENT - For checking stock levels, inventory queries (internal use)
4. SUPPLIER_AGENT - For supplier communication, procurement (internal use)
5. WORKLOAD_AGENT - For task assignment and staff management (internal use)
6. BOTTLENECK_AGENT - For operational analysis (internal use)

Analyze the user message and respond with ONLY the agent name (e.g., "CUSTOMER_AGENT" or "ORDER_AGENT").

Consider the conversation context:
- If user is asking about products, prices, or availability -> CUSTOMER_AGENT
- If user wants to buy/order something or needs to provide delivery details -> ORDER_AGENT
- If user is asking about order status -> ORDER_AGENT

Respond with just the agent name, nothing else."""


async def route_message(state: AgentState) -> AgentState:
    """
    Route incoming message to appropriate agent.
    """
    llm = get_llm()
    
    # Get the last user message
    messages = state.get("messages", [])
    if not messages:
        state["current_agent"] = "CUSTOMER_AGENT"
        return state
    
    last_message = messages[-1]
    
    # Build context from conversation history
    context_messages = [SystemMessage(content=ROUTER_SYSTEM_PROMPT)]
    
    # Add recent conversation history for context
    for msg in messages[-5:]:
        if hasattr(msg, 'type'):
            if msg.type == "human":
                context_messages.append(HumanMessage(content=msg.content))
            elif msg.type == "ai":
                context_messages.append(AIMessage(content=msg.content))
    
    # Ask LLM to route
    response = await llm.ainvoke(context_messages)
    
    # Parse the agent name from response
    agent_name = response.content.strip().upper()
    
    # Validate agent name
    valid_agents = [
        "CUSTOMER_AGENT", "ORDER_AGENT", "INVENTORY_AGENT",
        "SUPPLIER_AGENT", "WORKLOAD_AGENT", "BOTTLENECK_AGENT"
    ]
    
    if agent_name not in valid_agents:
        # Default to customer agent for user-facing conversations
        agent_name = "CUSTOMER_AGENT"
    
    state["current_agent"] = agent_name
    return state


def get_next_agent(state: AgentState) -> str:
    """
    Determine which agent node to route to based on state.
    Used as conditional edge in the graph.
    """
    current_agent = state.get("current_agent")
    
    if current_agent == "CUSTOMER_AGENT":
        return "customer_agent"
    elif current_agent == "ORDER_AGENT":
        return "order_agent"
    elif current_agent == "INVENTORY_AGENT":
        return "inventory_agent"
    elif current_agent == "SUPPLIER_AGENT":
        return "supplier_agent"
    elif current_agent == "WORKLOAD_AGENT":
        return "workload_agent"
    elif current_agent == "BOTTLENECK_AGENT":
        return "bottleneck_agent"
    else:
        return "customer_agent"
