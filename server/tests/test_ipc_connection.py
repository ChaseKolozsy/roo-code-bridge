#!/usr/bin/env python3
"""
Test IPC connection to Roo-Code server
"""

import asyncio
import json
import sys
import socket

sys.path.append('src')
from utils.ipc_client import IPCClient

async def test_ipc_direct():
    """Test direct IPC connection to Roo-Code."""
    
    print("🔌 Testing IPC Connection to Roo-Code")
    print("=" * 40)
    
    # Test if port 9999 is listening
    print("1️⃣ Checking if port 9999 is listening...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 9999))
        sock.close()
        
        if result == 0:
            print("✅ Port 9999 is listening!")
        else:
            print("❌ Port 9999 is not listening")
            print("💡 Make sure Roo-Code extension is running in VS Code")
            return False
    except Exception as e:
        print(f"❌ Port check failed: {e}")
        return False
    
    # Test IPC client connection
    print("\n2️⃣ Testing IPC client connection...")
    try:
        client = IPCClient('127.0.0.1', 9999)
        connected = await client.connect()
        
        if connected:
            print("✅ IPC client connected successfully!")
            
            # Test sending a message
            print("\n3️⃣ Testing message sending...")
            test_message = {
                "type": "ping",
                "data": {"message": "test from bridge"}
            }
            
            response = await client.send_message(test_message)
            print(f"📤 Sent: {test_message}")
            print(f"📥 Response: {response}")
            
            client.disconnect()
            return True
        else:
            print("❌ IPC client failed to connect")
            return False
            
    except Exception as e:
        print(f"❌ IPC connection error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_via_websocket():
    """Test IPC via WebSocket bridge connection."""
    
    print("\n" + "=" * 40)
    print("🌐 Testing via WebSocket Bridge")
    print("=" * 40)
    
    import websockets
    
    uri = "ws://localhost:47291/ws/ipc-test-client"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to bridge WebSocket")
            
            # Configure Qwen first
            config = {
                "type": "saveApiConfiguration", 
                "data": {
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder",
                    "base_url": "http://localhost:3000/v1",
                    "context_length": 131000
                }
            }
            
            await websocket.send(json.dumps(config))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📝 Config result: {data.get('data', {}).get('status', 'unknown')}")
            
            # Try to start a task (this will test IPC)
            task = {
                "type": "newTask",
                "data": {
                    "prompt": "Hello from the bridge! Please respond with a simple greeting.",
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder"
                }
            }
            
            await websocket.send(json.dumps(task))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"🚀 Task result: {data.get('data', {}).get('status', 'unknown')}")
            
            # Listen for any responses from Roo-Code
            print("\n👂 Listening for Roo-Code responses (10 seconds)...")
            timeout = 10
            messages_received = 0
            
            while timeout > 0:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    messages_received += 1
                    
                    print(f"📨 Message {messages_received}: {data.get('type', 'unknown')}")
                    if 'data' in data:
                        print(f"   Data: {json.dumps(data['data'], indent=2)}")
                        
                except asyncio.TimeoutError:
                    timeout -= 1
                    if timeout % 3 == 0:
                        print(f"   ⏳ Waiting... ({timeout}s)")
            
            if messages_received > 0:
                print(f"✅ Received {messages_received} messages from Roo-Code!")
                return True
            else:
                print("❓ No messages received - check if Roo-Code is processing")
                return False
                
    except Exception as e:
        print(f"❌ WebSocket test error: {e}")
        return False

async def main():
    print("🧪 IPC CONNECTION TEST")
    print("=" * 50)
    
    # Test 1: Direct IPC
    ipc_success = await test_ipc_direct()
    
    # Test 2: Via WebSocket
    ws_success = await test_via_websocket()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Direct IPC:      {'✅ PASS' if ipc_success else '❌ FAIL'}")
    print(f"WebSocket Bridge: {'✅ PASS' if ws_success else '❌ FAIL'}")
    
    if ipc_success and ws_success:
        print("\n🎉 All tests passed! Bridge is fully connected to Roo-Code!")
    elif ipc_success:
        print("\n⚠️  IPC works but no Roo-Code responses - check Roo-Code server")
    else:
        print("\n❌ IPC connection failed - check VS Code extension")
        print("\n🔧 Troubleshooting:")
        print("   1. Open roo-code-bridge/extension in VS Code")
        print("   2. Press F5 to launch extension")
        print("   3. Check VS Code extension logs")
        print("   4. Verify extension is running and connected")

if __name__ == "__main__":
    asyncio.run(main())