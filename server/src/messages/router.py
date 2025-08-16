"""Message router for bridging communication between web UI and Roo-Code."""

import uuid
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from messages.types import (
    WebviewMessage, RooCodeMessage, ClineAsk, ClineSay,
    ApprovalRequest, ApprovalResponse, ImageData
)
from config.provider_manager import ProviderManager

logger = logging.getLogger(__name__)


class MessageRouter:
    """Routes messages between web UI and Roo-Code."""
    
    def __init__(self, provider_manager: ProviderManager):
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.provider_manager = provider_manager
        self.websocket_manager = None  # Will be set by main
        self.ipc_clients = {}  # client_id -> IPC connection
        
    def set_websocket_manager(self, manager):
        """Set the WebSocket manager for sending messages to web clients."""
        self.websocket_manager = manager
        
    def register_ipc_client(self, client_id: str, ipc_connection):
        """Register an IPC connection for a client."""
        self.ipc_clients[client_id] = ipc_connection
        logger.info(f"Registered IPC client for {client_id}")
        
    def unregister_ipc_client(self, client_id: str):
        """Unregister an IPC connection for a client."""
        if client_id in self.ipc_clients:
            del self.ipc_clients[client_id]
            logger.info(f"Unregistered IPC client for {client_id}")
            
    async def route_from_web(self, client_id: str, message: WebviewMessage) -> Dict[str, Any]:
        """Route message from web UI to Roo-Code."""
        
        logger.debug(f"Routing from web: {client_id} -> {message.type}")
        
        if message.type == "newTask":
            # Start new task in Roo-Code
            task_data = {
                "type": "newTask",
                "prompt": message.data.get("prompt", ""),
                "configuration": {}
            }
            
            # Apply provider config if specified
            if "provider" in message.data or "model" in message.data:
                config = await self.provider_manager.set_provider(client_id, message.data)
                task_data["configuration"] = config["data"]
                
            # Include images if provided
            if message.images:
                task_data["images"] = await self.process_images(message.images)
                
            await self.send_to_roocode(client_id, task_data)
            
            return {"status": "task_started", "client_id": client_id}
            
        elif message.type == "askResponse":
            # User responded to approval request
            approval_id = message.data.get("approval_id")
            response = ApprovalResponse(
                approval_id=approval_id,
                approved=message.data.get("approved"),
                response=message.data.get("response"),
                modifications=message.data.get("modifications")
            )
            return await self.handle_approval_response(client_id, response)
            
        elif message.type == "saveApiConfiguration":
            # Update provider settings in Roo-Code
            config_msg = await self.provider_manager.set_provider(client_id, message.data)
            await self.send_to_roocode(client_id, config_msg)
            return {"status": "config_updated", "provider": message.data.get("provider")}
            
        elif message.type == "cancelTask":
            # Cancel current task
            await self.send_to_roocode(client_id, {
                "type": "cancelTask",
                "taskId": message.data.get("taskId")
            })
            return {"status": "task_cancelled"}
            
        elif message.type == "resumeTask":
            # Resume a paused task
            await self.send_to_roocode(client_id, {
                "type": "resumeTask",
                "taskId": message.data.get("taskId")
            })
            return {"status": "task_resumed"}
            
        else:
            # Forward other messages as-is
            await self.send_to_roocode(client_id, {
                "type": message.type,
                "data": message.data
            })
            return {"status": "forwarded", "type": message.type}
            
    async def route_from_roocode(self, client_id: str, message: Dict[str, Any]) -> None:
        """Route message from Roo-Code to web UI."""
        
        logger.debug(f"Routing from Roo-Code: {client_id} <- {message.get('type')}")
        
        # Parse the message
        msg_type = message.get("type")
        msg_data = message.get("data", {})
        
        # Check if this is an ask (approval request) or say (status update)
        if msg_type == "ask":
            await self.handle_ask_message(client_id, msg_data)
        elif msg_type == "say":
            await self.handle_say_message(client_id, msg_data)
        elif msg_type == "event":
            await self.handle_event_message(client_id, msg_data)
        else:
            # Forward unknown messages as-is
            await self.send_to_web(client_id, message)
            
    async def handle_ask_message(self, client_id: str, data: Dict[str, Any]) -> None:
        """Handle approval request from Roo-Code."""
        
        ask_type = data.get("ask_type") or data.get("type")
        approval_id = str(uuid.uuid4())
        
        # Store approval request
        self.pending_approvals[approval_id] = {
            "client_id": client_id,
            "ask_type": ask_type,
            "data": data,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Format for web UI
        approval_request = ApprovalRequest(
            approval_id=approval_id,
            ask_type=ask_type,
            data=self.format_approval_data(ask_type, data)
        )
        
        # Handle multiple choice questions
        if ask_type == "followup" and "options" in data:
            approval_request.options = data["options"]
            approval_request.allow_text_response = data.get("allow_text_response", True)
            
        await self.send_to_web(client_id, {
            "type": "approval_required",
            "data": approval_request.dict()
        })
        
    async def handle_say_message(self, client_id: str, data: Dict[str, Any]) -> None:
        """Handle status update from Roo-Code."""
        
        say_type = data.get("say_type") or data.get("type")
        
        await self.send_to_web(client_id, {
            "type": "status_update",
            "say_type": say_type,
            "data": data
        })
        
    async def handle_event_message(self, client_id: str, data: Dict[str, Any]) -> None:
        """Handle event message from Roo-Code."""
        
        event_name = data.get("name")
        event_data = data.get("data", {})
        
        await self.send_to_web(client_id, {
            "type": "event",
            "event_name": event_name,
            "data": event_data
        })
        
    async def handle_approval_response(self, client_id: str, response: ApprovalResponse) -> Dict[str, Any]:
        """Handle user's response to an approval request."""
        
        approval = self.pending_approvals.get(response.approval_id)
        if not approval:
            logger.warning(f"Unknown approval ID: {response.approval_id}")
            return {"error": "Unknown approval ID"}
            
        # Send response back to Roo-Code
        await self.send_to_roocode(client_id, {
            "type": "askResponse",
            "data": {
                "approved": response.approved,
                "response": response.response,
                "modifications": response.modifications,
                "ask_type": approval["ask_type"]
            }
        })
        
        # Update status
        approval["status"] = "approved" if response.approved else "denied"
        approval["responded_at"] = datetime.now().isoformat()
        
        return {"status": "response_sent", "approval_id": response.approval_id}
        
    def format_approval_data(self, ask_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format approval data for web UI display."""
        
        formatted = {
            "type": ask_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if ask_type == "command":
            formatted.update({
                "command": data.get("command", ""),
                "working_directory": data.get("cwd", ""),
                "description": f"Execute command: {data.get('command', '')}"
            })
        elif ask_type == "tool":
            formatted.update({
                "tool": data.get("tool", ""),
                "parameters": data.get("parameters", {}),
                "description": f"Use tool: {data.get('tool', '')}"
            })
        elif ask_type == "followup":
            formatted.update({
                "question": data.get("question", ""),
                "context": data.get("context", ""),
                "options": data.get("options", [])
            })
        else:
            formatted.update(data)
            
        return formatted
        
    async def process_images(self, images: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Process images for Roo-Code format."""
        
        processed = []
        for img in images:
            try:
                image_data = ImageData(**img)
                
                if image_data.type == "base64":
                    # Already in correct format
                    processed.append({
                        "data": image_data.data,
                        "mime_type": image_data.mime_type,
                        "name": image_data.name
                    })
                elif image_data.type == "url":
                    # Would need to fetch and convert
                    logger.warning("URL image type not yet implemented")
                elif image_data.type == "path":
                    # Would need to read and convert
                    logger.warning("Path image type not yet implemented")
                    
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                
        return processed
        
    async def send_to_web(self, client_id: str, message: Dict[str, Any]) -> None:
        """Send message to web client via WebSocket."""
        
        if self.websocket_manager:
            await self.websocket_manager.send_personal_message(
                json.dumps(message),
                client_id
            )
        else:
            logger.warning("WebSocket manager not set, cannot send to web")
            
    async def send_to_roocode(self, client_id: str, message: Dict[str, Any]) -> None:
        """Send message to Roo-Code via IPC."""
        
        ipc_client = self.ipc_clients.get(client_id)
        if ipc_client:
            try:
                await ipc_client.send_message(message)
            except Exception as e:
                logger.error(f"Error sending to Roo-Code: {e}")
        else:
            logger.warning(f"No IPC client for {client_id}, cannot send to Roo-Code")