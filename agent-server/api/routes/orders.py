"""
Orders API routes - Order management endpoints.
"""

from fastapi import APIRouter, HTTPException
from database.connection import database
from database.models import OrderStatus
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.get("")
async def list_orders(
    status: str = None,
    limit: int = 50,
    skip: int = 0
):
    """List all orders with optional status filter."""
    orders_collection = database.get_collection("orders")
    
    query = {}
    if status:
        query["status"] = status
    
    orders = await orders_collection.find(query).sort(
        "created_at", -1
    ).skip(skip).limit(limit).to_list(limit)
    
    # Convert ObjectId to string
    for order in orders:
        order["_id"] = str(order["_id"])
    
    return orders


@router.get("/stats")
async def get_order_stats():
    """Get order statistics."""
    orders_collection = database.get_collection("orders")
    
    # Count by status
    total = await orders_collection.count_documents({})
    pending = await orders_collection.count_documents({"status": OrderStatus.PENDING.value})
    confirmed = await orders_collection.count_documents({"status": OrderStatus.CONFIRMED.value})
    processing = await orders_collection.count_documents({"status": OrderStatus.PROCESSING.value})
    shipped = await orders_collection.count_documents({"status": OrderStatus.SHIPPED.value})
    delivered = await orders_collection.count_documents({"status": OrderStatus.DELIVERED.value})
    cancelled = await orders_collection.count_documents({"status": OrderStatus.CANCELLED.value})
    
    # Orders today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    orders_today = await orders_collection.count_documents({
        "created_at": {"$gte": today_start}
    })
    
    # Revenue today
    pipeline = [
        {"$match": {"created_at": {"$gte": today_start}, "status": {"$ne": OrderStatus.CANCELLED.value}}},
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]
    revenue_result = await orders_collection.aggregate(pipeline).to_list(1)
    revenue_today = revenue_result[0]["total"] if revenue_result else 0
    
    return {
        "total": total,
        "by_status": {
            "pending": pending,
            "confirmed": confirmed,
            "processing": processing,
            "shipped": shipped,
            "delivered": delivered,
            "cancelled": cancelled
        },
        "orders_today": orders_today,
        "revenue_today": revenue_today
    }


@router.get("/{order_id}")
async def get_order(order_id: str):
    """Get order details by ID."""
    orders_collection = database.get_collection("orders")
    
    try:
        order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    except Exception:
        # Try by order number
        order = await orders_collection.find_one({"order_number": order_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order["_id"] = str(order["_id"])
    return order


@router.put("/{order_id}/status")
async def update_order_status(order_id: str, status: str):
    """Update order status."""
    orders_collection = database.get_collection("orders")
    
    # Validate status
    try:
        new_status = OrderStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    try:
        result = await orders_collection.update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "status": new_status.value,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    except Exception:
        # Try by order number
        result = await orders_collection.update_one(
            {"order_number": order_id},
            {
                "$set": {
                    "status": new_status.value,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # If order is being processed, assign to staff
    if new_status == OrderStatus.PROCESSING:
        from agents.workload_agent import assign_task_to_staff
        from agents.state import create_initial_state
        
        state = create_initial_state("internal")
        state["context"] = {
            "workload_action": "assign",
            "task_description": f"Process order {order_id}",
            "order_id": order_id,
            "priority": 2
        }
        await assign_task_to_staff(state)
    
    return {"message": f"Order status updated to {new_status.value}"}


@router.get("/tracking/{order_number}")
async def track_order(order_number: str):
    """Track order by order number (for customers)."""
    orders_collection = database.get_collection("orders")
    
    order = await orders_collection.find_one({"order_number": order_number})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Return limited info for customer
    return {
        "order_number": order["order_number"],
        "status": order["status"],
        "total_amount": order["total_amount"],
        "estimated_delivery": order.get("estimated_delivery"),
        "created_at": order["created_at"]
    }
