from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from api.auth import get_current_user

router = APIRouter()

class ProviderConfig(BaseModel):
    name: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    model: Optional[str] = None

class AutoApprovalConfig(BaseModel):
    enabled: bool = False
    patterns: List[str] = []
    max_file_size: int = 10000

class CommandConfig(BaseModel):
    allowed: List[str] = []
    denied: List[str] = []

@router.get("/providers")
async def get_providers(user: str = Depends(get_current_user)):
    return {
        "providers": [
            {"name": "roo-code", "status": "available"},
            {"name": "claude-code", "status": "not_configured"},
            {"name": "qwen-code", "status": "not_configured"}
        ]
    }

@router.post("/providers")
async def configure_provider(config: ProviderConfig, user: str = Depends(get_current_user)):
    return {"status": "configured", "provider": config.name}

@router.post("/model")
async def select_model(model: str, provider: str = "roo-code", user: str = Depends(get_current_user)):
    return {"status": "selected", "model": model, "provider": provider}

@router.post("/instructions")
async def set_instructions(instructions: str, user: str = Depends(get_current_user)):
    return {"status": "updated", "instructions": instructions[:100] + "..."}

@router.post("/auto-approval")
async def configure_auto_approval(config: AutoApprovalConfig, user: str = Depends(get_current_user)):
    return {"status": "configured", "auto_approval": config.dict()}

@router.post("/commands")
async def configure_commands(config: CommandConfig, user: str = Depends(get_current_user)):
    return {"status": "configured", "commands": config.dict()}