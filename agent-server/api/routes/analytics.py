"""
Analytics API routes - Dashboard metrics and bottleneck analysis.
"""

from fastapi import APIRouter
from database.connection import database
from database.models import DashboardStats, OrderStatus
from agents.bottleneck_agent import get_active_bottlenecks, get_bottleneck_stats, comprehensive_analysis
from agents.workload_agent import get_workload_distribution
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview", response_model=DashboardStats)
async def get_dashboard_overview():
    """Get dashboard overview statistics."""
    orders_collection = database.get_collection("orders")
    products_collection = database.get_collection("products")
    bottlenecks_collection = database.get_collection("bottlenecks")
    staff_collection = database.get_collection("staff")
    
    # Order stats
    total_orders = await orders_collection.count_documents({})
    pending_orders = await orders_collection.count_documents({
        "status": {"$in": [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]}
    })
    processing_orders = await orders_collection.count_documents({
        "status": OrderStatus.PROCESSING.value
    })
    
    # Orders today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    orders_today = await orders_collection.count_documents({
        "created_at": {"$gte": today_start}
    })
    
    # Product stats
    total_products = await products_collection.count_documents({})
    low_stock_count = await products_collection.count_documents({
        "$expr": {"$lte": ["$quantity", "$low_stock_threshold"]}
    })
    
    # Bottleneck stats
    active_bottlenecks = await bottlenecks_collection.count_documents({
        "is_resolved": False
    })
    
    # Staff utilization
    staff_members = await staff_collection.find().to_list(100)
    if staff_members:
        total_capacity = sum(s.get("max_workload", 10) for s in staff_members)
        total_current = sum(s.get("current_workload", 0) for s in staff_members)
        staff_utilization = (total_current / total_capacity * 100) if total_capacity > 0 else 0
    else:
        staff_utilization = 0
    
    return DashboardStats(
        total_orders=total_orders,
        pending_orders=pending_orders,
        processing_orders=processing_orders,
        total_products=total_products,
        low_stock_count=low_stock_count,
        active_bottlenecks=active_bottlenecks,
        staff_utilization=round(staff_utilization, 1),
        orders_today=orders_today
    )


@router.get("/bottlenecks")
async def get_bottlenecks():
    """Get all active bottlenecks."""
    bottlenecks = await get_active_bottlenecks()
    return bottlenecks


@router.get("/bottlenecks/analyze")
async def analyze_bottlenecks():
    """Run comprehensive bottleneck analysis."""
    result = await comprehensive_analysis()
    bottlenecks = await get_active_bottlenecks()
    
    return {
        "analysis": result,
        "bottlenecks": bottlenecks
    }


@router.get("/bottlenecks/stats")
async def bottleneck_statistics():
    """Get bottleneck statistics."""
    stats = await get_bottleneck_stats()
    return stats


@router.put("/bottlenecks/{bottleneck_id}/resolve")
async def resolve_bottleneck(bottleneck_id: str):
    """Mark a bottleneck as resolved."""
    bottlenecks_collection = database.get_collection("bottlenecks")
    
    try:
        result = await bottlenecks_collection.update_one(
            {"_id": ObjectId(bottleneck_id)},
            {
                "$set": {
                    "is_resolved": True,
                    "resolved_at": datetime.utcnow()
                }
            }
        )
    except Exception:
        return {"error": "Invalid bottleneck ID"}
    
    if result.modified_count == 0:
        return {"error": "Bottleneck not found"}
    
    return {"message": "Bottleneck resolved"}


@router.get("/workload")
async def get_workload_analytics():
    """Get workload distribution analytics."""
    distribution = await get_workload_distribution()
    
    # Calculate summary stats
    if distribution:
        avg_utilization = sum(d["utilization_percent"] for d in distribution) / len(distribution)
        max_utilization = max(d["utilization_percent"] for d in distribution)
        min_utilization = min(d["utilization_percent"] for d in distribution)
    else:
        avg_utilization = max_utilization = min_utilization = 0
    
    return {
        "distribution": distribution,
        "summary": {
            "average_utilization": round(avg_utilization, 1),
            "max_utilization": max_utilization,
            "min_utilization": min_utilization,
            "total_staff": len(distribution)
        }
    }


@router.get("/agent-activity")
async def get_agent_activity(limit: int = 50):
    """Get recent agent activity."""
    activities_collection = database.get_collection("agent_activities")
    
    activities = await activities_collection.find().sort(
        "timestamp", -1
    ).limit(limit).to_list(limit)
    
    for activity in activities:
        activity["_id"] = str(activity["_id"])
    
    return activities


@router.get("/orders/trends")
async def get_order_trends(days: int = 7):
    """Get order trends over time."""
    orders_collection = database.get_collection("orders")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {"created_at": {"$gte": start_date}}},
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                },
                "count": {"$sum": 1},
                "revenue": {"$sum": "$total_amount"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    trends = await orders_collection.aggregate(pipeline).to_list(days)
    
    return [{"date": t["_id"], "orders": t["count"], "revenue": t["revenue"]} for t in trends]


@router.get("/inventory/alerts")
async def get_inventory_alerts():
    """Get inventory alerts (low stock, out of stock)."""
    products_collection = database.get_collection("products")
    
    # Out of stock
    out_of_stock = await products_collection.find({
        "quantity": 0
    }).to_list(50)
    
    # Low stock
    low_stock = await products_collection.find({
        "$expr": {"$lte": ["$quantity", "$low_stock_threshold"]},
        "quantity": {"$gt": 0}
    }).to_list(50)
    
    for p in out_of_stock + low_stock:
        p["_id"] = str(p["_id"])
    
    return {
        "out_of_stock": out_of_stock,
        "low_stock": low_stock
    }
