"""
Leads Communication Agent - AI-powered sales outreach simulation.

Handles conversation with potential leads using Gemini AI,
qualifies leads based on their responses, and manages conversation flow.
"""

from datetime import datetime
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from database.connection import database
import os


def get_llm():
    """Get the Gemini LLM instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.7
    )


# Global state for leads conversations (per-session, will be stored in DB)
leads_state = {
    "leads": [],
    "current_index": 0,
    "sales_context": "",
    "conversation_history": {},
    "potential_leads": []
}


async def set_sales_context(context: str) -> dict:
    """Set the sales context for the agent."""
    leads_state["sales_context"] = context
    return {"success": True, "message": "Context set successfully"}


async def load_leads(leads: list, clear_existing: bool = True) -> dict:
    """Load leads into the system and store in database."""
    leads_collection = database.get_collection("leads")
    
    # Clear existing leads from database if requested
    if clear_existing:
        await leads_collection.delete_many({})
    
    # Clear existing leads state
    leads_state["leads"] = leads
    leads_state["current_index"] = 0
    leads_state["conversation_history"] = {}
    leads_state["potential_leads"] = []
    
    # Store leads in database
    for lead in leads:
        lead_doc = {
            "lead_id": lead.get("client_id", lead.get("lead_id")),
            "name": lead.get("name"),
            "email": lead.get("email"),
            "phone": lead.get("phone"),
            "company": lead.get("company"),
            "industry": lead.get("industry"),
            "role": lead.get("role", ""),
            "status": "pending",
            "is_potential": False,
            "conversation_summary": "",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await leads_collection.insert_one(lead_doc)
    
    return {
        "success": True,
        "message": f"Loaded {len(leads)} leads (cleared previous)",
        "total_leads": len(leads)
    }


async def get_demo_leads() -> list:
    """Get demo leads data."""
    return [
        {
            "client_id": "LEAD_001",
            "name": "John Anderson",
            "email": "john.anderson@techcorp.com",
            "phone": "+1-555-0101",
            "company": "TechCorp Industries",
            "industry": "Technology",
            "role": "CTO"
        },
        {
            "client_id": "LEAD_002",
            "name": "Sarah Mitchell",
            "email": "sarah.mitchell@retailmax.com",
            "phone": "+1-555-0102",
            "company": "RetailMax Solutions",
            "industry": "Retail",
            "role": "VP of Operations"
        },
        {
            "client_id": "LEAD_003",
            "name": "Michael Chen",
            "email": "m.chen@healthplus.com",
            "phone": "+1-555-0103",
            "company": "HealthPlus Medical",
            "industry": "Healthcare",
            "role": "Director of IT"
        },
        {
            "client_id": "LEAD_004",
            "name": "Emily Rodriguez",
            "email": "emily.r@financepro.com",
            "phone": "+1-555-0104",
            "company": "FinancePro Group",
            "industry": "Finance",
            "role": "Chief Innovation Officer"
        },
        {
            "client_id": "LEAD_005",
            "name": "David Thompson",
            "email": "d.thompson@manufacturing.com",
            "phone": "+1-555-0105",
            "company": "Thompson Manufacturing",
            "industry": "Manufacturing",
            "role": "Operations Manager"
        }
    ]


async def start_conversation() -> dict:
    """Start conversation with current lead."""
    if not leads_state["sales_context"]:
        return {"success": False, "message": "Please set sales context first"}
    
    if not leads_state["leads"]:
        return {"success": False, "message": "No leads loaded"}
    
    if leads_state["current_index"] >= len(leads_state["leads"]):
        # All leads processed
        return {
            "success": True,
            "finished": True,
            "message": "All leads processed",
            "total_potential_leads": len(leads_state["potential_leads"])
        }
    
    lead = leads_state["leads"][leads_state["current_index"]]
    lead_id = lead.get("client_id", lead.get("lead_id"))
    
    # Initial message
    initial_message = """Hello! I'm reaching out to discuss an opportunity that might interest you.

Would you like to continue this conversation or would you prefer I don't contact you further?
Please reply with 'CONTINUE' to proceed or 'STOP' to end this conversation."""
    
    leads_state["conversation_history"][lead_id] = [
        {"role": "agent", "content": initial_message}
    ]
    
    return {
        "success": True,
        "lead": lead,
        "message": initial_message,
        "current_index": leads_state["current_index"],
        "total_leads": len(leads_state["leads"])
    }


async def send_message(lead_id: str, user_message: str) -> dict:
    """Process user message and get AI response. Qualifies within 3-4 messages."""
    if lead_id not in leads_state["conversation_history"]:
        return {"success": False, "message": "Invalid conversation"}
    
    # Add user message to history
    leads_state["conversation_history"][lead_id].append({
        "role": "user",
        "content": user_message
    })
    
    # Count user messages (excluding initial agent message)
    user_message_count = len([m for m in leads_state["conversation_history"][lead_id] if m["role"] == "user"])
    
    # Check if user wants to stop
    if "STOP" in user_message.upper():
        leads_state["current_index"] += 1
        
        # Update lead status in DB
        leads_collection = database.get_collection("leads")
        await leads_collection.update_one(
            {"lead_id": lead_id},
            {"$set": {"status": "not_interested", "updated_at": datetime.utcnow()}}
        )
        
        return {
            "success": True,
            "stopped": True,
            "message": "Thank you for your time. Have a great day!",
            "next_lead": leads_state["current_index"] < len(leads_state["leads"])
        }
    
    # Check if this is the first response (CONTINUE/STOP check)
    if user_message_count == 1:
        if "CONTINUE" not in user_message.upper():
            leads_state["current_index"] += 1
            return {
                "success": True,
                "stopped": True,
                "message": "Thank you for your time. Have a great day!",
                "next_lead": leads_state["current_index"] < len(leads_state["leads"])
            }
    
    # Get current lead
    lead = leads_state["leads"][leads_state["current_index"]]
    
    # Build conversation context - for quick qualification
    conversation_context = f"""You are a sales agent analyzing a potential customer. Your context: {leads_state['sales_context']}

You are talking to:
Name: {lead.get('name')}
Company: {lead.get('company')}
Industry: {lead.get('industry')}
Role: {lead.get('role', 'N/A')}

Message count: {user_message_count} (You MUST make a decision by message 3-4)

Conversation history:
"""
    for msg in leads_state["conversation_history"][lead_id]:
        role = "Agent" if msg["role"] == "agent" else "Client"
        conversation_context += f"{role}: {msg['content']}\n"
    
    # Force decision by message 3-4
    if user_message_count >= 3:
        conversation_context += f"""
CRITICAL: This is message {user_message_count}. You MUST make a final decision NOW.
Analyze the conversation and determine if this person is a POTENTIAL LEAD or NOT.

Signs of potential lead:
- Asking questions about the product/service
- Showing interest or curiosity
- Wanting to know pricing, features, or details
- Agreeing to a demo or follow-up call
- Positive or engaged responses

Signs of NOT a lead:
- Short dismissive responses
- Clearly not interested
- Wrong person/industry fit
- No engagement

Client's message: {user_message}

Respond with a brief closing message, and you MUST end with either [QUALIFIED] or [NOT_QUALIFIED].
Example: "Thank you for your interest! I'll have our team reach out with more details. [QUALIFIED]"
Or: "I understand this isn't a priority for you right now. Thank you for your time! [NOT_QUALIFIED]"

Your response:"""
    else:
        conversation_context += f"""
Instructions:
1. Ask ONE quick qualifying question
2. Keep it to 1-2 sentences max
3. Try to gauge their interest level quickly
4. We need to qualify them within 3-4 total messages

Client's response: {user_message}

Your response:"""
    
    # Get AI response
    try:
        llm = get_llm()
        response = await llm.ainvoke([HumanMessage(content=conversation_context)])
        ai_response = response.content
    except Exception as e:
        return {"success": False, "message": f"Error calling AI: {str(e)}"}
    
    # Check for qualification tags
    is_potential = False
    conversation_ended = False
    alert_message = None
    
    if "[QUALIFIED]" in ai_response:
        is_potential = True
        conversation_ended = True
        ai_response = ai_response.replace("[QUALIFIED]", "").strip()
        alert_message = "🎯 ADDED TO POTENTIAL LEADS DATABASE!"
        
        # Add to potential leads
        leads_state["potential_leads"].append({
            **lead,
            "summary": user_message
        })
        
        # Update lead in DB
        leads_collection = database.get_collection("leads")
        await leads_collection.update_one(
            {"lead_id": lead_id},
            {
                "$set": {
                    "status": "potential",
                    "is_potential": True,
                    "conversation_summary": user_message,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
    elif "[NOT_QUALIFIED]" in ai_response:
        conversation_ended = True
        ai_response = ai_response.replace("[NOT_QUALIFIED]", "").strip()
        alert_message = "Lead not qualified - moving to next"
        
        # Update lead in DB
        leads_collection = database.get_collection("leads")
        await leads_collection.update_one(
            {"lead_id": lead_id},
            {"$set": {"status": "not_interested", "updated_at": datetime.utcnow()}}
        )
    
    # Also check old tags for compatibility
    elif "[POTENTIAL_YES]" in ai_response:
        is_potential = True
        conversation_ended = True
        ai_response = ai_response.replace("[POTENTIAL_YES]", "").strip()
        alert_message = "🎯 ADDED TO POTENTIAL LEADS DATABASE!"
        leads_state["potential_leads"].append({**lead, "summary": user_message})
        leads_collection = database.get_collection("leads")
        await leads_collection.update_one(
            {"lead_id": lead_id},
            {"$set": {"status": "potential", "is_potential": True, "updated_at": datetime.utcnow()}}
        )
    elif "[POTENTIAL_NO]" in ai_response:
        conversation_ended = True
        ai_response = ai_response.replace("[POTENTIAL_NO]", "").strip()
        alert_message = "Lead not qualified - moving to next"
        leads_collection = database.get_collection("leads")
        await leads_collection.update_one(
            {"lead_id": lead_id},
            {"$set": {"status": "not_interested", "updated_at": datetime.utcnow()}}
        )
    
    # Add AI response to history
    leads_state["conversation_history"][lead_id].append({
        "role": "agent",
        "content": ai_response
    })
    
    if conversation_ended:
        leads_state["current_index"] += 1
        
        # Check if all leads are done
        if leads_state["current_index"] >= len(leads_state["leads"]):
            return {
                "success": True,
                "message": ai_response,
                "is_potential": is_potential,
                "alert": alert_message,
                "conversation_ended": True,
                "all_done": True,
                "total_potential_leads": len(leads_state["potential_leads"]),
                "next_lead": False
            }
    
    return {
        "success": True,
        "message": ai_response,
        "is_potential": is_potential,
        "alert": alert_message,
        "conversation_ended": conversation_ended,
        "next_lead": leads_state["current_index"] < len(leads_state["leads"]),
        "messages_so_far": user_message_count
    }


async def skip_lead() -> dict:
    """Skip current lead and move to next."""
    leads_state["current_index"] += 1
    return {
        "success": True,
        "next_lead": leads_state["current_index"] < len(leads_state["leads"])
    }


async def get_status() -> dict:
    """Get current status."""
    return {
        "leads_loaded": len(leads_state["leads"]),
        "current_index": leads_state["current_index"],
        "context_set": bool(leads_state["sales_context"]),
        "potential_leads": len(leads_state["potential_leads"])
    }


async def get_all_leads() -> list:
    """Get all leads from database."""
    leads_collection = database.get_collection("leads")
    leads = await leads_collection.find().sort("created_at", -1).to_list(100)
    
    for lead in leads:
        lead["_id"] = str(lead["_id"])
    
    return leads


async def get_potential_leads() -> list:
    """Get all potential (qualified) leads."""
    leads_collection = database.get_collection("leads")
    leads = await leads_collection.find({"is_potential": True}).to_list(100)
    
    for lead in leads:
        lead["_id"] = str(lead["_id"])
    
    return leads


async def generate_report() -> dict:
    """Generate potential leads report."""
    potential = leads_state["potential_leads"]
    
    return {
        "success": True,
        "total_potential_leads": len(potential),
        "leads": potential,
        "message": f"Found {len(potential)} potential leads"
    }
