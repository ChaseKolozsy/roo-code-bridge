#!/usr/bin/env python3
"""
Test IPC with the correct protocol based on the welcome message
"""

import asyncio
import json
import sys

sys.path.append('src')
from utils.ipc_client import IPCClient

async def test_correct_ipc_protocol():
    """Test using the correct IPC protocol."""
    
    print("🎯 Testing Correct IPC Protocol")
    print("=" * 40)
    
    try:
        client = IPCClient('127.0.0.1', 9999)
        await client.connect()
        print("✅ Connected to IPC server")
        
        # Test 1: Try the runTask command (this should work with our extension)
        print("\n📝 Test 1: Running a task...")
        task_message = {
            "type": "runTask",
            "data": {
                "prompt": "Hello from the bridge! Please create a simple Python function that adds two numbers.",
                "config": {
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder",
                    "base_url": "http://localhost:3000/v1",
                    "max_tokens": 1000
                }
            }
        }
        
        response = await client.send_message(task_message)
        print(f"📥 Task response: {json.dumps(response, indent=2)}")
        
        # Test 2: Try execute command
        print("\n💻 Test 2: Execute command...")
        execute_message = {
            "type": "execute",
            "data": {
                "command": "echo 'Hello from bridge'",
                "cwd": "/tmp"
            }
        }
        
        response = await client.send_message(execute_message)
        print(f"📥 Execute response: {json.dumps(response, indent=2)}")
        
        # Test 3: List files
        print("\n📁 Test 3: List files...")
        list_message = {
            "type": "listFiles",
            "data": {
                "path": "."
            }
        }
        
        response = await client.send_message(list_message)
        print(f"📥 List files response: {json.dumps(response, indent=2)}")
        
        client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ IPC test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_through_bridge():
    """Test Roo-Code integration through the bridge."""
    
    print("\n" + "=" * 40)
    print("🌉 Testing Roo-Code Integration Through Bridge")
    print("=" * 40)
    
    import websockets
    
    try:
        uri = "ws://localhost:47291/ws/roo-code-integration-test"
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to bridge")
            
            # First, configure Qwen-3-Coder
            print("\n🔧 Configuring Qwen-3-Coder...")
            config = {
                "type": "saveApiConfiguration",
                "data": {
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder", 
                    "base_url": "http://localhost:3000/v1",
                    "context_length": 131000,
                    "max_tokens": 2048,
                    "temperature": 0.7
                }
            }
            
            await websocket.send(json.dumps(config))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✅ Config: {data.get('data', {}).get('status', 'unknown')}")
            
            # Now try to start a task that should reach Roo-Code
            print("\n🚀 Starting Roo-Code task...")
            task = {
                "type": "newTask",
                "data": {
                    "prompt": "Create a Python function that calculates the Fibonacci sequence up to n terms. Include proper documentation and error handling.",
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder"
                }
            }
            
            await websocket.send(json.dumps(task))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✅ Task: {data.get('data', {}).get('status', 'unknown')}")
            
            # Listen for any messages from Roo-Code
            print("\n👂 Listening for Roo-Code messages (15 seconds)...")
            timeout = 15
            received_messages = []
            
            while timeout > 0:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    received_messages.append(data)
                    
                    msg_type = data.get('type', 'unknown')
                    print(f"📨 {len(received_messages)}: {msg_type}")
                    
                    # Show approval requests in detail
                    if msg_type == 'approval_required':
                        ask_type = data.get('data', {}).get('ask_type', 'unknown')
                        print(f"   🔐 Approval needed: {ask_type}")
                        
                        # Auto-approve for testing
                        approval_id = data.get('data', {}).get('approval_id')
                        if approval_id:
                            approval = {
                                "type": "askResponse",
                                "data": {
                                    "approval_id": approval_id,
                                    "approved": True
                                }
                            }
                            await websocket.send(json.dumps(approval))
                            print(f"   ✅ Auto-approved: {approval_id}")
                    
                    # Show status updates
                    elif msg_type == 'status_update':
                        say_type = data.get('say_type', 'unknown')
                        print(f"   📊 Status: {say_type}")
                        
                except asyncio.TimeoutError:
                    timeout -= 1
                    if timeout % 5 == 0:
                        print(f"   ⏳ Still listening... ({timeout}s)")
            
            print(f"\n📊 Received {len(received_messages)} messages total")
            
            if received_messages:
                print("✅ Roo-Code is responding through the bridge!")
                return True
            else:
                print("❓ No Roo-Code responses - check Roo-Code configuration")
                return False
                
    except Exception as e:
        print(f"❌ Bridge test failed: {e}")
        return False

async def main():
    print("🧪 ROO-CODE IPC INTEGRATION TEST")
    print("=" * 50)
    
    # Test 1: Direct IPC with correct protocol
    ipc_success = await test_correct_ipc_protocol()
    
    # Test 2: Through bridge to Roo-Code
    bridge_success = await test_through_bridge()
    
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    print(f"IPC Protocol:     {'✅ WORKING' if ipc_success else '❌ FAILED'}")
    print(f"Roo-Code Bridge:  {'✅ WORKING' if bridge_success else '❌ NEEDS SETUP'}")
    
    if ipc_success and bridge_success:
        print("\n🎉 SUCCESS! Roo-Code integration is fully working!")
    elif ipc_success:
        print("\n⚠️  IPC works but Roo-Code not responding")
        print("💡 Check: Is Roo-Code extension properly configured?")
    else:
        print("\n❌ IPC connection issues")
        print("💡 Check: Is the VS Code extension running?")

if __name__ == "__main__":
    asyncio.run(main())