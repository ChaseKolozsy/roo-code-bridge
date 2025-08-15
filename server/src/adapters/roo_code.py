import asyncio
import json
from typing import AsyncIterator, Dict, Any, Optional
from adapters.base import LLMAdapter
from utils.ipc_client import IPCClient
import logging

logger = logging.getLogger(__name__)

class RooCodeAdapter(LLMAdapter):
    def __init__(self, client_id: str, host: str = "127.0.0.1", port: int = 9999):
        super().__init__(client_id)
        self.host = host
        self.port = port
        self.ipc_client: Optional[IPCClient] = None
        self.current_task_id: Optional[str] = None
        
    async def connect(self) -> bool:
        try:
            self.ipc_client = IPCClient(self.host, self.port)
            await self.ipc_client.connect()
            self.connected = True
            logger.info(f"RooCodeAdapter connected for client {self.client_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to IPC server: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        if self.ipc_client:
            self.ipc_client.disconnect()
        self.connected = False
        logger.info(f"RooCodeAdapter disconnected for client {self.client_id}")
    
    async def start_task(self, prompt: str, config: dict) -> dict:
        if not self.connected or not self.ipc_client:
            raise Exception("Not connected to IPC server")
        
        try:
            response = await self.ipc_client.send_message({
                "type": "task.start",
                "data": {
                    "prompt": prompt,
                    "config": config
                }
            })
            
            if response.get("type") == "task.started":
                self.current_task_id = response.get("data", {}).get("task_id")
                return response.get("data", {})
            else:
                raise Exception(f"Unexpected response: {response}")
                
        except Exception as e:
            logger.error(f"Failed to start task: {e}")
            raise
    
    async def send_message(self, message: str) -> AsyncIterator[str]:
        if not self.connected or not self.ipc_client:
            raise Exception("Not connected to IPC server")
        
        try:
            response = await self.ipc_client.send_message({
                "type": "message.send",
                "data": {
                    "content": message,
                    "task_id": self.current_task_id
                }
            })
            
            if response.get("type") == "message.stream":
                content = response.get("data", {}).get("content", "")
                for chunk in content:
                    yield chunk
            elif response.get("type") == "error":
                raise Exception(response.get("data", {}).get("message", "Unknown error"))
                
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    async def execute_tool(self, tool: str, params: dict) -> dict:
        if not self.connected or not self.ipc_client:
            raise Exception("Not connected to IPC server")
        
        try:
            response = await self.ipc_client.send_message({
                "type": "tool.execute",
                "data": {
                    "tool": tool,
                    "params": params,
                    "task_id": self.current_task_id
                }
            })
            
            if response.get("type") == "tool.result":
                return response.get("data", {})
            elif response.get("type") == "error":
                raise Exception(response.get("data", {}).get("message", "Unknown error"))
            else:
                raise Exception(f"Unexpected response: {response}")
                
        except Exception as e:
            logger.error(f"Failed to execute tool: {e}")
            raise
    
    async def cancel_task(self) -> bool:
        if not self.connected or not self.ipc_client:
            return False
        
        try:
            response = await self.ipc_client.send_message({
                "type": "task.cancel",
                "data": {
                    "task_id": self.current_task_id
                }
            })
            
            if response.get("type") == "task.cancelled":
                self.current_task_id = None
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel task: {e}")
            return False
    
    async def get_status(self) -> dict:
        return {
            "connected": self.connected,
            "provider": "roo-code",
            "current_task_id": self.current_task_id,
            "host": self.host,
            "port": self.port
        }