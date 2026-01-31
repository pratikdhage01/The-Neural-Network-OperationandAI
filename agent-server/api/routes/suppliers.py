"""
Suppliers API routes - Supplier management endpoints.
"""

from fastapi import APIRouter, HTTPException
from database.connection import database
from database.models import SupplierCreate, SupplierResponseRequest, SupplierQueryStatus, OrderStatus
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])


@router.get("")
async def list_suppliers(active_only: bool = True):
    """List all suppliers."""
    suppliers_collection = database.get_collection("suppliers")
    
    query = {}
    if active_only:
        query["is_active"] = True
    
    suppliers = await suppliers_collection.find(query).sort("name", 1).to_list(100)
    
    # Convert ObjectId to string
    for supplier in suppliers:
        supplier["_id"] = str(supplier["_id"])
    
    return suppliers


@router.get("/pending-queries")
async def get_all_pending_queries():
    """Get all pending supplier queries across all suppliers."""
    queries_collection = database.get_collection("supplier_queries")
    
    queries = await queries_collection.find({
        "status": SupplierQueryStatus.PENDING.value
    }).sort("created_at", -1).to_list(100)
    
    for q in queries:
        q["_id"] = str(q["_id"])
    
    return queries


@router.get("/{supplier_id}")
async def get_supplier(supplier_id: str):
    """Get supplier details."""
    suppliers_collection = database.get_collection("suppliers")
    
    try:
        supplier = await suppliers_collection.find_one({"_id": ObjectId(supplier_id)})
    except Exception:
        supplier = None
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    supplier["_id"] = str(supplier["_id"])
    return supplier


@router.post("")
async def add_supplier(supplier: SupplierCreate):
    """Add a new supplier."""
    suppliers_collection = database.get_collection("suppliers")
    
    supplier_doc = supplier.model_dump()
    supplier_doc["created_at"] = datetime.utcnow()
    supplier_doc["is_active"] = True
    supplier_doc["avg_response_time_hours"] = 24.0
    supplier_doc["reliability_score"] = 0.8
    
    # Convert category enums to values
    supplier_doc["categories"] = [c.value for c in supplier.categories]
    
    result = await suppliers_collection.insert_one(supplier_doc)
    
    return {"id": str(result.inserted_id), "message": "Supplier added successfully"}


@router.put("/{supplier_id}")
async def update_supplier(supplier_id: str, updates: dict):
    """Update supplier details."""
    suppliers_collection = database.get_collection("suppliers")
    
    try:
        result = await suppliers_collection.update_one(
            {"_id": ObjectId(supplier_id)},
            {"$set": updates}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid supplier ID")
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    return {"message": "Supplier updated successfully"}


@router.delete("/{supplier_id}")
async def delete_supplier(supplier_id: str, soft_delete: bool = True):
    """Delete or deactivate a supplier."""
    suppliers_collection = database.get_collection("suppliers")
    
    try:
        if soft_delete:
            result = await suppliers_collection.update_one(
                {"_id": ObjectId(supplier_id)},
                {"$set": {"is_active": False}}
            )
        else:
            result = await suppliers_collection.delete_one({"_id": ObjectId(supplier_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid supplier ID")
    
    if (soft_delete and result.modified_count == 0) or (not soft_delete and result.deleted_count == 0):
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    return {"message": "Supplier removed successfully"}


@router.get("/{supplier_id}/chat")
async def get_supplier_chat_history(supplier_id: str, limit: int = 50):
    """Get chat history with a supplier."""
    conversations_collection = database.get_collection("conversations")
    
    conversations = await conversations_collection.find({
        "type": "supplier",
        "supplier_id": supplier_id
    }).sort("updated_at", -1).limit(limit).to_list(limit)
    
    for conv in conversations:
        conv["_id"] = str(conv["_id"])
        # Add conversation_id for frontend compatibility
        conv["conversation_id"] = conv.get("conversation_id", conv["_id"])
    
    return conversations


@router.get("/{supplier_id}/queries")
async def get_supplier_queries(supplier_id: str, status: str = None):
    """Get product queries for a supplier."""
    queries_collection = database.get_collection("supplier_queries")
    
    query = {"supplier_id": supplier_id}
    if status:
        query["status"] = status
    
    queries = await queries_collection.find(query).sort("created_at", -1).to_list(100)
    
    for q in queries:
        q["_id"] = str(q["_id"])
    
    return queries


@router.put("/{supplier_id}/queries/{query_id}/respond")
async def respond_to_query(supplier_id: str, query_id: str, response: str, available: bool):
    """Submit response to a supplier query (simulates supplier responding)."""
    queries_collection = database.get_collection("supplier_queries")
    
    status = "available" if available else "unavailable"
    
    try:
        result = await queries_collection.update_one(
            {"_id": ObjectId(query_id), "supplier_id": supplier_id},
            {
                "$set": {
                    "status": status,
                    "response": response,
                    "responded_at": datetime.utcnow()
                }
            }
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid query ID")
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return {"message": "Response submitted successfully"}


@router.post("/{supplier_id}/respond")
async def supplier_respond_to_stock_query(supplier_id: str, response: SupplierResponseRequest):
    """
    Supplier responds to a stock availability query.
    If available, updates inventory and order status.
    """
    queries_collection = database.get_collection("supplier_queries")
    products_collection = database.get_collection("products")
    orders_collection = database.get_collection("orders")
    activities_collection = database.get_collection("agent_activities")
    
    # Find the query
    query = await queries_collection.find_one({
        "query_id": response.query_id,
        "supplier_id": supplier_id
    })
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found or doesn't belong to this supplier")
    
    if query.get("status") != SupplierQueryStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="Query has already been responded to")
    
    # Update query status
    new_status = SupplierQueryStatus.RESPONDED_AVAILABLE.value if response.available else SupplierQueryStatus.RESPONDED_UNAVAILABLE.value
    
    await queries_collection.update_one(
        {"query_id": response.query_id},
        {
            "$set": {
                "status": new_status,
                "response_quantity": response.quantity_available,
                "response_message": response.message,
                "responded_at": datetime.utcnow()
            }
        }
    )
    
    result_message = ""
    
    if response.available and response.quantity_available:
        quantity_to_add = response.quantity_available
        product_id = query.get("product_id")
        
        # Update inventory
        await products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"quantity": quantity_to_add}}
        )
        
        # Check if all pending queries for this order are resolved
        order_id = query.get("order_id")
        pending_queries = await queries_collection.count_documents({
            "order_id": order_id,
            "status": SupplierQueryStatus.PENDING.value
        })
        
        # If no more pending queries, check if we have enough stock now
        order = await orders_collection.find_one({"_id": ObjectId(order_id)})
        
        if order and pending_queries == 0:
            # Update order status to pending (ready to process)
            await orders_collection.update_one(
                {"_id": ObjectId(order_id)},
                {
                    "$set": {
                        "status": OrderStatus.PENDING.value,
                        "awaiting_supplier": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Log activity
            await activities_collection.insert_one({
                "agent_name": "order_agent",
                "action": "stock_fulfilled_by_supplier",
                "details": f"Order {query.get('order_number')} stock fulfilled by {query.get('supplier_name')}",
                "order_id": order_id,
                "conversation_id": query.get("conversation_id"),
                "timestamp": datetime.utcnow(),
                "success": True
            })
            
            result_message = f"Inventory updated with {quantity_to_add} units. Order {query.get('order_number')} is now ready for processing!"
        else:
            result_message = f"Inventory updated with {quantity_to_add} units. Waiting for {pending_queries} more supplier responses."
        
        print(f"✅ Supplier Response: {query.get('supplier_name')} provided {quantity_to_add} units of {query.get('product_name')}")
    else:
        # Supplier doesn't have stock
        # Check if all suppliers have responded with unavailable
        order_id = query.get("order_id")
        pending_queries = await queries_collection.count_documents({
            "order_id": order_id,
            "status": SupplierQueryStatus.PENDING.value
        })
        
        available_responses = await queries_collection.count_documents({
            "order_id": order_id,
            "status": SupplierQueryStatus.RESPONDED_AVAILABLE.value
        })
        
        if pending_queries == 0 and available_responses == 0:
            # All suppliers responded, none available
            # Log activity
            await activities_collection.insert_one({
                "agent_name": "order_agent",
                "action": "stock_unavailable_all_suppliers",
                "details": f"Order {query.get('order_number')} - No suppliers have the required stock. Order delayed by 7 days.",
                "order_id": order_id,
                "conversation_id": query.get("conversation_id"),
                "timestamp": datetime.utcnow(),
                "success": False
            })
            
            result_message = f"No stock available. Customer will be notified of 7-day delay for order {query.get('order_number')}."
        else:
            result_message = f"Response recorded. Waiting for {pending_queries} more supplier responses."
        
        print(f"❌ Supplier Response: {query.get('supplier_name')} has no stock of {query.get('product_name')}")
    
    return {
        "message": "Response recorded successfully",
        "result": result_message,
        "query_id": response.query_id,
        "order_number": query.get("order_number")
    }
