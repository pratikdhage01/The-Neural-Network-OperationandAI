"""
Chat API routes - Consumer and Supplier chat endpoints.
"""

from fastapi import APIRouter, HTTPException
from database.models import ChatRequest, ChatResponse, SupplierChatRequest
from agents.graph import run_agent, get_conversation_history
import traceback

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/consumer", response_model=ChatResponse)
async def consumer_chat(request: ChatRequest):
    """
    Consumer chat endpoint - main entry point for customer interactions.
    
    The agent will handle:
    - Product inquiries
    - Availability checks
    - Order placement
    - Order tracking
    """
    try:
        result = await run_agent(
            message=request.message,
            conversation_id=request.conversation_id,
            conversation_type="consumer"
        )
        
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            context=result.get("context", {})
        )
    except Exception as e:
        print(f"CHAT ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.post("/supplier/{supplier_id}", response_model=ChatResponse)
async def supplier_chat(supplier_id: str, request: SupplierChatRequest):
    """
    Supplier chat endpoint - for communication with specific suppliers.
    
    Each supplier has their own chat endpoint.
    """
    try:
        result = await run_agent(
            message=request.message,
            conversation_id=request.conversation_id,
            conversation_type="supplier",
            supplier_id=supplier_id
        )
        
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            context=result.get("context", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """Get conversation history by ID."""
    conversation = await get_conversation_history(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.get("/conversations")
async def list_conversations(limit: int = 20, conversation_type: str = None):
    """List recent conversations."""
    from database.connection import database
    
    conversations_collection = database.get_collection("conversations")
    
    query = {}
    if conversation_type:
        query["type"] = conversation_type
    
    conversations = await conversations_collection.find(query).sort(
        "updated_at", -1
    ).limit(limit).to_list(limit)
    
    # Convert ObjectId to string
    for conv in conversations:
        conv["_id"] = str(conv["_id"])
    
    return conversations
