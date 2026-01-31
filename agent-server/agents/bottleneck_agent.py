"""
Bottleneck Analysis Agent - Identifies and reports operational bottlenecks.
"""

from langchain_core.messages import AIMessage
from agents.state import AgentState
from database.connection import database
from database.models import BottleneckType, BottleneckSeverity, OrderStatus
from datetime import datetime, timedelta


async def bottleneck_agent(state: AgentState) -> AgentState:
    """
    Analyze operations and identify bottlenecks.
    """
    context = state.get("context", {})
    action = context.get("bottleneck_action", "analyze")
    
    if action == "resolve":
        result = await resolve_bottleneck(context.get("bottleneck_id"))
    else:
        result = await comprehensive_analysis()
    
    state["final_response"] = result
    state["messages"] = state.get("messages", []) + [AIMessage(content=result)]
    
    return state


async def comprehensive_analysis() -> str:
    """Perform comprehensive bottleneck analysis."""
    bottlenecks = []
    
    # Check order backlog
    order_bottleneck = await check_order_backlog()
    if order_bottleneck:
        bottlenecks.append(order_bottleneck)
    
    # Check inventory issues
    inventory_bottleneck = await check_inventory_issues()
    if inventory_bottleneck:
        bottlenecks.append(inventory_bottleneck)
    
    # Check workload issues
    workload_bottleneck = await check_workload_issues()
    if workload_bottleneck:
        bottlenecks.append(workload_bottleneck)
    
    # Check supplier delays
    supplier_bottleneck = await check_supplier_delays()
    if supplier_bottleneck:
        bottlenecks.append(supplier_bottleneck)
    
    if not bottlenecks:
        return "✅ No operational bottlenecks detected. Operations running smoothly."
    
    # Save new bottlenecks
    bottlenecks_collection = database.get_collection("bottlenecks")
    
    for bn in bottlenecks:
        # Check if similar bottleneck already exists
        existing = await bottlenecks_collection.find_one({
            "type": bn["type"],
            "is_resolved": False
        })
        
        if not existing:
            bn["detected_at"] = datetime.utcnow()
            bn["is_resolved"] = False
            await bottlenecks_collection.insert_one(bn)
    
    # Format response
    lines = ["⚠️ Operational Bottlenecks Detected:", ""]
    
    for i, bn in enumerate(bottlenecks, 1):
        severity_icon = {
            "low": "🟢",
            "medium": "🟡", 
            "high": "🟠",
            "critical": "🔴"
        }.get(bn.get("severity"), "⚪")
        
        lines.append(f"{i}. {severity_icon} {bn.get('title')}")
        lines.append(f"   {bn.get('description')}")
        lines.append(f"   Suggested: {bn.get('suggested_actions', ['No suggestions'])[0]}")
        lines.append("")
    
    return "\n".join(lines)


async def check_order_backlog() -> dict | None:
    """Check for order backlog."""
    orders_collection = database.get_collection("orders")
    
    # Count pending orders older than 24 hours
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    old_pending = await orders_collection.count_documents({
        "status": {"$in": [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]},
        "created_at": {"$lt": cutoff}
    })
    
    # Count all pending orders
    total_pending = await orders_collection.count_documents({
        "status": {"$in": [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]}
    })
    
    if old_pending > 5 or total_pending > 20:
        severity = BottleneckSeverity.CRITICAL if old_pending > 10 else BottleneckSeverity.HIGH
        
        return {
            "type": BottleneckType.ORDER_BACKLOG.value,
            "severity": severity.value,
            "title": "Order Backlog Building Up",
            "description": f"{total_pending} pending orders, {old_pending} are older than 24 hours",
            "affected_resources": [f"{total_pending} orders"],
            "suggested_actions": [
                "Prioritize processing oldest orders first",
                "Assign additional staff to order processing",
                "Consider overtime or temporary help"
            ]
        }
    
    return None


async def check_inventory_issues() -> dict | None:
    """Check for inventory issues."""
    products_collection = database.get_collection("products")
    
    # Count out of stock items
    out_of_stock = await products_collection.count_documents({"quantity": 0})
    
    # Count low stock items
    low_stock = await products_collection.count_documents({
        "$expr": {"$lte": ["$quantity", "$low_stock_threshold"]},
        "quantity": {"$gt": 0}
    })
    
    if out_of_stock > 0 or low_stock > 5:
        severity = BottleneckSeverity.HIGH if out_of_stock > 3 else BottleneckSeverity.MEDIUM
        
        return {
            "type": BottleneckType.INVENTORY_SHORTAGE.value,
            "severity": severity.value,
            "title": "Inventory Running Low",
            "description": f"{out_of_stock} products out of stock, {low_stock} at low stock levels",
            "affected_resources": [f"{out_of_stock + low_stock} products"],
            "suggested_actions": [
                "Contact suppliers for restocking",
                "Review sales forecasts",
                "Consider expedited shipping for critical items"
            ]
        }
    
    return None


async def check_workload_issues() -> dict | None:
    """Check for workload issues."""
    staff_collection = database.get_collection("staff")
    
    staff_members = await staff_collection.find().to_list(100)
    
    if not staff_members:
        return None
    
    total_capacity = sum(s.get("max_workload", 10) for s in staff_members)
    total_current = sum(s.get("current_workload", 0) for s in staff_members)
    
    utilization = (total_current / total_capacity * 100) if total_capacity > 0 else 0
    
    # Check for staff at max capacity
    at_max = sum(1 for s in staff_members 
                 if s.get("current_workload", 0) >= s.get("max_workload", 10))
    
    if utilization > 85 or at_max > len(staff_members) // 2:
        severity = BottleneckSeverity.HIGH if utilization > 95 else BottleneckSeverity.MEDIUM
        
        overloaded_names = [s.get("name") for s in staff_members 
                           if s.get("current_workload", 0) >= s.get("max_workload", 10)]
        
        return {
            "type": BottleneckType.WORKLOAD_IMBALANCE.value,
            "severity": severity.value,
            "title": "Staff Capacity Stretched",
            "description": f"Team at {utilization:.0f}% capacity. {at_max} staff at maximum workload.",
            "affected_resources": overloaded_names or ["Team"],
            "suggested_actions": [
                "Rebalance tasks across team",
                "Postpone non-urgent tasks",
                "Consider temporary assistance"
            ]
        }
    
    return None


async def check_supplier_delays() -> dict | None:
    """Check for supplier response delays."""
    queries_collection = database.get_collection("supplier_queries")
    
    # Check for queries pending > 24 hours
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    old_queries = await queries_collection.count_documents({
        "status": "pending",
        "created_at": {"$lt": cutoff}
    })
    
    if old_queries > 0:
        return {
            "type": BottleneckType.SUPPLIER_DELAY.value,
            "severity": BottleneckSeverity.HIGH.value,
            "title": "Supplier Response Delays",
            "description": f"{old_queries} supplier queries awaiting response for over 24 hours",
            "affected_resources": [f"{old_queries} pending queries"],
            "suggested_actions": [
                "Follow up with suppliers",
                "Consider alternative suppliers",
                "Update affected customer orders"
            ]
        }
    
    return None


async def resolve_bottleneck(bottleneck_id: str) -> str:
    """Mark a bottleneck as resolved."""
    if not bottleneck_id:
        return "No bottleneck ID provided."
    
    bottlenecks_collection = database.get_collection("bottlenecks")
    
    from bson import ObjectId
    
    result = await bottlenecks_collection.update_one(
        {"_id": ObjectId(bottleneck_id)},
        {
            "$set": {
                "is_resolved": True,
                "resolved_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count > 0:
        return f"Bottleneck {bottleneck_id} marked as resolved."
    return f"Bottleneck {bottleneck_id} not found."


async def get_active_bottlenecks() -> list:
    """Get all active bottlenecks."""
    bottlenecks_collection = database.get_collection("bottlenecks")
    
    bottlenecks = await bottlenecks_collection.find({
        "is_resolved": False
    }).sort("detected_at", -1).to_list(50)
    
    # Convert ObjectId to string
    for bn in bottlenecks:
        bn["_id"] = str(bn["_id"])
    
    return bottlenecks


async def get_bottleneck_stats() -> dict:
    """Get bottleneck statistics."""
    bottlenecks_collection = database.get_collection("bottlenecks")
    
    total = await bottlenecks_collection.count_documents({})
    active = await bottlenecks_collection.count_documents({"is_resolved": False})
    resolved = await bottlenecks_collection.count_documents({"is_resolved": True})
    
    # Count by severity
    critical = await bottlenecks_collection.count_documents({
        "is_resolved": False,
        "severity": BottleneckSeverity.CRITICAL.value
    })
    high = await bottlenecks_collection.count_documents({
        "is_resolved": False,
        "severity": BottleneckSeverity.HIGH.value
    })
    
    return {
        "total": total,
        "active": active,
        "resolved": resolved,
        "critical": critical,
        "high": high
    }
