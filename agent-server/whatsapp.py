"""
WhatsApp Bot Integration using Twilio
Routes WhatsApp messages to the existing agent system
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from agents.graph import run_agent
from database.connection import database
import traceback

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    ProfileName: str = Form(None),
    MessageSid: str = Form(None)
):
    """
    Twilio WhatsApp webhook endpoint.
    Receives messages from WhatsApp users and responds via agent system.
    
    From: WhatsApp number (e.g., whatsapp:+1234567890)
    Body: Message text
    ProfileName: WhatsApp user's name
    MessageSid: Twilio message ID
    """
    try:
        # Extract phone number from WhatsApp format
        phone_number = From.replace("whatsapp:", "")
        
        # Use phone number as conversation ID for continuity
        conversation_id = f"wa_{phone_number.replace('+', '')}"
        
        print(f"📱 WhatsApp message from {ProfileName or phone_number}: {Body}")
        
        # Process message through agent system
        result = await run_agent(
            message=Body,
            conversation_id=conversation_id,
            conversation_type="consumer"
        )
        
        # Create Twilio response
        response = MessagingResponse()
        response.message(result["response"])
        
        print(f"🤖 Agent response: {result['response'][:100]}...")
        
        # Return TwiML response
        return Response(
            content=str(response),
            media_type="application/xml"
        )
        
    except Exception as e:
        print(f"❌ WhatsApp webhook error: {e}")
        traceback.print_exc()
        
        # Send error message to user
        response = MessagingResponse()
        response.message("Sorry, I encountered an error. Please try again in a moment.")
        
        return Response(
            content=str(response),
            media_type="application/xml"
        )


@router.get("/status")
async def whatsapp_status():
    """Health check for WhatsApp integration."""
    return {
        "status": "active",
        "service": "WhatsApp Bot via Twilio",
        "webhook_endpoint": "/whatsapp/webhook"
    }