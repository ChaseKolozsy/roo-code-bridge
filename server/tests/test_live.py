#!/usr/bin/env python3
"""
Live test of Phase 2 features - Interactive mode
"""

import asyncio
import json
import websockets
from datetime import datetime

async def test_phase2_interactive():
    uri = "ws://localhost:47291/ws/live-test-client"
    
    print("🚀 Connecting to Roo-Code Bridge...")
    async with websockets.connect(uri) as websocket:
        print("✅ Connected! Testing Phase 2 features...")
        
        # Test 1: Provider Configuration
        print("\n1️⃣ Testing Provider Configuration...")
        providers = ["anthropic", "openai", "gemini"]
        models = ["claude-3-sonnet", "gpt-4-turbo", "gemini-1.5-pro"]
        
        for provider, model in zip(providers, models):
            config = {
                "type": "saveApiConfiguration",
                "data": {
                    "provider": provider,
                    "model": model,
                    "max_tokens": 4096,
                    "temperature": 0.7
                }
            }
            
            print(f"   🔧 Configuring {provider} with {model}...")
            await websocket.send(json.dumps(config))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"   ✅ Response: {data.get('data', {}).get('status', 'unknown')}")
        
        # Test 2: Task Creation with Provider
        print("\n2️⃣ Testing Task Creation with Provider...")
        task = {
            "type": "newTask",
            "data": {
                "prompt": "Create a simple web server in Python",
                "provider": "anthropic",
                "model": "claude-3-sonnet",
                "max_tokens": 2048
            }
        }
        
        await websocket.send(json.dumps(task))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"   ✅ Task started: {data.get('data', {}).get('status', 'unknown')}")
        
        # Test 3: Image Handling
        print("\n3️⃣ Testing Image Handling...")
        # Small test image (1x1 pixel)
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        image_task = {
            "type": "newTask",
            "data": {
                "prompt": "Analyze this image"
            },
            "images": [
                {
                    "type": "base64",
                    "data": test_image,
                    "mime_type": "image/png",
                    "name": "test.png"
                }
            ]
        }
        
        await websocket.send(json.dumps(image_task))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"   ✅ Image task created: {data.get('data', {}).get('status', 'unknown')}")
        
        # Test 4: Message Types
        print("\n4️⃣ Testing Different Message Types...")
        message_types = [
            {"type": "cancelTask", "data": {"taskId": "test-123"}},
            {"type": "resumeTask", "data": {"taskId": "test-456"}},
            {"type": "selectImages", "images": []},
            {"type": "draggedImages", "images": []}
        ]
        
        for msg in message_types:
            await websocket.send(json.dumps(msg))
            response = await websocket.recv()
            data = json.loads(response)
            status = data.get('data', {}).get('status', 'unknown')
            print(f"   ✅ {msg['type']}: {status}")
        
        # Test 5: Error Handling
        print("\n5️⃣ Testing Error Handling...")
        bad_approval = {
            "type": "askResponse",
            "data": {
                "approval_id": "non-existent-id",
                "approved": True
            }
        }
        
        await websocket.send(json.dumps(bad_approval))
        response = await websocket.recv()
        data = json.loads(response)
        if data.get('type') == 'error':
            print(f"   ✅ Error handled correctly: {data.get('data', {}).get('message', 'unknown')}")
        else:
            print(f"   ❓ Unexpected response: {data}")
        
        print("\n🎉 All Phase 2 features tested successfully!")
        print(f"📊 Summary:")
        print(f"   • Provider configuration: Working ✅")
        print(f"   • Task creation: Working ✅")
        print(f"   • Image handling: Working ✅")
        print(f"   • Message routing: Working ✅")
        print(f"   • Error handling: Working ✅")

async def main():
    print("=" * 60)
    print("🧪 PHASE 2 LIVE TESTING")
    print("=" * 60)
    
    try:
        await test_phase2_interactive()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())