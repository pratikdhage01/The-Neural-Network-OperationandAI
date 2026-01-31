"""
Customer Service Agent - Handles product inquiries and customer interactions.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agents.state import AgentState
from agents.router import get_llm
from database.connection import database


CUSTOMER_SYSTEM_PROMPT = """You are a friendly and helpful customer service agent for an MSME that sells jewelry, kitchen appliances, and makeup products.

Your responsibilities:
1. Help customers browse and find products
2. Provide detailed product information including prices and descriptions
3. Check product availability
4. Answer questions about products
5. Guide customers to place orders when they're ready

Available product categories:
- Jewelry (necklaces, rings, bracelets, earrings)
- Kitchen Appliances (mixers, toasters, blenders, air fryers, etc.)
- Makeup (lipsticks, foundations, mascaras, eyeshadow palettes, etc.)

Current inventory will be provided to you. Use this information to answer customer queries accurately.

When a customer wants to buy something, confirm the product details and let them know you'll help them place the order. Collect their name, phone number, and delivery address.

Be conversational, warm, and helpful. Ask clarifying questions if needed. Always provide prices in INR (₹).

IMPORTANT: If a product is out of stock, inform the customer that you can check with suppliers and get back to them."""


async def customer_agent(state: AgentState) -> AgentState:
    """
    Handle customer inquiries about products.
    """
    llm = get_llm()
    
    # Fetch current inventory for context
    inventory_context = await get_inventory_context()
    
    # Build messages for LLM
    system_content = CUSTOMER_SYSTEM_PROMPT + f"\n\nCurrent Inventory:\n{inventory_context}"
    messages = [SystemMessage(content=system_content)]
    
    # Add conversation history
    for msg in state.get("messages", []):
        if hasattr(msg, 'type'):
            if msg.type == "human":
                messages.append(HumanMessage(content=msg.content))
            elif msg.type == "ai":
                messages.append(AIMessage(content=msg.content))
        elif isinstance(msg, dict):
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))
    
    # Get LLM response
    response = await llm.ainvoke(messages)
    
    # Update state
    state["final_response"] = response.content
    state["messages"] = state.get("messages", []) + [AIMessage(content=response.content)]
    
    # Check if customer wants to order - update context
    content_lower = response.content.lower()
    if any(phrase in content_lower for phrase in ["place an order", "ready to order", "proceed with", "delivery details"]):
        state["current_agent"] = "ORDER_AGENT"
    
    return state


async def get_inventory_context() -> str:
    """Fetch inventory and format for LLM context."""
    try:
        products_collection = database.get_collection("products")
        products = await products_collection.find({"quantity": {"$gt": 0}}).to_list(100)
        
        if not products:
            return "No products currently in stock."
        
        context_lines = []
        by_category = {}
        
        for p in products:
            category = p.get("category", "other")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(p)
        
        for category, items in by_category.items():
            context_lines.append(f"\n{category.upper().replace('_', ' ')}:")
            for item in items:
                stock_status = "In Stock" if item.get("quantity", 0) > 5 else f"Low Stock ({item.get('quantity')} left)"
                context_lines.append(
                    f"  - {item.get('name')}: ₹{item.get('price', 0):,.2f} | {stock_status} | {item.get('description', '')[:50]}..."
                )
        
        return "\n".join(context_lines)
    except Exception as e:
        return f"Unable to fetch inventory: {str(e)}"


async def search_products(query: str, category: str = None) -> list:
    """Search products by name or category."""
    try:
        products_collection = database.get_collection("products")
        
        search_filter = {}
        if category:
            search_filter["category"] = category
        if query:
            search_filter["$or"] = [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        
        products = await products_collection.find(search_filter).to_list(20)
        return products
    except Exception:
        return []
