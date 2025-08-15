from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional

class LLMAdapter(ABC):
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.connected = False
        
    @abstractmethod
    async def connect(self) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    async def start_task(self, prompt: str, config: dict) -> dict:
        pass
    
    @abstractmethod
    async def send_message(self, message: str) -> AsyncIterator[str]:
        pass
    
    @abstractmethod
    async def execute_tool(self, tool: str, params: dict) -> dict:
        pass
    
    @abstractmethod
    async def cancel_task(self) -> bool:
        pass
    
    @abstractmethod
    async def get_status(self) -> dict:
        pass