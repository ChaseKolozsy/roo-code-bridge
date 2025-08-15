from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from typing import Dict, Optional
from datetime import datetime

from models.session import SessionManager, Session
from models.database import init_db
from api.auth import get_current_user, authenticate_user
from api.tasks import router as tasks_router
from api.config import router as config_router
from api.tools import router as tools_router
from api.messages import router as messages_router
from adapters.base import LLMAdapter
from adapters.roo_code import RooCodeAdapter
from utils.ipc_client import IPCClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await SessionManager.cleanup_all()

app = FastAPI(title="Roo-Code Bridge", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
app.include_router(config_router, prefix="/api/config", tags=["config"])
app.include_router(tools_router, prefix="/api/tools", tags=["tools"])
app.include_router(messages_router, prefix="/api/messages", tags=["messages"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, Session] = {}
        self.adapters: Dict[str, LLMAdapter] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        session = await SessionManager.create_session(client_id)
        self.sessions[client_id] = session
        
        # Try to connect adapter but don't fail if IPC server is not available
        try:
            adapter = RooCodeAdapter(client_id)
            if await adapter.connect():
                self.adapters[client_id] = adapter
                logger.info(f"Client {client_id} connected with adapter")
            else:
                logger.warning(f"Client {client_id} connected but adapter unavailable")
        except Exception as e:
            logger.warning(f"Client {client_id} connected without adapter: {e}")
        
        logger.info(f"Client {client_id} connected")
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.sessions:
            SessionManager.close_session(self.sessions[client_id].id)
            del self.sessions[client_id]
        if client_id in self.adapters:
            self.adapters[client_id].disconnect()
            del self.adapters[client_id]
        logger.info(f"Client {client_id} disconnected")
        
    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
            
    async def broadcast(self, message: dict, exclude: Optional[str] = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude:
                await connection.send_json(message)
                
    async def handle_message(self, client_id: str, message: dict):
        message_type = message.get("type")
        data = message.get("data", {})
        
        # Handle ping message
        if message_type == "ping":
            await self.send_message(client_id, {
                "type": "pong",
                "data": data
            })
            return
        
        if client_id not in self.adapters:
            await self.send_message(client_id, {
                "type": "error",
                "data": {"message": "No adapter connected (VS Code extension not running)"}
            })
            return
            
        adapter = self.adapters[client_id]
        
        try:
            if message_type == "task.start":
                result = await adapter.start_task(data.get("prompt"), data.get("config", {}))
                await self.send_message(client_id, {
                    "type": "task.started",
                    "data": result
                })
                
            elif message_type == "message.send":
                async for chunk in adapter.send_message(data.get("content")):
                    await self.send_message(client_id, {
                        "type": "message.stream",
                        "data": {"chunk": chunk}
                    })
                    
            elif message_type == "tool.execute":
                result = await adapter.execute_tool(data.get("tool"), data.get("params", {}))
                await self.send_message(client_id, {
                    "type": "tool.result",
                    "data": result
                })
                
            else:
                await self.send_message(client_id, {
                    "type": "error",
                    "data": {"message": f"Unknown message type: {message_type}"}
                })
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_message(client_id, {
                "type": "error",
                "data": {"message": str(e)}
            })

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await manager.handle_message(client_id, message)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(client_id)

@app.get("/")
async def root():
    return {"message": "Roo-Code Bridge API", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_sessions": len(manager.sessions)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)