"""
Workload Distribution Agent - Manages staff task assignment and workload balancing.
"""

from langchain_core.messages import AIMessage
from agents.state import AgentState
from database.connection import database
from database.models import TaskStatus, BottleneckType, BottleneckSeverity
from datetime import datetime
import uuid


async def workload_agent(state: AgentState) -> AgentState:
    """
    Handle workload distribution and task assignment.
    """
    context = state.get("context", {})
    action = context.get("workload_action", "analyze")
    
    if action == "assign":
        result = await assign_task_to_staff(state)
    elif action == "rebalance":
        result = await rebalance_workload()
    else:
        result = await analyze_workload()
    
    state["final_response"] = result
    state["messages"] = state.get("messages", []) + [AIMessage(content=result)]
    
    return state


async def assign_task_to_staff(state: AgentState) -> str:
    """Assign a task to the most available staff member."""
    context = state.get("context", {})
    task_description = context.get("task_description", "Process order")
    order_id = context.get("order_id")
    priority = context.get("priority", 1)
    
    staff_collection = database.get_collection("staff")
    
    # Find available staff member with lowest workload
    available_staff = await staff_collection.find({
        "is_available": True,
        "$expr": {"$lt": ["$current_workload", "$max_workload"]}
    }).sort("current_workload", 1).to_list(10)
    
    if not available_staff:
        # Check workload imbalance bottleneck
        await check_workload_bottleneck()
        return "No available staff. All team members are at capacity."
    
    # Assign to the staff member with lowest workload
    selected_staff = available_staff[0]
    task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
    
    task = {
        "task_id": task_id,
        "description": task_description,
        "order_id": order_id,
        "status": TaskStatus.PENDING.value,
        "priority": priority,
        "assigned_at": datetime.utcnow()
    }
    
    await staff_collection.update_one(
        {"_id": selected_staff["_id"]},
        {
            "$push": {"assigned_tasks": task},
            "$inc": {"current_workload": 1}
        }
    )
    
    return f"Task {task_id} assigned to {selected_staff.get('name')} ({selected_staff.get('role')})"


async def analyze_workload() -> str:
    """Analyze current workload distribution."""
    staff_collection = database.get_collection("staff")
    
    staff_members = await staff_collection.find().to_list(100)
    
    if not staff_members:
        return "No staff members found."
    
    total_capacity = sum(s.get("max_workload", 10) for s in staff_members)
    total_current = sum(s.get("current_workload", 0) for s in staff_members)
    
    utilization = (total_current / total_capacity * 100) if total_capacity > 0 else 0
    
    lines = ["Workload Distribution Analysis:", ""]
    
    for staff in staff_members:
        name = staff.get("name")
        current = staff.get("current_workload", 0)
        max_wl = staff.get("max_workload", 10)
        staff_util = (current / max_wl * 100) if max_wl > 0 else 0
        status = "🟢" if staff_util < 70 else "🟡" if staff_util < 90 else "🔴"
        lines.append(f"{status} {name}: {current}/{max_wl} tasks ({staff_util:.0f}%)")
    
    lines.append("")
    lines.append(f"Overall Utilization: {utilization:.1f}%")
    
    # Check for imbalances
    await check_workload_bottleneck()
    
    return "\n".join(lines)


async def rebalance_workload() -> str:
    """Rebalance tasks across staff members."""
    staff_collection = database.get_collection("staff")
    
    staff_members = await staff_collection.find({"is_available": True}).to_list(100)
    
    if len(staff_members) < 2:
        return "Not enough staff to rebalance."
    
    # Find overloaded and underloaded staff
    avg_workload = sum(s.get("current_workload", 0) for s in staff_members) / len(staff_members)
    
    overloaded = [s for s in staff_members if s.get("current_workload", 0) > avg_workload + 2]
    underloaded = [s for s in staff_members if s.get("current_workload", 0) < avg_workload - 2]
    
    if not overloaded or not underloaded:
        return "Workload is already balanced."
    
    tasks_moved = 0
    
    for over_staff in overloaded:
        pending_tasks = [t for t in over_staff.get("assigned_tasks", []) 
                        if t.get("status") == TaskStatus.PENDING.value]
        
        for task in pending_tasks[:2]:  # Move up to 2 tasks
            if not underloaded:
                break
            
            under_staff = underloaded[0]
            
            # Remove from overloaded
            await staff_collection.update_one(
                {"_id": over_staff["_id"]},
                {
                    "$pull": {"assigned_tasks": {"task_id": task["task_id"]}},
                    "$inc": {"current_workload": -1}
                }
            )
            
            # Add to underloaded
            await staff_collection.update_one(
                {"_id": under_staff["_id"]},
                {
                    "$push": {"assigned_tasks": task},
                    "$inc": {"current_workload": 1}
                }
            )
            
            tasks_moved += 1
            
            # Update underloaded list
            under_staff["current_workload"] = under_staff.get("current_workload", 0) + 1
            if under_staff["current_workload"] >= avg_workload:
                underloaded.remove(under_staff)
    
    return f"Workload rebalanced. {tasks_moved} tasks redistributed."


async def check_workload_bottleneck():
    """Check and create bottleneck for workload issues."""
    staff_collection = database.get_collection("staff")
    bottlenecks_collection = database.get_collection("bottlenecks")
    
    staff_members = await staff_collection.find().to_list(100)
    
    # Check for general overload
    total_capacity = sum(s.get("max_workload", 10) for s in staff_members)
    total_current = sum(s.get("current_workload", 0) for s in staff_members)
    utilization = (total_current / total_capacity * 100) if total_capacity > 0 else 0
    
    # Check for imbalance
    workloads = [s.get("current_workload", 0) for s in staff_members]
    max_wl = max(workloads) if workloads else 0
    min_wl = min(workloads) if workloads else 0
    
    if utilization > 90 or (max_wl - min_wl > 5):
        existing = await bottlenecks_collection.find_one({
            "type": BottleneckType.WORKLOAD_IMBALANCE.value,
            "is_resolved": False
        })
        
        if not existing:
            severity = BottleneckSeverity.HIGH if utilization > 95 else BottleneckSeverity.MEDIUM
            
            overloaded_names = [s.get("name") for s in staff_members 
                               if s.get("current_workload", 0) >= s.get("max_workload", 10) - 1]
            
            bottleneck = {
                "type": BottleneckType.WORKLOAD_IMBALANCE.value,
                "severity": severity.value,
                "title": "Staff Workload Imbalance",
                "description": f"Overall utilization at {utilization:.0f}%. Some staff may be overloaded.",
                "affected_resources": overloaded_names,
                "suggested_actions": [
                    "Rebalance tasks across team members",
                    "Consider hiring temporary staff",
                    "Delay non-urgent tasks"
                ],
                "is_resolved": False,
                "detected_at": datetime.utcnow()
            }
            
            await bottlenecks_collection.insert_one(bottleneck)


async def complete_task(staff_id: str, task_id: str) -> str:
    """Mark a task as completed."""
    staff_collection = database.get_collection("staff")
    
    result = await staff_collection.update_one(
        {"_id": staff_id, "assigned_tasks.task_id": task_id},
        {
            "$set": {
                "assigned_tasks.$.status": TaskStatus.COMPLETED.value,
                "assigned_tasks.$.completed_at": datetime.utcnow()
            },
            "$inc": {"current_workload": -1}
        }
    )
    
    if result.modified_count > 0:
        return f"Task {task_id} marked as completed."
    return f"Task {task_id} not found."


async def get_workload_distribution() -> list:
    """Get workload distribution for all staff."""
    staff_collection = database.get_collection("staff")
    
    staff_members = await staff_collection.find().to_list(100)
    
    distribution = []
    for staff in staff_members:
        current = staff.get("current_workload", 0)
        max_wl = staff.get("max_workload", 10)
        utilization = (current / max_wl * 100) if max_wl > 0 else 0
        
        distribution.append({
            "staff_id": str(staff["_id"]),
            "staff_name": staff.get("name"),
            "role": staff.get("role"),
            "current_tasks": current,
            "max_capacity": max_wl,
            "utilization_percent": round(utilization, 1)
        })
    
    return distribution
