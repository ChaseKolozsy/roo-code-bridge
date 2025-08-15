from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from api.auth import get_current_user

router = APIRouter()

class ExecuteRequest(BaseModel):
    command: str
    cwd: Optional[str] = None
    timeout: Optional[int] = 30

class FileRequest(BaseModel):
    path: str
    content: Optional[str] = None

class SearchRequest(BaseModel):
    pattern: str
    path: Optional[str] = "."
    include: Optional[List[str]] = []
    exclude: Optional[List[str]] = []

class DiffRequest(BaseModel):
    file_path: str
    diff: str

@router.post("/execute")
async def execute_command(request: ExecuteRequest, user: str = Depends(get_current_user)):
    return {
        "status": "executed",
        "output": f"Command '{request.command}' executed",
        "exit_code": 0
    }

@router.post("/read")
async def read_file(request: FileRequest, user: str = Depends(get_current_user)):
    return {
        "status": "success",
        "path": request.path,
        "content": "File content here..."
    }

@router.post("/write")
async def write_file(request: FileRequest, user: str = Depends(get_current_user)):
    if not request.content:
        raise HTTPException(status_code=400, detail="Content is required")
    return {
        "status": "written",
        "path": request.path,
        "size": len(request.content)
    }

@router.post("/diff")
async def apply_diff(request: DiffRequest, user: str = Depends(get_current_user)):
    return {
        "status": "applied",
        "file_path": request.file_path,
        "changes": 5
    }

@router.post("/search")
async def search_files(request: SearchRequest, user: str = Depends(get_current_user)):
    return {
        "status": "completed",
        "pattern": request.pattern,
        "matches": [
            {"file": "example.py", "line": 10, "content": "matched line"}
        ]
    }

@router.post("/list")
async def list_files(path: str = ".", user: str = Depends(get_current_user)):
    return {
        "status": "success",
        "path": path,
        "files": ["file1.py", "file2.js", "README.md"]
    }

@router.post("/todo")
async def update_todos(todos: List[Dict[str, Any]], user: str = Depends(get_current_user)):
    return {
        "status": "updated",
        "count": len(todos)
    }