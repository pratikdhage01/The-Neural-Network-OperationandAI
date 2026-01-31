"""
Order Management Agent - Handles order placement and tracking.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agents.state import AgentState
from agents.router import get_llm
from database.connection import database
from database.models import OrderStatus, SupplierQueryStatus
from datetime import datetime, timedelta
import uuid


ORDER_SYSTEM_PROMPT = """You are an order management agent for an MSME business selling jewelry, kitchen appliances, and makeup.

Your responsibilities:
1. Collect customer details for order placement (name, phone, address, city, pincode)
2. Confirm order details with the customer
3. Process order placement
4. Provide order tracking updates

When collecting information, be conversational and natural. Ask for one or two pieces of information at a time.

Required information for an order:
- Customer name
- Phone number
- Delivery address
- City
- Pincode

If the customer provides partial information, acknowledge what they've given and ask for the remaining details.

Current order context will be provided to you.

IMPORTANT: When all details are collected, confirm the order summary and ask for final confirmation."""


async def order_agent(state: AgentState) -> AgentState:
    """
    Handle order-related operations.
    """
    llm = get_llm()
    
    # Get current order context
    current_order = state.get("current_order") or {}
    context = state.get("context", {})
    
    # Build order context for LLM
    order_context = format_order_context(current_order, context)
    
    system_content = ORDER_SYSTEM_PROMPT + f"\n\nCurrent Order Context:\n{order_context}"
    messages = [SystemMessage(content=system_content)]
    
    # Add conversation history
    for msg in state.get("messages", []):
        if hasattr(msg, 'type'):
            if msg.type == "human":
                messages.append(HumanMessage(content=msg.content))
            elif msg.type == "ai":
                messages.append(AIMessage(content=msg.content))
    
    response = await llm.ainvoke(messages)
    
    # Parse and extract customer details from conversation
    updated_context = await extract_customer_details(state, response.content)
    state["context"] = {**context, **updated_context}
    
    # Check if order is ready to be placed
    if is_order_complete(state):
        # Check for order confirmation in user message
        last_message = state.get("messages", [])[-1] if state.get("messages") else None
        if last_message and is_confirmation(last_message.content if hasattr(last_message, 'content') else str(last_message)):
            order_result = await place_order(state)
            state["final_response"] = order_result
            state["messages"] = state.get("messages", []) + [AIMessage(content=order_result)]
            return state
    
    state["final_response"] = response.content
    state["messages"] = state.get("messages", []) + [AIMessage(content=response.content)]
    
    return state


def format_order_context(current_order: dict, context: dict) -> str:
    """Format order context for LLM."""
    lines = []
    
    # Items to order
    if current_order.get("items"):
        lines.append("Items to order:")
        for item in current_order["items"]:
            lines.append(f"  - {item.get('product_name')}: {item.get('quantity')} x ₹{item.get('unit_price', 0):,.2f}")
        total = sum(item.get('total_price', 0) for item in current_order["items"])
        lines.append(f"  Total: ₹{total:,.2f}")
    else:
        lines.append("No items selected yet.")
    
    # Customer details collected so far
    lines.append("\nCustomer details collected:")
    customer = context.get("customer", {})
    lines.append(f"  Name: {customer.get('name', 'Not provided')}")
    lines.append(f"  Phone: {customer.get('phone', 'Not provided')}")
    lines.append(f"  Address: {customer.get('address', 'Not provided')}")
    lines.append(f"  City: {customer.get('city', 'Not provided')}")
    lines.append(f"  Pincode: {customer.get('pincode', 'Not provided')}")
    
    # What's still needed
    missing = []
    if not customer.get('name'):
        missing.append("name")
    if not customer.get('phone'):
        missing.append("phone")
    if not customer.get('address'):
        missing.append("address")
    if not customer.get('city'):
        missing.append("city")
    if not customer.get('pincode'):
        missing.append("pincode")
    
    if missing:
        lines.append(f"\nStill needed: {', '.join(missing)}")
    else:
        lines.append("\nAll details collected! Ready for confirmation.")
    
    return "\n".join(lines)


async def extract_customer_details(state: AgentState, response: str) -> dict:
    """Extract customer details from conversation using LLM."""
    llm = get_llm()
    
    # Get entire conversation
    conversation = ""
    for msg in state.get("messages", []):
        if hasattr(msg, 'type') and hasattr(msg, 'content'):
            role = "Customer" if msg.type == "human" else "Agent"
            conversation += f"{role}: {msg.content}\n"
    
    extraction_prompt = f"""Extract customer details from this conversation. Return ONLY a JSON object with the fields that were mentioned.
Fields to extract: name, phone, address, city, pincode

Conversation:
{conversation}

Return a valid JSON object like {{"name": "...", "phone": "...", etc.}}
Only include fields that were actually provided. If a field wasn't provided, don't include it."""
    
    try:
        result = await llm.ainvoke([HumanMessage(content=extraction_prompt)])
        
        # Try to parse JSON from response
        import json
        import re
        
        # Find JSON in response
        json_match = re.search(r'\{[^}]+\}', result.content)
        if json_match:
            extracted = json.loads(json_match.group())
            
            # Merge with existing context
            current_customer = state.get("context", {}).get("customer", {})
            for key, value in extracted.items():
                if value and value.lower() not in ["not provided", "n/a", ""]:
                    current_customer[key] = value
            
            return {"customer": current_customer}
    except Exception:
        pass
    
    return {}


def is_order_complete(state: AgentState) -> bool:
    """Check if all required order details are collected."""
    context = state.get("context", {})
    customer = context.get("customer", {})
    
    required = ["name", "phone", "address", "city", "pincode"]
    return all(customer.get(field) for field in required)


def is_confirmation(message: str) -> bool:
    """Check if message is a confirmation."""
    message_lower = message.lower()
    confirmation_words = ["yes", "confirm", "place order", "proceed", "correct", "that's right", "looks good"]
    return any(word in message_lower for word in confirmation_words)


async def place_order(state: AgentState) -> str:
    """Place the order in the database with stock checking."""
    try:
        context = state.get("context") or {}
        customer = context.get("customer") or {}
        current_order = state.get("current_order") or {}
        
        orders_collection = database.get_collection("orders")
        products_collection = database.get_collection("products")
        suppliers_collection = database.get_collection("suppliers")
        queries_collection = database.get_collection("supplier_queries")
        
        # Generate order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        items = current_order.get("items") or []
        
        # If no items in order, try to extract from conversation
        if not items:
            items = await extract_order_items_from_conversation(state, products_collection)
        
        if not items:
            return "I apologize, but I couldn't find the product you wanted to order. Could you please tell me which product you'd like to purchase?"
        
        # Check stock availability
        stock_issues = []
        items_with_stock_info = []
        
        for item in items:
            product_id = item.get("product_id")
            quantity_needed = item.get("quantity", 1)
            
            if product_id is not None:
                # Fetch current stock
                product = await products_collection.find_one({"_id": product_id})
                if product:
                    current_stock = product.get("quantity", 0)
                    stock_shortage = max(0, quantity_needed - current_stock)
                    
                    items_with_stock_info.append({
                        **item,
                        "product_id": product_id,  # Keep original ObjectId for now
                        "current_stock": current_stock,
                        "stock_shortage": stock_shortage,
                        "category": product.get("category", "")
                    })
                    
                    if stock_shortage > 0:
                        stock_issues.append({
                            "product_id": product_id,
                            "product_name": item.get("product_name"),
                            "quantity_needed": quantity_needed,
                            "current_stock": current_stock,
                            "shortage": stock_shortage,
                            "category": product.get("category", "")
                        })
        
        total_amount = sum(item.get("total_price", 0) for item in items)
        
        # Determine order status based on stock
        if stock_issues:
            order_status = OrderStatus.AWAITING_STOCK.value
        else:
            order_status = OrderStatus.PENDING.value
        
        # Prepare items for storage (convert ObjectId to string)
        stored_items = []
        inventory_updates = []
        for item in items_with_stock_info:
            product_id = item.get("product_id")
            current_stock = item.get("current_stock", 0)
            quantity_needed = item.get("quantity", 1)
            
            # Only deduct what's available
            deduct_quantity = min(quantity_needed, current_stock)
            if deduct_quantity > 0:
                inventory_updates.append((product_id, deduct_quantity))
            
            stored_items.append({
                "product_id": str(product_id),
                "product_name": item.get("product_name"),
                "quantity": quantity_needed,
                "unit_price": item.get("unit_price", 0),
                "total_price": item.get("total_price", 0)
            })
        
        order_doc = {
            "order_number": order_number,
            "customer_info": {
                "name": customer.get("name"),
                "phone": customer.get("phone"),
                "address": customer.get("address"),
                "city": customer.get("city"),
                "pincode": customer.get("pincode"),
                "email": customer.get("email")
            },
            "items": stored_items,
            "total_amount": total_amount,
            "status": order_status,
            "awaiting_supplier": bool(stock_issues),
            "conversation_id": state.get("conversation_id"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "estimated_delivery": datetime.utcnow() + timedelta(days=5 if not stock_issues else 10)
        }
        
        result = await orders_collection.insert_one(order_doc)
        order_id = str(result.inserted_id)
        
        # Update inventory for available stock
        for product_id, qty in inventory_updates:
            await products_collection.update_one(
                {"_id": product_id},
                {"$inc": {"quantity": -qty}}
            )
        
        # If stock issues, query suppliers
        if stock_issues:
            queries_created = await query_suppliers_for_stock(
                order_id=order_id,
                order_number=order_number,
                stock_issues=stock_issues,
                suppliers_collection=suppliers_collection,
                queries_collection=queries_collection,
                conversation_id=state.get("conversation_id")
            )
            
            # Log activity
            await log_agent_activity(
                agent_name="order_agent",
                action="order_placed_awaiting_stock",
                details=f"Order {order_number} placed, awaiting supplier response for {len(stock_issues)} items",
                order_id=order_id,
                conversation_id=state.get("conversation_id")
            )
            
            shortage_details = "\n".join([
                f"  • {issue['product_name']}: Need {issue['shortage']} more units"
                for issue in stock_issues
            ])
            
            return f"""📦 Order Created - Awaiting Stock

Order Number: {order_number}
Total Amount: ₹{total_amount:,.2f}

⚠️ Some items are currently low on stock:
{shortage_details}

We've contacted {queries_created} supplier(s) to fulfill your order.
Your order may take 2-3 extra days for delivery.

Delivery Details:
{customer.get('name')}
{customer.get('address')}
{customer.get('city')} - {customer.get('pincode')}
Phone: {customer.get('phone')}

We'll notify you once we confirm stock availability. Thank you for your patience!"""
        
        # Normal order - sufficient stock
        await log_agent_activity(
            agent_name="order_agent",
            action="order_placed",
            details=f"Order {order_number} placed for {customer.get('name')}",
            order_id=order_id,
            conversation_id=state.get("conversation_id")
        )
        
        return f"""🎉 Order Placed Successfully!

Order Number: {order_number}
Total Amount: ₹{total_amount:,.2f}

Delivery Details:
{customer.get('name')}
{customer.get('address')}
{customer.get('city')} - {customer.get('pincode')}
Phone: {customer.get('phone')}

Estimated Delivery: 5-7 business days

Thank you for shopping with us! You'll receive updates on your order status."""
    except Exception as e:
        import traceback
        print(f"ORDER PLACEMENT ERROR: {e}")
        traceback.print_exc()
        return f"I apologize, there was an error placing your order: {str(e)}. Please try again."


async def query_suppliers_for_stock(
    order_id: str,
    order_number: str,
    stock_issues: list,
    suppliers_collection,
    queries_collection,
    conversation_id: str
) -> int:
    """Query all suppliers in relevant categories for stock by creating conversations."""
    conversations_collection = database.get_collection("conversations")
    queries_created = 0
    
    for issue in stock_issues:
        category = issue.get("category", "")
        product_name = issue.get("product_name", "")
        shortage = issue.get("shortage", 0)
        
        # Find all active suppliers in this category
        suppliers = await suppliers_collection.find({
            "categories": category,
            "is_active": True
        }).to_list(50)
        
        for supplier in suppliers:
            query_id = f"SQ-{uuid.uuid4().hex[:8].upper()}"
            supplier_id = str(supplier.get("_id"))
            supplier_name = supplier.get("name", "Supplier")
            
            # Create the agent's message to the supplier
            agent_message = f"""Hello {supplier_name}! 👋

We have an urgent stock requirement for an order we're processing.

📦 **Product Needed:** {product_name}
📊 **Quantity Required:** {shortage} units
🆔 **Order Reference:** {order_number}
🔖 **Query ID:** {query_id}

Could you please let us know:
1. Do you have this product available?
2. If yes, how many units can you supply?
3. What is your price and delivery timeline?

Please reply with your availability. Thank you!"""

            # Create or update supplier conversation
            existing_conv = await conversations_collection.find_one({
                "type": "supplier",
                "supplier_id": supplier_id,
                "is_active": True
            })
            
            if existing_conv:
                # Add message to existing conversation
                await conversations_collection.update_one(
                    {"_id": existing_conv["_id"]},
                    {
                        "$push": {
                            "messages": {
                                "role": "assistant",
                                "content": agent_message,
                                "timestamp": datetime.utcnow(),
                                "metadata": {"query_id": query_id, "order_number": order_number}
                            }
                        },
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
                supplier_conversation_id = str(existing_conv["_id"])
            else:
                # Create new conversation with supplier
                supplier_conv_id = f"SC-{uuid.uuid4().hex[:12]}"
                new_conv = {
                    "conversation_id": supplier_conv_id,
                    "type": "supplier",
                    "supplier_id": supplier_id,
                    "messages": [
                        {
                            "role": "assistant",
                            "content": agent_message,
                            "timestamp": datetime.utcnow(),
                            "metadata": {"query_id": query_id, "order_number": order_number}
                        }
                    ],
                    "context": {"pending_queries": [query_id]},
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                result = await conversations_collection.insert_one(new_conv)
                supplier_conversation_id = supplier_conv_id
            
            # Create the query record
            query_doc = {
                "query_id": query_id,
                "order_id": order_id,
                "order_number": order_number,
                "supplier_id": supplier_id,
                "supplier_name": supplier_name,
                "product_id": str(issue.get("product_id")),
                "product_name": product_name,
                "product_category": category,
                "quantity_needed": shortage,
                "conversation_id": conversation_id,  # Original customer conversation
                "supplier_conversation_id": supplier_conversation_id,
                "status": SupplierQueryStatus.PENDING.value,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=24)
            }
            
            await queries_collection.insert_one(query_doc)
            queries_created += 1
            
            print(f"📤 Supplier Message Sent: {query_id} -> {supplier_name} for {product_name}")
    
    return queries_created


async def extract_order_items_from_conversation(state: AgentState, products_collection) -> list:
    """Extract ordered product and quantity from conversation history."""
    from bson import ObjectId
    import re
    
    # Get conversation text
    conversation = ""
    for msg in state.get("messages", []):
        if hasattr(msg, 'content'):
            conversation += f"{msg.content}\n"
    
    conversation_lower = conversation.lower()
    
    # Extract quantity from conversation
    quantity = 1  # Default quantity
    
    # Look for patterns like "10 sets", "want 5", "order 3", "need 2", etc.
    quantity_patterns = [
        r'(?:want|need|order|get|buy|give me|i\'ll take)\s+(\d+)',  # "want 10", "order 5"
        r'(\d+)\s+(?:sets?|pieces?|units?|items?|pcs?)',  # "10 sets", "5 pieces"
        r'(\d+)\s+of\s+(?:them|it|these|those)',  # "10 of them"
        r'quantity[:\s]+(\d+)',  # "quantity: 10"
    ]
    
    for pattern in quantity_patterns:
        match = re.search(pattern, conversation_lower)
        if match:
            quantity = int(match.group(1))
            break
    
    # Find all products and check which one was mentioned in conversation
    products = await products_collection.find({}).to_list(100)
    
    for product in products:
        product_name = product.get("name", "").lower()
        # Check if product name (or key parts) appears in conversation
        name_parts = product_name.split()
        if len(name_parts) >= 2:
            # Check for partial match (at least first two words)
            partial_name = " ".join(name_parts[:3])
            if partial_name in conversation_lower or product_name in conversation_lower:
                unit_price = product.get("price", 0)
                return [{
                    "product_id": product.get("_id"),
                    "product_name": product.get("name"),
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": unit_price * quantity
                }]
    
    return []


async def log_agent_activity(agent_name: str, action: str, details: str, 
                             order_id: str = None, conversation_id: str = None):
    """Log agent activity to database."""
    activities_collection = database.get_collection("agent_activities")
    
    activity = {
        "agent_name": agent_name,
        "action": action,
        "details": details,
        "order_id": order_id,
        "conversation_id": conversation_id,
        "timestamp": datetime.utcnow(),
        "success": True
    }
    
    await activities_collection.insert_one(activity)


async def get_order_status(order_number: str) -> dict:
    """Get status of an order by order number."""
    orders_collection = database.get_collection("orders")
    
    order = await orders_collection.find_one({"order_number": order_number})
    
    if not order:
        return {"found": False, "message": f"Order {order_number} not found."}
    
    return {
        "found": True,
        "order_number": order["order_number"],
        "status": order["status"],
        "total_amount": order["total_amount"],
        "estimated_delivery": order.get("estimated_delivery"),
        "items": order["items"]
    }
