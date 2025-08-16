# Phase 2: Roo-Code Communication Bridge - Implementation Plan

## Overview
Phase 2 focuses on creating a transparent communication bridge between web interfaces and Roo-Code. The bridge will pass ALL messages, handle approval flows, and allow configuration of Roo-Code's provider settings. The LLM within Roo-Code remains in control of all tools and operations.

**📘 Implementation Details**: See [PHASE2_IMPLEMENTATION_DETAILS.md](PHASE2_IMPLEMENTATION_DETAILS.md) for complete technical specifications, API methods, message formats, and code examples that enable implementation without examining Roo-Code's source code.

## Core Concept
```
Web UI ←→ Bridge Server ←→ VS Code Extension ←→ Roo-Code
         (WebSocket)      (IPC)              (Native)

The bridge is transparent - it doesn't execute tools, it passes messages.
```

## What Needs to Be Bridged

### 1. Message Types (from Roo-Code to Web UI)

#### ClineAsk Messages (Approval Requests)
These require user interaction and approval:
- `followup` - LLM needs clarification (includes multiple choice questions)
- `command` - Permission to execute command
- `command_output` - Review command output
- `completion_result` - Task completed, needs feedback
- `tool` - Permission to use a tool
- `api_req_failed` - API failed, retry?
- `resume_task` - Resume paused task?
- `browser_action_launch` - Launch browser?
- `use_mcp_server` - Use MCP server?
- `auto_approval_max_req_reached` - Manual approval needed

#### ClineSay Messages (Status Updates)
These are informational:
- `text` - General AI messages
- `reasoning` - AI's thought process
- `error` - Error messages
- `command_output` - Command results
- `api_req_started/finished` - API status
- `tool_progress` - Tool execution progress
- `codebase_search_result` - Search results
- All other status messages

### 2. WebviewMessage Types (from Web UI to Roo-Code)

From `/tmp/Roo-Code/src/shared/WebviewMessage.ts`:

#### Task Control
- `newTask` - Start new task with prompt (can include images)
- `askResponse` - Response to approval request
- `cancelTask` - Cancel current task
- `clearTask` - Clear task history
- `selectImages` - Add images to context
- `draggedImages` - Handle dragged/pasted images

#### Configuration
- `saveApiConfiguration` - Set provider settings
- `loadApiConfiguration` - Load provider config
- `currentApiConfigName` - Get current config
- `customInstructions` - Set custom instructions
- `mode` - Change operating mode

#### Settings
- `allowedCommands` - Set command allowlist
- `deniedCommands` - Set command denylist
- `alwaysAllowReadOnly` - Auto-approve read operations
- `alwaysAllowWrite` - Auto-approve write operations
- `alwaysAllowExecute` - Auto-approve commands
- `autoApprovalEnabled` - Enable auto-approval
- `allowedMaxRequests` - Set request limits
- `allowedMaxCost` - Set cost limits

### 3. Provider Configuration Control

Critical for controlling which LLM Roo-Code uses:
```typescript
interface ProviderSettings {
  provider: "anthropic" | "openai" | "gemini" | "ollama" | ...
  apiKey?: string
  baseUrl?: string
  model: string
  maxTokens?: number
  temperature?: number
  contextLength?: number
  // ... other provider-specific settings
}
```

## Implementation Architecture

```
┌──────────────────────────────────────────────────────┐
│                    Web Client                         │
│  - Sends: newTask, askResponse, configuration        │
│  - Receives: ClineAsk, ClineSay, status updates      │
└────────────────┬─────────────────────────────────────┘
                 │ WebSocket
┌────────────────▼─────────────────────────────────────┐
│              Bridge Server (FastAPI)                  │
│  ┌─────────────────────────────────────────────┐    │
│  │         Message Router & Translator          │    │
│  │  - Routes messages bidirectionally          │    │
│  │  - Manages approval flow state              │    │
│  │  - Translates between protocols             │    │
│  └─────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────┐    │
│  │       Provider Configuration Manager         │    │
│  │  - Stores provider settings                 │    │
│  │  - Sends config updates to Roo-Code         │    │
│  └─────────────────────────────────────────────┘    │
└────────────────┬─────────────────────────────────────┘
                 │ IPC (TCP)
┌────────────────▼─────────────────────────────────────┐
│          VS Code Extension (IPC Server)              │
│  - Receives messages from bridge                     │
│  - Forwards to Roo-Code via extension API            │
│  - Sends Roo-Code events back to bridge              │
└────────────────┬─────────────────────────────────────┘
                 │ Extension API
┌────────────────▼─────────────────────────────────────┐
│                      Roo-Code                         │
│  - LLM controls all tool execution                   │
│  - Sends approval requests                           │
│  - Uses configured provider/model                    │
└───────────────────────────────────────────────────────┘
```

### 4. Image Handling

Images need to be passed through the bridge in both directions:
- **Screenshots** - User shares screenshots for debugging
- **Diagrams** - Architecture/flow diagrams for understanding
- **UI Mockups** - Design references
- **Error Screenshots** - Visual error reports
- **Generated Images** - Images created by tools

Image formats supported:
- Base64 encoded data URLs
- File paths (for local images)
- Binary data over WebSocket

## Implementation Steps

### Step 1: Message Type Definitions (Day 1)

```python
# server/src/messages/types.py
from enum import Enum
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel

class ClineAsk(str, Enum):
    """Approval request types from Roo-Code"""
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
    """Status message types from Roo-Code"""
    TEXT = "text"
    REASONING = "reasoning"
    ERROR = "error"
    COMMAND_OUTPUT = "command_output"
    API_REQ_STARTED = "api_req_started"
    API_REQ_FINISHED = "api_req_finished"
    TOOL_PROGRESS = "tool_progress"
    # ... all other types

class RooCodeMessage(BaseModel):
    """Message from Roo-Code to bridge"""
    type: Union[ClineAsk, ClineSay]
    data: Dict[str, Any]
    timestamp: str
    
class WebviewMessage(BaseModel):
    """Message from web UI to bridge"""
    type: str  # newTask, askResponse, saveApiConfiguration, etc.
    data: Optional[Dict[str, Any]] = {}
    images: Optional[List[Dict[str, str]]] = []  # List of images with metadata
    
class ImageData(BaseModel):
    """Image data structure"""
    type: str  # "base64", "url", "path"
    data: str  # base64 string, URL, or file path
    mime_type: str  # "image/png", "image/jpeg", etc.
    name: Optional[str] = None
    size: Optional[int] = None
```

### Step 2: Bidirectional Message Router (Day 2-3)

```python
# server/src/messages/router.py
class MessageRouter:
    def __init__(self):
        self.pending_approvals = {}  # Track approval requests
        self.active_sessions = {}
        
    async def route_from_web(self, client_id: str, message: WebviewMessage):
        """Route message from web UI to Roo-Code"""
        
        if message.type == "newTask":
            # Start new task in Roo-Code with optional images
            task_data = {
                "type": "newTask",
                "prompt": message.data.get("prompt"),
                "config": message.data.get("config")
            }
            
            # Include images if provided
            if message.images:
                task_data["images"] = await self.process_images(message.images)
                
            await self.send_to_roocode(client_id, task_data)
            
        elif message.type == "askResponse":
            # User responded to approval request
            approval_id = message.data.get("approval_id")
            response = message.data.get("response")
            await self.handle_approval_response(client_id, approval_id, response)
            
        elif message.type == "saveApiConfiguration":
            # Update provider settings in Roo-Code
            await self.update_provider_config(client_id, message.data)
            
    async def route_from_roocode(self, client_id: str, message: RooCodeMessage):
        """Route message from Roo-Code to web UI"""
        
        if message.type in ClineAsk.__members__.values():
            # This is an approval request
            approval_id = self.create_approval_request(client_id, message)
            
            await self.send_to_web(client_id, {
                "type": "approval_required",
                "approval_id": approval_id,
                "ask_type": message.type,
                "data": message.data
            })
            
        else:
            # This is a status update
            await self.send_to_web(client_id, {
                "type": "status_update",
                "say_type": message.type,
                "data": message.data
            })
```

### Step 3: Provider Configuration Bridge (Day 4)

```python
# server/src/config/provider_manager.py
class ProviderManager:
    """Manages provider configuration for Roo-Code"""
    
    async def set_provider(self, client_id: str, config: dict):
        """Send provider configuration to Roo-Code"""
        
        message = {
            "type": "saveApiConfiguration",
            "data": {
                "provider": config.get("provider"),  # anthropic, openai, etc.
                "apiKey": config.get("apiKey"),
                "baseUrl": config.get("baseUrl"),
                "model": config.get("model"),
                "maxTokens": config.get("maxTokens"),
                "temperature": config.get("temperature"),
                "contextLength": config.get("contextLength"),
                # Provider-specific settings
                **config.get("providerSettings", {})
            }
        }
        
        await self.send_to_roocode(client_id, message)
        
    async def get_available_models(self, provider: str):
        """Get list of available models for provider"""
        # Query Roo-Code for available models
        pass
```

### Step 4: Approval Flow Handler (Day 5)

```python
# server/src/approvals/handler.py
class ApprovalHandler:
    """Manages approval flows between web UI and Roo-Code"""
    
    def __init__(self):
        self.pending_approvals = {}
        
    async def create_approval_request(
        self, 
        client_id: str, 
        ask_type: ClineAsk,
        data: dict
    ) -> str:
        """Create approval request and send to web UI"""
        
        approval_id = str(uuid.uuid4())
        
        self.pending_approvals[approval_id] = {
            "client_id": client_id,
            "ask_type": ask_type,
            "data": data,
            "created_at": datetime.now(),
            "status": "pending"
        }
        
        # Format data based on ask type
        formatted_data = self.format_approval_data(ask_type, data)
        
        # Handle multiple choice questions for followup
        if ask_type == ClineAsk.FOLLOWUP and "options" in data:
            formatted_data["options"] = data["options"]
            formatted_data["allow_text_response"] = data.get("allow_text_response", True)
        
        # Send to web UI
        await self.websocket_manager.send(client_id, {
            "type": "approval_request",
            "approval_id": approval_id,
            "ask_type": ask_type,
            "data": formatted_data
        })
        
        return approval_id
        
    async def handle_approval_response(
        self,
        approval_id: str,
        approved: bool,
        modifications: dict = None
    ):
        """Handle user's response to approval request"""
        
        approval = self.pending_approvals.get(approval_id)
        if not approval:
            raise ValueError(f"Unknown approval ID: {approval_id}")
            
        # Send response back to Roo-Code
        await self.send_to_roocode(approval["client_id"], {
            "type": "askResponse",
            "data": {
                "approved": approved,
                "modifications": modifications,
                "ask_type": approval["ask_type"]
            }
        })
        
        # Update status
        approval["status"] = "approved" if approved else "denied"
```

### Step 5: Image Handler (Day 6)

```python
# server/src/images/handler.py
import base64
from typing import List, Dict, Any
from PIL import Image
import io

class ImageHandler:
    """Handles image processing for the bridge"""
    
    async def process_images_for_roocode(self, images: List[Dict[str, Any]]) -> List[Dict]:
        """Process images from web UI to Roo-Code format"""
        processed = []
        
        for img in images:
            if img["type"] == "base64":
                # Already in base64, just validate and forward
                processed.append({
                    "type": "image",
                    "data": img["data"],
                    "mime_type": img.get("mime_type", "image/png")
                })
                
            elif img["type"] == "url":
                # Fetch image from URL and convert to base64
                image_data = await self.fetch_image(img["data"])
                processed.append({
                    "type": "image",
                    "data": base64.b64encode(image_data).decode(),
                    "mime_type": self.detect_mime_type(image_data)
                })
                
            elif img["type"] == "path":
                # Read local file and convert to base64
                with open(img["data"], "rb") as f:
                    image_data = f.read()
                processed.append({
                    "type": "image",
                    "data": base64.b64encode(image_data).decode(),
                    "mime_type": self.detect_mime_type(image_data)
                })
                
        return processed
    
    async def handle_screenshot_paste(self, clipboard_data: bytes) -> Dict:
        """Handle pasted screenshots from clipboard"""
        # Convert clipboard data to base64
        return {
            "type": "image",
            "data": base64.b64encode(clipboard_data).decode(),
            "mime_type": "image/png"
        }
    
    def validate_image_size(self, image_data: bytes, max_size_mb: int = 10) -> bool:
        """Validate image size constraints"""
        size_mb = len(image_data) / (1024 * 1024)
        return size_mb <= max_size_mb
```

### Step 6: Enhanced VS Code Extension (Day 7-8)

```typescript
// extension/src/message-bridge.ts
export class MessageBridge {
    private rooCodeInterface: any;
    
    constructor(private context: vscode.ExtensionContext) {
        this.initializeRooCodeInterface();
    }
    
    private initializeRooCodeInterface() {
        // Get Roo-Code extension API
        const rooCodeExt = vscode.extensions.getExtension('roo-code');
        if (rooCodeExt) {
            this.rooCodeInterface = rooCodeExt.exports;
            this.setupEventListeners();
        }
    }
    
    private setupEventListeners() {
        // Listen for all Roo-Code events
        this.rooCodeInterface.onMessage((message: any) => {
            this.forwardTobridge(message);
        });
        
        this.rooCodeInterface.onAsk((ask: any) => {
            this.forwardTobridge({
                type: 'ask',
                data: ask
            });
        });
        
        this.rooCodeInterface.onSay((say: any) => {
            this.forwardTobridge({
                type: 'say',
                data: say
            });
        });
    }
    
    async handleBridgeMessage(message: any) {
        // Route message to appropriate Roo-Code API
        switch(message.type) {
            case 'newTask':
                await this.rooCodeInterface.startTask(
                    message.data.prompt,
                    message.data.config
                );
                break;
                
            case 'askResponse':
                await this.rooCodeInterface.respondToAsk(
                    message.data.approved,
                    message.data.response
                );
                break;
                
            case 'saveApiConfiguration':
                await this.rooCodeInterface.updateConfiguration(
                    message.data
                );
                break;
                
            // ... handle all other message types
        }
    }
}
```

### Step 6: WebSocket API (Day 8)

```python
# server/src/main.py updates
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive from web UI
            data = await websocket.receive_json()
            message = WebviewMessage(**data)
            
            # Route to Roo-Code
            await router.route_from_web(client_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
```

## API Endpoints

### Task Management
```
POST /api/tasks/start
Body: {
    "prompt": "Create a Python web server based on this design",
    "provider": "anthropic",
    "model": "claude-3-sonnet",
    "maxTokens": 4000,
    "temperature": 0.7,
    "images": [
        {
            "type": "base64",
            "data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
            "mime_type": "image/png",
            "name": "architecture_diagram.png"
        }
    ]
}

WebSocket Events:
← {"type": "task_started", "task_id": "123"}
← {"type": "say", "say_type": "text", "data": {"content": "I'll create..."}}
← {"type": "ask", "ask_type": "tool", "approval_id": "456", "data": {...}}
→ {"type": "askResponse", "approval_id": "456", "approved": true}
← {"type": "say", "say_type": "tool_progress", "data": {"status": "writing file..."}}
```

### Provider Configuration
```
POST /api/config/provider
Body: {
    "provider": "anthropic",
    "apiKey": "sk-...",
    "model": "claude-3-opus",
    "maxTokens": 8000,
    "contextLength": 200000
}

GET /api/config/provider
Response: {
    "current": "anthropic",
    "available": ["anthropic", "openai", "gemini"],
    "models": ["claude-3-opus", "claude-3-sonnet", ...]
}
```

### Approval Management

#### Command Approval
```
WebSocket:
← {
    "type": "approval_request",
    "approval_id": "789",
    "ask_type": "command",
    "data": {
        "command": "npm install express",
        "cwd": "/project"
    }
}

→ {
    "type": "askResponse",
    "approval_id": "789",
    "approved": true,
    "modifications": null
}
```

#### Multiple Choice Followup
```
WebSocket:
← {
    "type": "approval_request",
    "approval_id": "456",
    "ask_type": "followup",
    "data": {
        "question": "Which framework would you like to use?",
        "options": [
            "1. Express.js - Minimal and flexible",
            "2. Fastify - High performance",
            "3. Koa - Modern and lightweight",
            "4. Hapi - Configuration-centric"
        ],
        "allow_text_response": true
    }
}

→ {
    "type": "askResponse",
    "approval_id": "456",
    "response": "2"  // User selected option 2
}

// Or with custom text response:
→ {
    "type": "askResponse", 
    "approval_id": "456",
    "response": "Let's use NestJS instead"
}
```

#### Image Sharing
```
WebSocket:
// User shares screenshot for debugging
→ {
    "type": "newTask",
    "data": {
        "prompt": "Can you help me fix this error?"
    },
    "images": [
        {
            "type": "base64",
            "data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
            "mime_type": "image/png",
            "name": "error_screenshot.png"
        }
    ]
}

// Drag and drop multiple images
→ {
    "type": "draggedImages",
    "images": [
        {
            "type": "base64",
            "data": "...",
            "mime_type": "image/jpeg",
            "name": "mockup1.jpg"
        },
        {
            "type": "base64", 
            "data": "...",
            "mime_type": "image/png",
            "name": "mockup2.png"
        }
    ]
}

// Paste from clipboard
→ {
    "type": "selectImages",
    "images": [
        {
            "type": "clipboard",
            "data": "...",
            "mime_type": "image/png"
        }
    ]
}
```

## Testing Strategy

### Integration Tests
```python
async def test_full_communication_flow():
    """Test complete message flow through bridge"""
    
    # 1. Connect web client
    ws = await connect_websocket("/ws/test-client")
    
    # 2. Start task
    await ws.send_json({
        "type": "newTask",
        "data": {
            "prompt": "Write hello world",
            "provider": "anthropic",
            "model": "claude-3-sonnet"
        }
    })
    
    # 3. Receive status updates
    msg = await ws.receive_json()
    assert msg["type"] == "say"
    assert msg["say_type"] == "text"
    
    # 4. Handle approval request
    msg = await ws.receive_json()
    if msg["type"] == "approval_request":
        await ws.send_json({
            "type": "askResponse",
            "approval_id": msg["approval_id"],
            "approved": True
        })
    
    # 5. Verify completion
    # ...
```

## Security Considerations

1. **API Key Protection**: Never expose provider API keys to web clients
2. **Message Validation**: Validate all messages between components
3. **Approval Verification**: Ensure approval requests are legitimate
4. **Session Isolation**: Keep client sessions completely separate
5. **Rate Limiting**: Limit task creation and API calls

## Success Metrics

- [ ] All ClineAsk types properly bridged
- [ ] All ClineSay types properly bridged
- [ ] Provider configuration working
- [ ] Model selection working
- [ ] Context length configurable
- [ ] Approval flows working end-to-end
- [ ] Real-time message streaming
- [ ] Multiple concurrent sessions supported
- [ ] < 50ms message routing latency


## Key Differences from Original Plan

1. **No Tool Implementation**: The bridge doesn't implement tools - Roo-Code's LLM controls them
2. **Pure Message Passing**: Bridge is transparent, just routes messages
3. **Provider Control**: Added ability to control which LLM provider/model Roo-Code uses
4. **Approval Focus**: Emphasis on handling approval flows correctly
5. **Configuration Bridge**: Full configuration control through the bridge
