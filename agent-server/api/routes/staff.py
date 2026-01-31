"""
Staff API routes - Staff and workload management.
"""

from fastapi import APIRouter, HTTPException
from database.connection import database
from database.models import StaffCreate, TaskStatus
from agents.workload_agent import get_workload_distribution, complete_task
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/staff", tags=["Staff"])


@router.get("")
async def list_staff():
    """List all staff members."""
    staff_collection = database.get_collection("staff")
    
    staff = await staff_collection.find().sort("name", 1).to_list(100)
    
    # Convert ObjectId to string
    for s in staff:
        s["_id"] = str(s["_id"])
    
    return staff


@router.get("/workload")
async def get_workload():
    """Get workload distribution across staff."""
    distribution = await get_workload_distribution()
    return distribution


@router.get("/{staff_id}")
async def get_staff_member(staff_id: str):
    """Get staff member details."""
    staff_collection = database.get_collection("staff")
    
    try:
        staff = await staff_collection.find_one({"_id": ObjectId(staff_id)})
    except Exception:
        staff = None
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    staff["_id"] = str(staff["_id"])
    return staff


@router.post("")
async def add_staff(staff: StaffCreate):
    """Add a new staff member."""
    staff_collection = database.get_collection("staff")
    
    staff_doc = staff.model_dump()
    staff_doc["created_at"] = datetime.utcnow()
    staff_doc["is_available"] = True
    staff_doc["current_workload"] = 0
    staff_doc["assigned_tasks"] = []
    
    result = await staff_collection.insert_one(staff_doc)
    
    return {"id": str(result.inserted_id), "message": "Staff member added successfully"}


@router.put("/{staff_id}")
async def update_staff(staff_id: str, updates: dict):
    """Update staff member details."""
    staff_collection = database.get_collection("staff")
    
    try:
        result = await staff_collection.update_one(
            {"_id": ObjectId(staff_id)},
            {"$set": updates}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid staff ID")
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    return {"message": "Staff member updated successfully"}


@router.post("/{staff_id}/assign")
async def assign_task(staff_id: str, description: str, order_id: str = None, priority: int = 1):
    """Assign a task to staff member."""
    staff_collection = database.get_collection("staff")
    
    import uuid
    task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
    
    task = {
        "task_id": task_id,
        "description": description,
        "order_id": order_id,
        "status": TaskStatus.PENDING.value,
        "priority": priority,
        "assigned_at": datetime.utcnow()
    }
    
    try:
        result = await staff_collection.update_one(
            {"_id": ObjectId(staff_id)},
            {
                "$push": {"assigned_tasks": task},
                "$inc": {"current_workload": 1}
            }
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid staff ID")
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    return {"task_id": task_id, "message": f"Task assigned to staff member"}


@router.put("/{staff_id}/tasks/{task_id}/complete")
async def complete_staff_task(staff_id: str, task_id: str):
    """Mark a task as completed."""
    result = await complete_task(staff_id, task_id)
    return {"message": result}


@router.put("/{staff_id}/tasks/{task_id}/status")
async def update_task_status(staff_id: str, task_id: str, status: str):
    """Update task status."""
    staff_collection = database.get_collection("staff")
    
    try:
        task_status = TaskStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    update_data = {
        "assigned_tasks.$.status": task_status.value
    }
    
    if task_status == TaskStatus.COMPLETED:
        update_data["assigned_tasks.$.completed_at"] = datetime.utcnow()
    
    try:
        result = await staff_collection.update_one(
            {"_id": ObjectId(staff_id), "assigned_tasks.task_id": task_id},
            {"$set": update_data}
        )
        
        if task_status == TaskStatus.COMPLETED:
            await staff_collection.update_one(
                {"_id": ObjectId(staff_id)},
                {"$inc": {"current_workload": -1}}
            )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid staff ID or task ID")
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": f"Task status updated to {status}"}


@router.delete("/{staff_id}")
async def delete_staff(staff_id: str):
    """Remove a staff member."""
    staff_collection = database.get_collection("staff")
    
    try:
        result = await staff_collection.delete_one({"_id": ObjectId(staff_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid staff ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    return {"message": "Staff member removed successfully"}
