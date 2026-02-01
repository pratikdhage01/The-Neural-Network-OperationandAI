"""
Leads API Routes - Endpoints for leads communication system.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from agents.leads_agent import (
    set_sales_context,
    load_leads,
    get_demo_leads,
    start_conversation,
    send_message,
    skip_lead,
    get_status,
    get_all_leads,
    get_potential_leads,
    generate_report
)


router = APIRouter(prefix="/api/leads", tags=["leads"])


class SalesContextRequest(BaseModel):
    context: str


class LoadLeadsRequest(BaseModel):
    clients: List[dict]


class SendMessageRequest(BaseModel):
    message: str


@router.post("/context")
async def api_set_context(request: SalesContextRequest):
    """Set the sales context for the agent."""
    result = await set_sales_context(request.context)
    return result


@router.post("/load")
async def api_load_leads(request: LoadLeadsRequest):
    """Load leads from request."""
    result = await load_leads(request.clients)
    return result


@router.post("/load-demo")
async def api_load_demo():
    """Load demo leads."""
    demo_leads = await get_demo_leads()
    result = await load_leads(demo_leads)
    return result


@router.post("/start")
async def api_start_conversation():
    """Start conversation with current lead."""
    result = await start_conversation()
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/{lead_id}/message")
async def api_send_message(lead_id: str, request: SendMessageRequest):
    """Send a message in the conversation."""
    result = await send_message(lead_id, request.message)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/skip")
async def api_skip_lead():
    """Skip current lead."""
    result = await skip_lead()
    return result


@router.get("/status")
async def api_get_status():
    """Get current status."""
    return await get_status()


@router.get("")
async def api_get_leads():
    """Get all leads."""
    return await get_all_leads()


@router.get("/potential")
async def api_get_potential():
    """Get potential (qualified) leads."""
    return await get_potential_leads()


@router.post("/report")
async def api_generate_report():
    """Generate potential leads report."""
    return await generate_report()
