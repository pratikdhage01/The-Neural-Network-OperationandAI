"""
Inventory Agent - Manages stock levels and inventory operations.
"""

from langchain_core.messages import AIMessage
from agents.state import AgentState
from database.connection import database
from database.models import BottleneckType, BottleneckSeverity
from datetime import datetime


async def inventory_agent(state: AgentState) -> AgentState:
    """
    Handle inventory-related operations.
    """
    # This agent primarily works with other agents internally
    # It checks stock and triggers supplier queries when needed
    
    context = state.get("context", {})
    action = context.get("inventory_action", "check")
    
    if action == "check":
        result = await check_stock_for_order(state)
    elif action == "reserve":
        result = await reserve_stock(state)
    elif action == "update":
        result = await update_stock_level(state)
    else:
        result = "Inventory check completed."
    
    state["final_response"] = result
    state["messages"] = state.get("messages", []) + [AIMessage(content=result)]
    
    return state


async def check_stock_for_order(state: AgentState) -> str:
    """Check if we have enough stock for an order."""
    current_order = state.get("current_order")
    if not current_order:
        return "No order to check stock for."
    
    products_collection = database.get_collection("products")
    insufficient_stock = []
    
    items = current_order.get("items", [])
    for item in items:
        product = await products_collection.find_one({"_id": item["product_id"]})
        if not product:
            insufficient_stock.append({"product": item["product_name"], "issue": "not_found"})
        elif product.get("quantity", 0) < item["quantity"]:
            insufficient_stock.append({
                "product": item["product_name"],
                "issue": "insufficient",
                "available": product.get("quantity", 0),
                "needed": item["quantity"]
            })
    
    if insufficient_stock:
        # Trigger supplier queries
        state["pending_supplier_queries"] = insufficient_stock
        state["awaiting_supplier_response"] = True
        return f"Stock check: {len(insufficient_stock)} items need supplier inquiry."
    
    return "All items in stock."


async def reserve_stock(state: AgentState) -> str:
    """Reserve stock for a confirmed order."""
    current_order = state.get("current_order")
    if not current_order:
        return "No order to reserve stock for."
    
    products_collection = database.get_collection("products")
    
    for item in current_order.get("items", []):
        await products_collection.update_one(
            {"_id": item["product_id"]},
            {"$inc": {"quantity": -item["quantity"]}}
        )
    
    # Check for low stock and create bottleneck if needed
    await check_low_stock_bottlenecks()
    
    return "Stock reserved for order."


async def update_stock_level(state: AgentState) -> str:
    """Update stock level for a product."""
    context = state.get("context", {})
    product_id = context.get("product_id")
    quantity_change = context.get("quantity_change", 0)
    
    if not product_id:
        return "No product specified for stock update."
    
    products_collection = database.get_collection("products")
    await products_collection.update_one(
        {"_id": product_id},
        {"$inc": {"quantity": quantity_change}}
    )
    
    return f"Stock updated by {quantity_change}."


async def get_low_stock_items() -> list:
    """Get list of items below low stock threshold."""
    products_collection = database.get_collection("products")
    
    low_stock = await products_collection.find({
        "$expr": {"$lte": ["$quantity", "$low_stock_threshold"]}
    }).to_list(100)
    
    return low_stock


async def check_low_stock_bottlenecks():
    """Create bottleneck events for low stock items."""
    low_stock_items = await get_low_stock_items()
    
    if low_stock_items:
        bottlenecks_collection = database.get_collection("bottlenecks")
        
        for item in low_stock_items:
            # Check if bottleneck already exists for this product
            existing = await bottlenecks_collection.find_one({
                "type": BottleneckType.INVENTORY_SHORTAGE.value,
                "affected_resources": {"$in": [item.get("name")]},
                "is_resolved": False
            })
            
            if not existing:
                severity = BottleneckSeverity.HIGH if item.get("quantity", 0) == 0 else BottleneckSeverity.MEDIUM
                
                bottleneck = {
                    "type": BottleneckType.INVENTORY_SHORTAGE.value,
                    "severity": severity.value,
                    "title": f"Low Stock: {item.get('name')}",
                    "description": f"{item.get('name')} has only {item.get('quantity', 0)} units left (threshold: {item.get('low_stock_threshold', 5)})",
                    "affected_resources": [item.get("name")],
                    "suggested_actions": [
                        f"Contact supplier for {item.get('name')}",
                        "Review upcoming orders for this product",
                        "Consider expedited shipping"
                    ],
                    "is_resolved": False,
                    "detected_at": datetime.utcnow()
                }
                
                await bottlenecks_collection.insert_one(bottleneck)


async def get_product_availability(product_name: str) -> dict:
    """Check availability of a specific product."""
    products_collection = database.get_collection("products")
    
    product = await products_collection.find_one({
        "name": {"$regex": product_name, "$options": "i"}
    })
    
    if not product:
        return {"found": False, "message": f"Product '{product_name}' not found."}
    
    quantity = product.get("quantity", 0)
    if quantity > 5:
        status = "in_stock"
        message = f"{product.get('name')} is in stock ({quantity} available)."
    elif quantity > 0:
        status = "low_stock"
        message = f"{product.get('name')} is low in stock (only {quantity} left)."
    else:
        status = "out_of_stock"
        message = f"{product.get('name')} is currently out of stock."
    
    return {
        "found": True,
        "product": product,
        "quantity": quantity,
        "status": status,
        "message": message
    }
