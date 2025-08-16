#!/usr/bin/env python3
"""
Demo: How to use the Roo-Code Bridge with Qwen-3-Coder
"""

import asyncio
import json
import websockets

async def demo_usage():
    print("🎯 Roo-Code Bridge Usage Demo")
    print("=" * 40)
    print("📡 Server: localhost:47291")
    print("🧠 Model: qwen-3-coder")
    print("🔗 Endpoint: http://localhost:3000/v1")
    print("=" * 40)
    
    uri = "ws://localhost:47291/ws/demo-user"
    
    async with websockets.connect(uri) as websocket:
        print("\n✅ Connected to bridge!")
        
        # 1. Configure your Qwen setup
        print("\n1️⃣ Configuring Qwen-3-Coder...")
        config_message = {
            "type": "saveApiConfiguration",
            "data": {
                "provider": "openai-compatible",
                "model": "qwen-3-coder",
                "base_url": "http://localhost:3000/v1",
                "context_length": 131000,
                "max_tokens": 4096,
                "temperature": 0.7
            }
        }
        
        await websocket.send(json.dumps(config_message))
        response = await websocket.recv()
        print(f"✅ Configured: {json.loads(response)['data']['status']}")
        
        # 2. Start a coding task
        print("\n2️⃣ Starting coding task...")
        task_message = {
            "type": "newTask",
            "data": {
                "prompt": "Create a FastAPI endpoint that handles file uploads with validation",
                "provider": "openai-compatible",
                "model": "qwen-3-coder",
                "max_tokens": 2048,
                "temperature": 0.3
            }
        }
        
        await websocket.send(json.dumps(task_message))
        response = await websocket.recv()
        print(f"✅ Task started: {json.loads(response)['data']['status']}")
        
        # 3. Example of other operations
        print("\n3️⃣ Other available operations...")
        
        operations = [
            {"type": "cancelTask", "desc": "Cancel current task"},
            {"type": "resumeTask", "desc": "Resume paused task"},
            {"type": "selectImages", "desc": "Add images to context"},
            {"type": "askResponse", "desc": "Respond to approval requests"}
        ]
        
        for op in operations:
            print(f"   📋 {op['type']}: {op['desc']}")
        
        print("\n🎉 Demo completed!")
        print("\n📝 To connect with VS Code extension:")
        print("   1. Open extension folder in VS Code")
        print("   2. Press F5 to launch extension")
        print("   3. Extension will connect to bridge on port 9999")
        print("   4. Bridge will relay messages to/from Roo-Code")

async def main():
    try:
        await demo_usage()
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    asyncio.run(main())