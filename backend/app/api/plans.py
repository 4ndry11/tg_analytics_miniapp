from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/plans", tags=["plans"])

# In-memory storage for plans (without database)
# In future, replace with database storage
plans_storage = []


@router.get("/")
async def get_plans():
    """Get all plans"""
    return {"plans": plans_storage}


@router.post("/")
async def create_plan(
    manager_id: str,
    metric_type: str,
    period_type: str,
    target_value: float,
    start_date: str,
    end_date: str
):
    """Create a new plan"""
    plan = {
        "id": len(plans_storage) + 1,
        "manager_id": manager_id,
        "metric_type": metric_type,  # 'leads', 'sales', 'conversion'
        "period_type": period_type,  # 'daily', 'weekly', 'monthly'
        "target_value": target_value,
        "start_date": start_date,
        "end_date": end_date,
        "created_at": datetime.now().isoformat()
    }

    plans_storage.append(plan)

    return {"plan": plan}


@router.put("/{plan_id}")
async def update_plan(
    plan_id: int,
    target_value: float
):
    """Update a plan"""
    for plan in plans_storage:
        if plan["id"] == plan_id:
            plan["target_value"] = target_value
            plan["updated_at"] = datetime.now().isoformat()
            return {"plan": plan}

    raise HTTPException(status_code=404, detail="Plan not found")


@router.delete("/{plan_id}")
async def delete_plan(plan_id: int):
    """Delete a plan"""
    global plans_storage
    plans_storage = [p for p in plans_storage if p["id"] != plan_id]
    return {"status": "deleted"}
