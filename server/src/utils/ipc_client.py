import asyncio
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class IPCClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 9999):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.connected = False
        self.message_id = 0
        
    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self.connected = True
            logger.info(f"Connected to IPC server at {self.host}:{self.port}")
            
            welcome = await self.read_message()
            logger.info(f"Server welcome: {welcome}")
            
        except Exception as e:
            logger.error(f"Failed to connect to IPC server: {e}")
            self.connected = False
            raise
    
    def disconnect(self):
        if self.writer:
            self.writer.close()
        self.connected = False
        logger.info("Disconnected from IPC server")
    
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        if not self.connected or not self.writer:
            raise Exception("Not connected to IPC server")
        
        self.message_id += 1
        message["id"] = str(self.message_id)
        
        try:
            message_str = json.dumps(message) + "\n"
            self.writer.write(message_str.encode())
            await self.writer.drain()
            
            response = await self.read_message()
            return response
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    async def read_message(self) -> Dict[str, Any]:
        if not self.reader:
            raise Exception("Not connected to IPC server")
        
        try:
            data = await self.reader.readline()
            if not data:
                raise Exception("Connection closed by server")
            
            message_str = data.decode().strip()
            return json.loads(message_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to read message: {e}")
            raise