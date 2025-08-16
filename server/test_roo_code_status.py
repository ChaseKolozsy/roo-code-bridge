#!/usr/bin/env python3
"""
Check if Roo-Code extension is actually loaded and running
"""

import asyncio
import json
import websockets

async def check_roo_code_status():
    """Check if we can determine Roo-Code's status."""
    
    print("🔍 Checking Roo-Code Extension Status")
    print("=" * 40)
    
    # Test if we can communicate with the real Roo-Code through our bridge
    uri = "ws://localhost:47291/ws/roo-code-status-check"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to bridge")
            
            # Configure the provider we want to use
            print("\n🔧 Setting up Qwen-3-Coder configuration...")
            config = {
                "type": "saveApiConfiguration",
                "data": {
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder",
                    "base_url": "http://localhost:3000/v1",
                    "context_length": 131000,
                    "max_tokens": 2048,
                    "temperature": 0.7,
                    "api_key": ""  # Add if your server needs one
                }
            }
            
            await websocket.send(json.dumps(config))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✅ Configuration: {data.get('data', {}).get('status', 'unknown')}")
            
            # Try to start a very simple task
            print("\n🎯 Testing simple task to check Roo-Code response...")
            simple_task = {
                "type": "newTask",
                "data": {
                    "prompt": "Hello! Please respond with 'Hello from Roo-Code' to confirm you're working.",
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder",
                    "max_tokens": 50
                }
            }
            
            await websocket.send(json.dumps(simple_task))
            response = await websocket.recv()
            data = json.loads(response)
            task_status = data.get('data', {}).get('status', 'unknown')
            print(f"✅ Task started: {task_status}")
            
            # Listen for any response
            print("\n👂 Listening for any Roo-Code activity (20 seconds)...")
            timeout = 20
            activity_detected = False
            
            while timeout > 0:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    
                    activity_detected = True
                    msg_type = data.get('type', 'unknown')
                    
                    print(f"🎉 ACTIVITY DETECTED: {msg_type}")
                    
                    if msg_type == 'approval_required':
                        print("   🔐 Approval request received!")
                        ask_type = data.get('data', {}).get('ask_type', 'unknown')
                        print(f"   📋 Type: {ask_type}")
                        
                        # Auto-approve to continue the flow
                        approval_id = data.get('data', {}).get('approval_id')
                        if approval_id:
                            approve_msg = {
                                "type": "askResponse",
                                "data": {
                                    "approval_id": approval_id,
                                    "approved": True
                                }
                            }
                            await websocket.send(json.dumps(approve_msg))
                            print("   ✅ Auto-approved")
                    
                    elif msg_type == 'status_update':
                        say_type = data.get('say_type', 'unknown')
                        content = data.get('data', {})
                        print(f"   📊 Status: {say_type}")
                        if 'text' in content:
                            text_preview = content['text'][:100] + "..." if len(content['text']) > 100 else content['text']
                            print(f"   💬 Content: {text_preview}")
                    
                    elif msg_type == 'event':
                        event_name = data.get('event_name', 'unknown')
                        print(f"   🎪 Event: {event_name}")
                    
                    else:
                        print(f"   📨 Data: {json.dumps(data, indent=2)[:200]}...")
                        
                except asyncio.TimeoutError:
                    timeout -= 1
                    if timeout % 5 == 0 and not activity_detected:
                        print(f"   ⏳ Still waiting... ({timeout}s)")
            
            if activity_detected:
                print("\n🎉 SUCCESS: Roo-Code is active and responding!")
                return True
            else:
                print("\n❓ No Roo-Code activity detected")
                return False
                
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

async def check_server_status():
    """Check the status of all components."""
    
    print("\n" + "=" * 40)
    print("🔧 Component Status Check")
    print("=" * 40)
    
    # Check 1: Bridge server
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:47291/health') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ Bridge Server: Healthy")
                    print(f"   📊 Active sessions: {data.get('active_sessions', 0)}")
                else:
                    print("❌ Bridge Server: Unhealthy")
    except Exception as e:
        print(f"❌ Bridge Server: Failed ({e})")
    
    # Check 2: Qwen server
    try:
        async with aiohttp.ClientSession() as session:
            # Try to check if Qwen server is responding
            async with session.get('http://localhost:3000/v1/models', timeout=5) as resp:
                if resp.status == 200:
                    print("✅ Qwen-3-Coder Server: Responding")
                else:
                    print(f"⚠️  Qwen-3-Coder Server: Status {resp.status}")
    except Exception as e:
        print(f"❓ Qwen-3-Coder Server: Cannot verify ({e})")
    
    # Check 3: IPC connection
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 9999))
        sock.close()
        
        if result == 0:
            print("✅ IPC Port 9999: Listening")
        else:
            print("❌ IPC Port 9999: Not available")
    except Exception as e:
        print(f"❌ IPC Port 9999: Error ({e})")

async def main():
    print("🧪 ROO-CODE STATUS CHECK")
    print("=" * 50)
    
    # Check server components
    await check_server_status()
    
    # Check Roo-Code integration
    roo_code_active = await check_roo_code_status()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if roo_code_active:
        print("🎉 SUCCESS: Roo-Code integration is working!")
        print("\n✅ Your setup is ready:")
        print("   • Bridge server: Running on port 47291")
        print("   • Qwen-3-Coder: Configured as provider")
        print("   • Roo-Code: Active and responding")
        print("   • Message routing: Functional")
    else:
        print("⚠️  Roo-Code integration needs attention")
        print("\n🔧 Possible issues:")
        print("   1. Roo-Code extension not loaded in Cursor")
        print("   2. Roo-Code not configured with API key")
        print("   3. Roo-Code waiting for user approval")
        print("   4. Network connectivity to Qwen server")
        
        print("\n💡 Next steps:")
        print("   1. Check Cursor extensions panel")
        print("   2. Verify Roo-Code extension is enabled")
        print("   3. Configure Roo-Code with your API settings")
        print("   4. Test Roo-Code directly in Cursor first")

if __name__ == "__main__":
    asyncio.run(main())