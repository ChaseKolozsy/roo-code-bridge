# Roo-Code Bridge

A programmatic interface bridge for Roo-Code that enables web-based UIs and external applications to interact with the Roo-Code VS Code extension.

## 📋 Project Status

- ✅ **Phase 1: Core Infrastructure** - COMPLETED ([Details](PHASE1_STATUS.md))
- 🚧 **Phase 2: Roo-Code Integration** - IN PLANNING ([Plan](PHASE2_PLAN.md))
- ⏳ Phase 3: Advanced Features - Not Started
- ⏳ Phase 4: Multi-LLM Support - Not Started  
- ⏳ Phase 5: Web Interface - Not Started

## 🏗️ Architecture

```
Web Client → WebSocket → FastAPI → IPC → VS Code Extension → Roo-Code
```

## Project Structure

```
roo-code-bridge/
├── extension/          # VS Code extension with IPC server
├── server/            # FastAPI backend with WebSocket support
├── tests/             # Integration and unit tests
├── PHASE1_STATUS.md   # Phase 1 completion details
└── PHASE2_PLAN.md     # Phase 2 implementation plan
```

## Quick Start

### 1. Start the Bridge Server
```bash
cd server
uv run python src/main.py
```

### 2. Install VS Code Extension
```bash
cd extension
npm install
npm run compile
# Press F5 in VS Code to launch
```

### 3. Run Tests
```bash
# Test server components
cd server
uv run python tests/test_phase1.py

# Test with VS Code extension running
python test_extension.py
python demo_phase1.py
```

## Features Implemented (Phase 1)

### ✅ Core Infrastructure
- **VS Code Extension**: IPC server on port 9999 with JSON message protocol
- **WebSocket Server**: Real-time bidirectional communication
- **REST API**: Task, config, tools, and message endpoints
- **Session Management**: SQLite-based session tracking
- **Authentication**: JWT tokens with Bearer auth
- **Adapter Pattern**: Extensible LLM provider support

### 🚧 Coming Soon (Phase 2)

- **17 Roo-Code Tools**: All file, command, search, and task operations
- **Message Streaming**: Real-time output from commands and tools
- **Approval Flows**: User confirmation for dangerous operations
- **Task Management**: Complete lifecycle with state persistence

See [PHASE2_PLAN.md](PHASE2_PLAN.md) for detailed roadmap.

## API Examples

### WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/my-client-id');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

ws.send(JSON.stringify({
    type: 'ping',
    data: { message: 'Hello' }
}));
```

### REST API
```bash
# Health check
curl http://localhost:8000/health

# With authentication
curl -H "Authorization: Bearer your-token" \
     http://localhost:8000/api/config/providers
```

## Development

### Requirements
- Python 3.10+
- Node.js 16+
- VS Code

### Setup
```bash
# Clone repository
git clone https://github.com/ChaseKolozsy/roo-code-bridge.git
cd roo-code-bridge

# Server setup
cd server
uv venv
uv pip install -r requirements.txt

# Extension setup
cd ../extension
npm install
npm run compile
```

## Contributing

See the implementation plans:
- [Phase 1 Status](PHASE1_STATUS.md) - Completed infrastructure
- [Phase 2 Plan](PHASE2_PLAN.md) - Roo-Code integration roadmap

## License

MIT License - See LICENSE for details.