"""
Supplier Liaison Agent - Manages communication with multiple suppliers.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agents.state import AgentState
from agents.router import get_llm
from database.connection import database
from database.models import BottleneckType, BottleneckSeverity
from datetime import datetime, timedelta
from bson import ObjectId


SUPPLIER_SYSTEM_PROMPT = """You are a procurement agent for an MSME jewelry business called "Bhangale Jewellers".

IMPORTANT: You are communicating with a SUPPLIER on behalf of your business. The person you're chatting with is a SUPPLIER who provides products to you. You are BUYING products FROM them, not selling TO them.

Your role:
1. Ask about product availability and pricing
2. Negotiate prices and delivery timelines
3. Record their stock availability responses
4. Confirm order details when supplier agrees to provide stock

CRITICAL RULES:
- NEVER ask for the supplier's address, phone, or personal details - you already have those
- NEVER try to place an order for delivery TO the supplier
- You are procuring stock FROM them, they deliver TO your warehouse
- Focus on: "Do you have X product? How many? What price? When can you deliver?"

When supplier confirms availability:
- Thank them for the information
- Confirm the quantity and price
- Ask for delivery timeline
- Do NOT ask for their personal details

Your business address for deliveries: Bhangale Jewellers, 123 Main Market, Mumbai - 400001"""


async def supplier_agent(state: AgentState) -> AgentState:
    """
    Handle supplier communications.
    """
    conversation_type = state.get("conversation_type")
    
    if conversation_type == "supplier":
        # This is a direct supplier conversation
        return await handle_supplier_conversation(state)
    else:
        # This is an internal call to query suppliers
        return await query_suppliers_for_product(state)


async def handle_supplier_conversation(state: AgentState) -> AgentState:
    """Handle direct conversation with a supplier."""
    llm = get_llm()
    
    supplier_id = state.get("supplier_id")
    supplier_info = await get_supplier_info(supplier_id)
    
    # Get pending queries that this supplier might be responding to
    pending_queries = await get_pending_queries_for_supplier(supplier_id)
    
    # Build detailed context about what we need from this supplier
    query_details = []
    for q in pending_queries:
        query_details.append(
            f"- Query {q.get('query_id')}: Need {q.get('quantity_needed')} units of {q.get('product_name')} "
            f"(for Order {q.get('order_number')})"
        )
    
    context = f"""
SUPPLIER YOU ARE TALKING TO:
Name: {supplier_info.get('name', 'Unknown')}
Contact: {supplier_info.get('contact_person', 'Unknown')}
Categories: {', '.join(supplier_info.get('categories', []))}

WHAT YOU NEED FROM THEM:
{chr(10).join(query_details) if query_details else 'No specific pending queries - general inquiry'}

REMEMBER: You are BUYING from them. Do NOT collect their personal info. Just confirm availability, price, quantity, and delivery timeline.
"""
    
    system_content = SUPPLIER_SYSTEM_PROMPT + f"\n\nCurrent Context:\n{context}"
    messages = [SystemMessage(content=system_content)]
    
    # Add conversation history
    for msg in state.get("messages", []):
        if hasattr(msg, 'type'):
            if msg.type == "human":
                messages.append(HumanMessage(content=msg.content))
            elif msg.type == "ai":
                messages.append(AIMessage(content=msg.content))
    
    response = await llm.ainvoke(messages)
    
    # Process supplier response for any order updates
    await process_supplier_response(state, response.content)
    
    state["final_response"] = response.content
    state["messages"] = state.get("messages", []) + [AIMessage(content=response.content)]
    
    return state


async def query_suppliers_for_product(state: AgentState) -> AgentState:
    """Query all relevant suppliers for a product."""
    pending_queries = state.get("pending_supplier_queries", [])
    
    if not pending_queries:
        state["final_response"] = "No pending supplier queries."
        return state
    
    suppliers_collection = database.get_collection("suppliers")
    queries_collection = database.get_collection("supplier_queries")
    
    messages_to_send = []
    
    for query in pending_queries:
        product_name = query.get("product")
        quantity_needed = query.get("needed", 1)
        
        # Find suppliers who might have this product
        suppliers = await suppliers_collection.find({"is_active": True}).to_list(100)
        
        for supplier in suppliers:
            # Create a query record
            query_record = {
                "supplier_id": str(supplier["_id"]),
                "supplier_name": supplier.get("name"),
                "product_name": product_name,
                "quantity_needed": quantity_needed,
                "status": "pending",
                "created_at": datetime.utcnow(),
                "conversation_id": state.get("conversation_id")
            }
            
            await queries_collection.insert_one(query_record)
            
            messages_to_send.append({
                "supplier_id": str(supplier["_id"]),
                "supplier_name": supplier.get("name"),
                "message": f"Hello! We need {quantity_needed} units of {product_name}. Do you have it available? What's your price and delivery timeline?"
            })
    
    # Create bottleneck for supplier delay tracking
    if messages_to_send:
        await create_supplier_delay_bottleneck(pending_queries)
    
    state["final_response"] = f"Queries sent to {len(messages_to_send)} suppliers. Waiting for responses."
    state["awaiting_supplier_response"] = True
    state["context"]["supplier_messages"] = messages_to_send
    
    return state


async def get_supplier_info(supplier_id: str) -> dict:
    """Get supplier information by ID."""
    if not supplier_id:
        return {}
    
    try:
        suppliers_collection = database.get_collection("suppliers")
        supplier = await suppliers_collection.find_one({"_id": ObjectId(supplier_id)})
        return supplier or {}
    except Exception:
        return {}


async def get_pending_queries_for_supplier(supplier_id: str) -> list:
    """Get pending queries for a specific supplier."""
    queries_collection = database.get_collection("supplier_queries")
    
    queries = await queries_collection.find({
        "supplier_id": supplier_id,
        "status": "pending"
    }).to_list(50)
    
    return queries


def format_pending_queries(queries: list) -> str:
    """Format pending queries for LLM context."""
    if not queries:
        return "No pending inquiries."
    
    lines = []
    for q in queries:
        lines.append(f"- {q.get('product_name')}: Need {q.get('quantity_needed')} units")
    
    return "\n".join(lines)


async def process_supplier_response(state: AgentState, response: str):
    """Process supplier response, update inventory, propagate to other suppliers, notify customer."""
    supplier_id = state.get("supplier_id")
    if not supplier_id:
        return
    
    queries_collection = database.get_collection("supplier_queries")
    products_collection = database.get_collection("products")
    orders_collection = database.get_collection("orders")
    activities_collection = database.get_collection("agent_activities")
    conversations_collection = database.get_collection("conversations")
    
    # Get the last message from user (supplier's response)
    messages = state.get("messages", [])
    supplier_message = ""
    for msg in reversed(messages):
        if hasattr(msg, 'type') and msg.type == "human":
            supplier_message = msg.content
            break
    
    if not supplier_message:
        return
    
    # Use LLM to extract availability info from supplier message
    llm = get_llm()
    extraction_prompt = f"""Extract stock availability information from this supplier response.

Supplier message: "{supplier_message}"

Respond with a JSON object containing:
- available: true/false (does the supplier have the product?)
- quantity: number (how many units available, 0 if not available or not mentioned)
- price: number or null (price per unit if mentioned)
- delivery_days: number or null (delivery time in days if mentioned)

Only respond with the JSON, no other text."""

    try:
        extraction_response = await llm.ainvoke([HumanMessage(content=extraction_prompt)])
        import json
        import re
        
        # Extract JSON from response
        json_match = re.search(r'\{[^}]+\}', extraction_response.content)
        if json_match:
            extracted = json.loads(json_match.group())
        else:
            extracted = {"available": False, "quantity": 0}
    except Exception:
        # Fallback to keyword matching
        response_lower = supplier_message.lower()
        if any(word in response_lower for word in ["available", "have", "yes", "can supply", "in stock"]):
            extracted = {"available": True, "quantity": 0}
            import re
            qty_match = re.search(r'(\d+)\s*(?:units?|pieces?|pcs?|items?)?', response_lower)
            if qty_match:
                extracted["quantity"] = int(qty_match.group(1))
        else:
            extracted = {"available": False, "quantity": 0}
    
    is_available = extracted.get("available", False)
    quantity_provided = extracted.get("quantity", 0)
    delivery_days = extracted.get("delivery_days")
    price = extracted.get("price")
    
    print(f"📊 Extracted from supplier: available={is_available}, qty={quantity_provided}, delivery={delivery_days}d, price=₹{price}")
    
    if not is_available:
        # Mark this supplier's queries as unavailable
        await queries_collection.update_many(
            {"supplier_id": supplier_id, "status": "pending"},
            {
                "$set": {
                    "status": "unavailable",
                    "response_message": supplier_message,
                    "responded_at": datetime.utcnow()
                }
            }
        )
        print(f"❌ Supplier {supplier_id} has no stock available")
        return
    
    # Get pending queries for this supplier
    pending_queries = await queries_collection.find({
        "supplier_id": supplier_id,
        "status": "pending"
    }).to_list(50)
    
    for query in pending_queries:
        product_id = query.get("product_id")
        order_id = query.get("order_id")
        order_number = query.get("order_number")
        original_needed = query.get("quantity_needed", 0)
        product_name = query.get("product_name")
        customer_conversation_id = query.get("conversation_id")  # Original customer conversation
        
        # Calculate how much this supplier is providing (capped at what we need)
        actual_provided = min(quantity_provided, original_needed)
        remaining_after_this = original_needed - actual_provided
        
        # Update this query as fulfilled
        await queries_collection.update_one(
            {"_id": query["_id"]},
            {
                "$set": {
                    "status": "available",
                    "response_message": supplier_message,
                    "response_quantity": actual_provided,
                    "price_per_unit": price,
                    "delivery_days": delivery_days,
                    "responded_at": datetime.utcnow()
                }
            }
        )
        
        # Update inventory with the stock provided
        await products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"quantity": actual_provided}}
        )
        
        print(f"✅ Stock added: {product_name} +{actual_provided} units from {query.get('supplier_name')}")
        
        # Log activity
        await activities_collection.insert_one({
            "agent_name": "supplier_agent",
            "action": "stock_received_from_supplier",
            "details": f"+{actual_provided} units of {product_name} from {query.get('supplier_name')} at ₹{price}/unit",
            "order_id": order_id,
            "conversation_id": customer_conversation_id,
            "timestamp": datetime.utcnow(),
            "success": True
        })
        
        # Check if we still need more stock for this product
        if remaining_after_this > 0:
            # Update other pending suppliers with reduced requirement
            await update_other_suppliers_requirement(
                product_id=product_id,
                product_name=product_name,
                order_id=order_id,
                order_number=order_number,
                new_requirement=remaining_after_this,
                fulfilled_by=query.get("supplier_name"),
                queries_collection=queries_collection,
                conversations_collection=conversations_collection
            )
        else:
            # Requirement fully met - cancel other pending queries for this product/order
            await queries_collection.update_many(
                {
                    "order_id": order_id,
                    "product_id": product_id,
                    "supplier_id": {"$ne": supplier_id},
                    "status": "pending"
                },
                {
                    "$set": {
                        "status": "cancelled",
                        "cancelled_reason": f"Requirement fulfilled by {query.get('supplier_name')}",
                        "cancelled_at": datetime.utcnow()
                    }
                }
            )
            
            # Notify other suppliers that we no longer need this product
            await notify_suppliers_requirement_fulfilled(
                order_id=order_id,
                product_id=product_id,
                product_name=product_name,
                fulfilled_by=query.get("supplier_name"),
                supplier_id_to_skip=supplier_id,
                conversations_collection=conversations_collection
            )
        
        # Check if ALL products for the order are now fulfilled
        still_pending = await queries_collection.count_documents({
            "order_id": order_id,
            "status": "pending"
        })
        
        if still_pending == 0:
            # All stock requirements met - update order and notify customer
            delivery_estimate = datetime.utcnow() + timedelta(days=delivery_days or 5)
            
            await orders_collection.update_one(
                {"_id": ObjectId(order_id)},
                {
                    "$set": {
                        "status": "pending",
                        "awaiting_supplier": False,
                        "estimated_delivery": delivery_estimate,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Notify the customer
            await notify_customer_stock_available(
                customer_conversation_id=customer_conversation_id,
                order_number=order_number,
                delivery_days=delivery_days or 5,
                conversations_collection=conversations_collection
            )
            
            print(f"🎉 Order {order_number} fully stocked! Customer notified.")


async def update_other_suppliers_requirement(
    product_id: str,
    product_name: str,
    order_id: str,
    order_number: str,
    new_requirement: int,
    fulfilled_by: str,
    queries_collection,
    conversations_collection
):
    """Update other pending suppliers about reduced requirement."""
    other_queries = await queries_collection.find({
        "order_id": order_id,
        "product_id": product_id,
        "status": "pending"
    }).to_list(50)
    
    for q in other_queries:
        # Update the requirement in the query
        await queries_collection.update_one(
            {"_id": q["_id"]},
            {"$set": {"quantity_needed": new_requirement}}
        )
        
        # Send updated message to supplier conversation
        update_message = f"""📢 **Update on Stock Requirement**

{fulfilled_by} has provided partial stock. Our updated requirement is:

📦 **Product:** {product_name}
📊 **New Quantity Needed:** {new_requirement} units (reduced from {q.get('quantity_needed')})
🆔 **Order Reference:** {order_number}

If you can supply any of this quantity, please let us know your availability, price, and delivery timeline."""

        # Find and update supplier conversation
        supplier_conv = await conversations_collection.find_one({
            "type": "supplier",
            "supplier_id": q.get("supplier_id"),
            "is_active": True
        })
        
        if supplier_conv:
            await conversations_collection.update_one(
                {"_id": supplier_conv["_id"]},
                {
                    "$push": {
                        "messages": {
                            "role": "assistant",
                            "content": update_message,
                            "timestamp": datetime.utcnow(),
                            "metadata": {"type": "requirement_update", "order_number": order_number}
                        }
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            print(f"📤 Updated {q.get('supplier_name')}: now need {new_requirement} units of {product_name}")


async def notify_suppliers_requirement_fulfilled(
    order_id: str,
    product_id: str,
    product_name: str,
    fulfilled_by: str,
    supplier_id_to_skip: str,
    conversations_collection
):
    """Notify other suppliers that we no longer need this product."""
    queries_collection = database.get_collection("supplier_queries")
    
    cancelled_queries = await queries_collection.find({
        "order_id": order_id,
        "product_id": product_id,
        "supplier_id": {"$ne": supplier_id_to_skip},
        "status": "cancelled"
    }).to_list(50)
    
    for q in cancelled_queries:
        cancel_message = f"""📢 **Stock Requirement Fulfilled**

Thank you for your response! We wanted to let you know that our requirement for **{product_name}** has been fulfilled by another supplier ({fulfilled_by}).

We appreciate your time and will reach out again for future requirements. Thank you for being our partner! 🙏"""

        supplier_conv = await conversations_collection.find_one({
            "type": "supplier",
            "supplier_id": q.get("supplier_id"),
            "is_active": True
        })
        
        if supplier_conv:
            await conversations_collection.update_one(
                {"_id": supplier_conv["_id"]},
                {
                    "$push": {
                        "messages": {
                            "role": "assistant",
                            "content": cancel_message,
                            "timestamp": datetime.utcnow(),
                            "metadata": {"type": "requirement_cancelled", "order_id": order_id}
                        }
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )


async def notify_customer_stock_available(
    customer_conversation_id: str,
    order_number: str,
    delivery_days: int,
    conversations_collection
):
    """Send message to customer that their order is now ready."""
    customer_message = f"""🎉 **Great News About Your Order!**

Hi! We wanted to update you on your order **{order_number}**.

✅ We've secured all the products for your order from our suppliers!

📦 **Estimated Delivery:** {delivery_days} days from now

Your order is now being processed and will be shipped soon. Thank you for your patience!

If you have any questions, feel free to ask. 😊"""

    # Find and update customer conversation
    customer_conv = await conversations_collection.find_one({
        "conversation_id": customer_conversation_id
    })
    
    if customer_conv:
        await conversations_collection.update_one(
            {"_id": customer_conv["_id"]},
            {
                "$push": {
                    "messages": {
                        "role": "assistant",
                        "content": customer_message,
                        "timestamp": datetime.utcnow(),
                        "metadata": {"type": "stock_update", "order_number": order_number}
                    }
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        print(f"📧 Customer notified about order {order_number} being ready!")


async def create_supplier_delay_bottleneck(queries: list):
    """Create bottleneck for tracking supplier response delays."""
    bottlenecks_collection = database.get_collection("bottlenecks")
    
    product_names = [q.get("product") for q in queries]
    
    bottleneck = {
        "type": BottleneckType.SUPPLIER_DELAY.value,
        "severity": BottleneckSeverity.MEDIUM.value,
        "title": "Awaiting Supplier Responses",
        "description": f"Waiting for supplier responses for: {', '.join(product_names)}",
        "affected_resources": product_names,
        "suggested_actions": [
            "Follow up with suppliers if no response in 24 hours",
            "Consider alternative suppliers",
            "Update customer on potential delay"
        ],
        "is_resolved": False,
        "detected_at": datetime.utcnow()
    }
    
    await bottlenecks_collection.insert_one(bottleneck)


async def get_all_suppliers() -> list:
    """Get all active suppliers."""
    suppliers_collection = database.get_collection("suppliers")
    suppliers = await suppliers_collection.find({"is_active": True}).to_list(100)
    return suppliers
