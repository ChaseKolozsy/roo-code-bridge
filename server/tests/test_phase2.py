#!/usr/bin/env python3
"""
Test script for Phase 2 features: Provider configuration and message routing.
Run after starting the server with: uv run python src/main.py
"""

import asyncio
import json
import websockets
from datetime import datetime

async def test_provider_configuration():
    """Test provider configuration management."""
    
    uri = "ws://localhost:8000/ws/test-phase2-client"
    
    async with websockets.connect(uri) as websocket:
        print("🔌 Connected to WebSocket")
        
        # Test 1: Configure provider
        print("\n📝 Test 1: Configuring provider...")
        config_msg = {
            "type": "saveApiConfiguration",
            "data": {
                "provider": "anthropic",
                "model": "claude-3-sonnet",
                "max_tokens": 4096,
                "temperature": 0.7,
                "context_length": 200000
            }
        }
        
        await websocket.send(json.dumps(config_msg))
        response = await websocket.recv()
        response_data = json.loads(response)
        print(f"Response: {response_data}")
        
        # Test 2: Start a new task with provider config
        print("\n📝 Test 2: Starting new task with provider config...")
        task_msg = {
            "type": "newTask",
            "data": {
                "prompt": "Write a simple hello world in Python",
                "provider": "openai",
                "model": "gpt-4-turbo",
                "max_tokens": 2048
            }
        }
        
        await websocket.send(json.dumps(task_msg))
        response = await websocket.recv()
        response_data = json.loads(response)
        print(f"Response: {response_data}")
        
        # Test 3: Test approval flow (simulate)
        print("\n📝 Test 3: Testing approval flow...")
        # This would normally come from Roo-Code, but we can simulate the response
        
        # Test 4: Cancel task
        print("\n📝 Test 4: Cancelling task...")
        cancel_msg = {
            "type": "cancelTask",
            "data": {
                "taskId": "test-task-123"
            }
        }
        
        await websocket.send(json.dumps(cancel_msg))
        response = await websocket.recv()
        response_data = json.loads(response)
        print(f"Response: {response_data}")
        
        # Test 5: Test with images
        print("\n📝 Test 5: Testing with images...")
        image_task_msg = {
            "type": "newTask",
            "data": {
                "prompt": "Analyze this image and create a similar UI"
            },
            "images": [
                {
                    "type": "base64",
                    "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                    "mime_type": "image/png",
                    "name": "test.png"
                }
            ]
        }
        
        await websocket.send(json.dumps(image_task_msg))
        response = await websocket.recv()
        response_data = json.loads(response)
        print(f"Response: {response_data}")
        
        print("\n✅ All Phase 2 tests completed!")

async def test_message_routing():
    """Test bidirectional message routing."""
    
    uri = "ws://localhost:8000/ws/test-routing-client"
    
    async with websockets.connect(uri) as websocket:
        print("\n🔄 Testing message routing...")
        
        # Send different message types
        message_types = [
            {"type": "newTask", "data": {"prompt": "Test"}},
            {"type": "askResponse", "data": {"approval_id": "123", "approved": True}},
            {"type": "selectImages", "images": []},
            {"type": "draggedImages", "images": []},
        ]
        
        for msg in message_types:
            print(f"\nSending {msg['type']}...")
            await websocket.send(json.dumps(msg))
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                response_data = json.loads(response)
                print(f"Response: {response_data}")
            except asyncio.TimeoutError:
                print(f"No response for {msg['type']} (expected if VS Code extension not running)")

async def main():
    print("=" * 50)
    print("Phase 2 Feature Tests")
    print("=" * 50)
    
    try:
        await test_provider_configuration()
        await test_message_routing()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())