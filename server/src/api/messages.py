from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from api.auth import get_current_user

router = APIRouter()

class MessageRequest(BaseModel):
    content: str
    task_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class MessageResponse(BaseModel):
    id: str
    content: str
    timestamp: str
    role: str

@router.post("/", response_model=MessageResponse)
async def send_message(request: MessageRequest, user: str = Depends(get_current_user)):
    from datetime import datetime
    return MessageResponse(
        id="msg-123",
        content=f"Processing: {request.content[:50]}...",
        timestamp=datetime.utcnow().isoformat(),
        role="assistant"
    )

@router.post("/followup")
async def send_followup(request: MessageRequest, user: str = Depends(get_current_user)):
    return {
        "status": "sent",
        "message_id": "msg-124",
        "followup": True
    }

@router.get("/history")
async def get_message_history(task_id: Optional[str] = None, limit: int = 50, user: str = Depends(get_current_user)):
    return {
        "messages": [],
        "total": 0,
        "task_id": task_id
    }