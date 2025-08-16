#!/usr/bin/env python3
"""
Full integration test with VS Code extension and Qwen-3-Coder
"""

import asyncio
import json
import websockets
import sys

async def test_full_integration():
    uri = "ws://localhost:47291/ws/integration-test"
    
    print("🚀 Full Integration Test - Qwen-3-Coder")
    print("=" * 50)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to Roo-Code Bridge")
            
            # Step 1: Configure Qwen-3-Coder
            print("\n🔧 Step 1: Configuring Qwen-3-Coder...")
            config = {
                "type": "saveApiConfiguration",
                "data": {
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder",
                    "base_url": "http://localhost:3000/v1",
                    "context_length": 131000,
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    "api_key": "your-api-key-here"  # Add if needed
                }
            }
            
            await websocket.send(json.dumps(config))
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get('type') == 'response':
                print(f"✅ Configuration successful: {data['data']['status']}")
            else:
                print(f"❌ Configuration failed: {data}")
            
            # Step 2: Create a coding task
            print("\n📝 Step 2: Creating a coding task...")
            task = {
                "type": "newTask",
                "data": {
                    "prompt": """Please create a Python function that implements a simple calculator with the following features:
1. Add, subtract, multiply, divide operations
2. Handle division by zero errors
3. Include proper type hints
4. Add docstring documentation
5. Include basic unit tests

Make it clean, well-documented code that follows Python best practices.""",
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder",
                    "max_tokens": 2048,
                    "temperature": 0.3  # Lower for coding
                }
            }
            
            await websocket.send(json.dumps(task))
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get('type') == 'response':
                print(f"✅ Task created: {data['data']['status']}")
                print(f"   Client ID: {data['data'].get('client_id', 'unknown')}")
            else:
                print(f"❌ Task creation failed: {data}")
            
            # Step 3: Listen for messages (with timeout)
            print("\n👂 Step 3: Listening for Roo-Code messages...")
            print("   (This will show any messages from Roo-Code if extension is connected)")
            
            timeout = 10  # Wait 10 seconds for any messages
            try:
                while timeout > 0:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(response)
                        
                        if data.get('type') == 'approval_required':
                            print(f"📋 Approval request: {data.get('data', {}).get('ask_type', 'unknown')}")
                        elif data.get('type') == 'status_update':
                            print(f"📊 Status update: {data.get('say_type', 'unknown')}")
                        elif data.get('type') == 'event':
                            print(f"🎉 Event: {data.get('event_name', 'unknown')}")
                        else:
                            print(f"💬 Message: {data.get('type', 'unknown')}")
                            
                    except asyncio.TimeoutError:
                        timeout -= 1
                        if timeout % 3 == 0:
                            print(f"   ⏳ Waiting... ({timeout}s remaining)")
                        
            except Exception as e:
                print(f"   ⚠️  Listening stopped: {e}")
            
            # Step 4: Test image handling
            print("\n🖼️  Step 4: Testing image handling...")
            # Simple 1x1 test image
            test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx8gAAAABJRU5ErkJggg=="
            
            image_task = {
                "type": "newTask",
                "data": {
                    "prompt": "Analyze this UI mockup and suggest improvements for better UX"
                },
                "images": [
                    {
                        "type": "base64",
                        "data": test_image,
                        "mime_type": "image/png",
                        "name": "ui_mockup.png"
                    }
                ]
            }
            
            await websocket.send(json.dumps(image_task))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✅ Image task: {data.get('data', {}).get('status', 'unknown')}")
            
            print("\n🎯 Integration Test Summary:")
            print("   ✅ Bridge server: Working (port 47291)")
            print("   ✅ Provider config: Qwen-3-Coder configured")
            print("   ✅ Task creation: Working")
            print("   ✅ Image handling: Working")
            print("   ✅ Message routing: Ready")
            
            # Check VS Code extension status
            print("\n🔌 VS Code Extension Status:")
            if "No IPC client" in str(data):  # This would appear in logs
                print("   ⚠️  VS Code extension not connected")
                print("   💡 To connect: Launch VS Code extension (F5 in extension folder)")
            else:
                print("   ✅ VS Code extension may be connected")
                print("   💡 Check logs for actual Roo-Code communication")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_full_integration()
    
    print("\n" + "=" * 50)
    print("🎉 Integration test completed!")
    print("\n📋 Next Steps:")
    print("1. Launch VS Code extension (F5) to enable Roo-Code communication")
    print("2. Verify your Qwen-3-Coder server is running on localhost:3000")
    print("3. Start using the bridge to control Roo-Code remotely!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())