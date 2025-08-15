# Phase 2: Implementation Details & Technical Specifications

This document provides complete implementation details for Phase 2, enabling development without needing to examine Roo-Code's source code.

## Critical Implementation Details

### 1. Roo-Code Extension API Access

The Roo-Code extension exposes an API that our VS Code bridge extension must access:

```typescript
// extension/src/roo-interface.ts
import * as vscode from 'vscode';

export class RooCodeInterface {
    private rooCodeAPI: any;
    private rooCodeExtension: vscode.Extension<any>;
    
    async initialize(): Promise<boolean> {
        // Roo-Code's extension ID (from package.json)
        const ROO_CODE_EXTENSION_ID = 'saoudrizwan.claude-dev';
        
        // Get the Roo-Code extension
        this.rooCodeExtension = vscode.extensions.getExtension(ROO_CODE_EXTENSION_ID);
        
        if (!this.rooCodeExtension) {
            console.error('Roo-Code extension not found');
            return false;
        }
        
        // Activate if not already active
        if (!this.rooCodeExtension.isActive) {
            await this.rooCodeExtension.activate();
        }
        
        // Get the API
        this.rooCodeAPI = this.rooCodeExtension.exports;
        
        return true;
    }
}
```

### 2. Available API Methods

The Roo-Code API exposes these methods:

```typescript
interface RooCodeAPI {
    // Task Management
    startNewTask(params: {
        configuration: RooCodeSettings;
        text?: string;
        images?: string[];
        newTab?: boolean;
    }): Promise<string>; // Returns taskId
    
    resumeTask(taskId: string): Promise<void>;
    cancelTask(taskId: string): Promise<void>;
    cancelCurrentTask(): Promise<void>;
    clearCurrentTask(lastMessage?: string): Promise<void>;
    
    // Message Handling
    sendMessage(text?: string, images?: string[]): Promise<void>;
    pressPrimaryButton(): Promise<void>;  // For "Yes" responses
    pressSecondaryButton(): Promise<void>; // For "No" responses
    
    // Configuration
    getConfiguration(): RooCodeSettings;
    setConfiguration(values: RooCodeSettings): Promise<void>;
    
    // Provider Profiles
    getProfiles(): string[];
    getProfileEntry(name: string): ProviderSettingsEntry | undefined;
    createProfile(name: string, profile?: ProviderSettings, activate?: boolean): Promise<string>;
    updateProfile(name: string, profile: ProviderSettings, activate?: boolean): Promise<string>;
    deleteProfile(name: string): Promise<void>;
    getActiveProfile(): string | undefined;
    setActiveProfile(name: string): Promise<string>;
    
    // Status
    isReady(): boolean;
    getCurrentTaskStack(): any;
    isTaskInHistory(taskId: string): Promise<boolean>;
    
    // Events (EventEmitter)
    on(event: string, handler: Function): void;
    off(event: string, handler: Function): void;
}
```

### 3. Event Names and Payloads

```typescript
// Events emitted by Roo-Code
enum RooCodeEventName {
    // Task Lifecycle
    TaskCreated = "taskCreated",
    TaskStarted = "taskStarted", 
    TaskCompleted = "taskCompleted",
    TaskAborted = "taskAborted",
    TaskPaused = "taskPaused",
    TaskUnpaused = "taskUnpaused",
    TaskSpawned = "taskSpawned",
    
    // Messages
    Message = "message",
    
    // Task Execution
    TaskModeSwitched = "taskModeSwitched",
    TaskAskResponded = "taskAskResponded",
    TaskToolFailed = "taskToolFailed",
    TaskTokenUsageUpdated = "taskTokenUsageUpdated"
}

// Message event payload structure
interface MessageEvent {
    taskId: string;
    message: {
        type: "ask" | "say";
        ask?: ClineAsk;        // When type is "ask"
        say?: ClineSay;        // When type is "say"
        text?: string;         // Message content
        data?: any;            // Additional data
        ts?: number;           // Timestamp
        partial?: boolean;     // If message is still streaming
    };
}
```

### 4. Handling Ask Responses via Webview Messages

Since the API doesn't have direct ask response methods, use the ClineProvider's webview messaging:

```typescript
// To respond to approval requests, send webview messages
async function handleAskResponse(
    provider: any, // ClineProvider instance
    askType: string,
    response: any
) {
    // Get the current task
    const currentTask = provider.getCurrentTask();
    if (!currentTask) return;
    
    // Send response via webview message
    await provider.postMessageToWebview({
        type: "askResponse",
        askResponse: response.approved ? "yesButtonClicked" : "noButtonClicked",
        text: response.text,      // For text responses
        images: response.images    // For image responses
    });
}

// For multiple choice questions
async function handleMultipleChoice(
    provider: any,
    choiceIndex: number | string
) {
    await provider.postMessageToWebview({
        type: "askResponse",
        askResponse: "messageResponse",
        text: String(choiceIndex)  // Send choice as text
    });
}
```

### 5. Configuration Structure

```typescript
interface RooCodeSettings {
    // Provider Settings
    apiProvider?: string;           // "anthropic", "openai", etc.
    apiModelId?: string;           // Model identifier
    apiKey?: string;               // API key (stored securely)
    apiUrl?: string;               // Custom API endpoint
    
    // Current Configuration
    currentApiConfigName?: string;  // Active profile name
    
    // Model Parameters
    maxTokens?: number;
    temperature?: number;
    topP?: number;
    topK?: number;
    
    // Custom Instructions
    customInstructions?: string;
    
    // Permissions
    allowedCommands?: string[];
    deniedCommands?: string[];
    alwaysAllowReadOnly?: boolean;
    alwaysAllowWrite?: boolean;
    alwaysAllowExecute?: boolean;
    alwaysAllowBrowser?: boolean;
    alwaysAllowMcp?: boolean;
    
    // Limits
    allowedMaxRequests?: number;
    allowedMaxCost?: number;
    commandExecutionTimeout?: number;
    
    // Features
    autoApprovalEnabled?: boolean;
    autoCondenseContext?: boolean;
    autoCondenseContextPercent?: number;
    diffEnabled?: boolean;
    enableCheckpoints?: boolean;
    
    // Terminal Settings
    terminalOutputLineLimit?: number;
    terminalOutputCharacterLimit?: number;
    terminalShellIntegrationDisabled?: boolean;
    
    // Mode
    mode?: "code" | "architect" | "ask";
}
```

### 6. IPC Message Protocol

The VS Code extension should implement a TCP server that speaks this protocol:

```typescript
// IPC Message Format (newline-delimited JSON)
interface IPCMessage {
    type: string;
    id?: string;      // Request ID for correlation
    data?: any;       // Message payload
    error?: string;   // Error message if applicable
}

// Example messages:
// Client → Server:
{"type": "task.start", "id": "123", "data": {"prompt": "Hello", "config": {...}}}
{"type": "ask.response", "id": "456", "data": {"approved": true}}

// Server → Client:
{"type": "event", "data": {"name": "taskStarted", "taskId": "789"}}
{"type": "ask", "data": {"type": "command", "command": "npm install"}}
{"type": "say", "data": {"type": "text", "content": "Working on it..."}}
```

### 7. Image Handling Specifics

Images must be base64 encoded for transmission:

```typescript
interface ImageData {
    // Images should be data URLs
    data: string;  // "data:image/png;base64,iVBORw0KGgoAAAANS..."
    
    // Or file paths (will be read and converted)
    path?: string; // "/path/to/image.png"
}

// Converting images for Roo-Code
function prepareImagesForRooCode(images: ImageData[]): string[] {
    return images.map(img => {
        if (img.data.startsWith('data:')) {
            return img.data; // Already a data URL
        }
        // Read file and convert to base64
        const buffer = fs.readFileSync(img.path);
        const base64 = buffer.toString('base64');
        const mimeType = getMimeType(img.path);
        return `data:${mimeType};base64,${base64}`;
    });
}
```

### 8. Complete Message Flow Example

```typescript
// 1. Web client starts a task
WebClient → Bridge: {
    "type": "newTask",
    "data": {
        "prompt": "Create a web server",
        "provider": "anthropic",
        "model": "claude-3-sonnet"
    }
}

// 2. Bridge configures and starts task in Roo-Code
Bridge → RooCode API: startNewTask({
    text: "Create a web server",
    configuration: {
        apiProvider: "anthropic",
        apiModelId: "claude-3-sonnet"
    }
})

// 3. Roo-Code emits events
RooCode → Bridge (via events):
- Event: "taskStarted", taskId: "abc123"
- Event: "message", { type: "say", say: "text", text: "I'll create..." }
- Event: "message", { type: "ask", ask: "tool", data: { tool: "write_file" } }

// 4. Bridge forwards to web client
Bridge → WebClient: {
    "type": "approval_request",
    "ask_type": "tool",
    "data": { "tool": "write_file", "path": "server.js" }
}

// 5. User approves
WebClient → Bridge: {
    "type": "askResponse",
    "approved": true
}

// 6. Bridge sends to Roo-Code
Bridge → RooCode: pressPrimaryButton() or postMessageToWebview({type: "askResponse", ...})
```

### 9. Error Handling Requirements

```typescript
// All operations should handle these error cases:

try {
    const result = await rooCodeAPI.startNewTask(params);
} catch (error) {
    if (error.message.includes('not found')) {
        // Roo-Code extension not installed
    } else if (error.message.includes('not active')) {
        // Extension not activated
    } else if (error.message.includes('policy')) {
        // Operation blocked by policy
    } else {
        // Generic error
    }
}

// Event errors
rooCodeAPI.on('error', (error) => {
    // Handle async errors from Roo-Code
});
```

### 10. Testing Without Roo-Code

For development/testing without Roo-Code installed:

```typescript
// Mock Roo-Code API
class MockRooCodeAPI {
    private events = new EventEmitter();
    
    async startNewTask(params) {
        // Simulate task creation
        const taskId = generateId();
        
        setTimeout(() => {
            this.events.emit('taskStarted', taskId);
            this.events.emit('message', {
                taskId,
                message: { type: 'say', say: 'text', text: 'Starting...' }
            });
        }, 100);
        
        return taskId;
    }
    
    on(event, handler) {
        this.events.on(event, handler);
    }
    
    // ... implement other methods
}
```

## Required NPM Packages

```json
{
  "dependencies": {
    "@types/vscode": "^1.85.0",
    "vscode": "^1.1.37",
    "net": "^1.0.2",          // For TCP server
    "uuid": "^9.0.0",         // For generating IDs
    "events": "^3.3.0"        // For EventEmitter
  }
}
```

## Security Considerations

1. **API Key Protection**: Never log or expose API keys
2. **Input Validation**: Validate all messages from web clients
3. **Rate Limiting**: Implement per-client rate limits
4. **Secure IPC**: Use authentication tokens for IPC connections
5. **Sandbox Images**: Validate image sizes and formats

## Performance Considerations

1. **Message Batching**: Batch rapid events to reduce overhead
2. **Image Compression**: Compress large images before transmission
3. **Connection Pooling**: Reuse IPC connections
4. **Event Throttling**: Throttle high-frequency events like token updates
5. **Async Operations**: All operations should be non-blocking

## Deployment Checklist

- [ ] VS Code extension manifest includes all permissions
- [ ] IPC server port is configurable (default 9999)
- [ ] Bridge server supports multiple concurrent clients
- [ ] All events are properly forwarded bidirectionally
- [ ] Error recovery and reconnection logic implemented
- [ ] Logging configured (without sensitive data)
- [ ] Tests cover all message types and error cases
- [ ] Documentation includes setup instructions
- [ ] Security review completed