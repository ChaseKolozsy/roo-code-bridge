"""Message type definitions for Roo-Code bridge communication."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel


class ClineAsk(str, Enum):
    """Approval request types from Roo-Code."""
    FOLLOWUP = "followup"
    COMMAND = "command"
    COMMAND_OUTPUT = "command_output"
    COMPLETION_RESULT = "completion_result"
    TOOL = "tool"
    API_REQ_FAILED = "api_req_failed"
    RESUME_TASK = "resume_task"
    BROWSER_ACTION_LAUNCH = "browser_action_launch"
    USE_MCP_SERVER = "use_mcp_server"
    AUTO_APPROVAL_MAX_REQ_REACHED = "auto_approval_max_req_reached"


class ClineSay(str, Enum):
    """Status message types from Roo-Code."""
    TEXT = "text"
    REASONING = "reasoning"
    ERROR = "error"
    COMMAND_OUTPUT = "command_output"
    API_REQ_STARTED = "api_req_started"
    API_REQ_FINISHED = "api_req_finished"
    TOOL_PROGRESS = "tool_progress"
    CODEBASE_SEARCH_RESULT = "codebase_search_result"
    COMPLETION_RESULT = "completion_result"
    USER_FEEDBACK = "user_feedback"
    USER_FEEDBACK_DIFF = "user_feedback_diff"
    API_REQ_RETRIED = "api_req_retried"
    RESUMING_TASK = "resuming_task"
    RESUME_COMPLETED = "resume_completed"
    MEMORY_UPDATED = "memory_updated"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_ABORTED = "task_aborted"
    TASK_PAUSED = "task_paused"
    TASK_UNPAUSED = "task_unpaused"
    TASK_SPAWNED = "task_spawned"


class RooCodeMessage(BaseModel):
    """Message from Roo-Code to bridge."""
    type: Union[ClineAsk, ClineSay]
    data: Dict[str, Any]
    timestamp: str
    task_id: Optional[str] = None
    

class WebviewMessage(BaseModel):
    """Message from web UI to bridge."""
    type: str  # newTask, askResponse, saveApiConfiguration, etc.
    data: Optional[Dict[str, Any]] = {}
    images: Optional[List[Dict[str, str]]] = []
    

class ImageData(BaseModel):
    """Image data structure."""
    type: str  # "base64", "url", "path"
    data: str  # base64 string, URL, or file path
    mime_type: str  # "image/png", "image/jpeg", etc.
    name: Optional[str] = None
    size: Optional[int] = None


class ProviderConfig(BaseModel):
    """Provider configuration settings."""
    provider: str  # "anthropic", "openai", "gemini", "ollama", etc.
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    context_length: Optional[int] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    custom_instructions: Optional[str] = None
    

class ApprovalRequest(BaseModel):
    """Approval request sent to web UI."""
    approval_id: str
    ask_type: ClineAsk
    data: Dict[str, Any]
    options: Optional[List[str]] = None  # For multiple choice questions
    allow_text_response: Optional[bool] = True
    

class ApprovalResponse(BaseModel):
    """User's response to approval request."""
    approval_id: str
    approved: Optional[bool] = None  # For yes/no questions
    response: Optional[str] = None  # For text/choice responses
    modifications: Optional[Dict[str, Any]] = None