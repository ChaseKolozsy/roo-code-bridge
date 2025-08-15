from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from api.auth import get_current_user

router = APIRouter()

class TaskRequest(BaseModel):
    provider: str = "roo-code"
    prompt: str
    config: Optional[Dict[str, Any]] = {}

class TaskResponse(BaseModel):
    task_id: str
    status: str
    provider: str

@router.post("/", response_model=TaskResponse)
async def create_task(request: TaskRequest, user: str = Depends(get_current_user)):
    # This will be connected to the WebSocket manager in main.py
    # For now, return a placeholder response
    return TaskResponse(
        task_id="task-123",
        status="started",
        provider=request.provider
    )

@router.delete("/{task_id}")
async def cancel_task(task_id: str, user: str = Depends(get_current_user)):
    return {"status": "cancelled", "task_id": task_id}

@router.post("/{task_id}/resume")
async def resume_task(task_id: str, user: str = Depends(get_current_user)):
    return {"status": "resumed", "task_id": task_id}

@router.post("/{task_id}/close")
async def close_task(task_id: str, user: str = Depends(get_current_user)):
    return {"status": "closed", "task_id": task_id}

@router.get("/{task_id}/status")
async def get_task_status(task_id: str, user: str = Depends(get_current_user)):
    return {"task_id": task_id, "status": "running", "progress": 50}