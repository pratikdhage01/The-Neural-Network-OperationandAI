"""
LangGraph state definitions for agent orchestration.
"""

from typing import Annotated, TypedDict, Optional, Literal
from langgraph.graph import add_messages


class AgentState(TypedDict):
    """
    State for the agent graph.
    This is passed between all nodes in the graph.
    """
    # Conversation messages - uses add_messages reducer to append
    messages: Annotated[list, add_messages]
    
    # Current conversation ID
    conversation_id: str
    
    # Type of conversation
    conversation_type: Literal["consumer", "supplier"]
    
    # For supplier conversations
    supplier_id: Optional[str]
    
    # Current routing decision
    current_agent: Optional[str]
    
    # Context data collected during conversation
    context: dict
    
    # Order being processed (if any)
    current_order: Optional[dict]
    
    # Products found during search
    found_products: list
    
    # Supplier queries pending
    pending_supplier_queries: list
    
    # Whether we're waiting for supplier response
    awaiting_supplier_response: bool
    
    # Final response to user
    final_response: Optional[str]
    
    # Whether conversation should end
    should_end: bool


class SupplierQueryState(TypedDict):
    """State for supplier query sub-graph."""
    product_name: str
    quantity_needed: int
    suppliers_queried: list[str]
    responses_received: dict
    best_offer: Optional[dict]


def create_initial_state(
    conversation_id: str,
    conversation_type: Literal["consumer", "supplier"] = "consumer",
    supplier_id: Optional[str] = None
) -> AgentState:
    """Create initial state for a new conversation."""
    return AgentState(
        messages=[],
        conversation_id=conversation_id,
        conversation_type=conversation_type,
        supplier_id=supplier_id,
        current_agent=None,
        context={},
        current_order=None,
        found_products=[],
        pending_supplier_queries=[],
        awaiting_supplier_response=False,
        final_response=None,
        should_end=False
    )
