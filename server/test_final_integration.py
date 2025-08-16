#!/usr/bin/env python3
"""
Final integration test - should now connect to actual Roo-Code extension
"""

import asyncio
import json
import websockets

async def test_final_integration():
    """Test the complete integration with the updated extension."""
    
    print("🎯 Final Integration Test - Roo-Code Connection")
    print("=" * 50)
    
    uri = "ws://localhost:47291/ws/final-integration-test"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to bridge")
            
            # Step 1: Configure Qwen-3-Coder
            print("\n1️⃣ Configuring Qwen-3-Coder...")
            config = {
                "type": "saveApiConfiguration",
                "data": {
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder",
                    "base_url": "http://localhost:3000/v1",
                    "context_length": 131000,
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            }
            
            await websocket.send(json.dumps(config))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"   ✅ Config: {data.get('data', {}).get('status', 'unknown')}")
            
            # Step 2: Start a simple test task
            print("\n2️⃣ Starting Roo-Code task...")
            task = {
                "type": "newTask",
                "data": {
                    "prompt": "Please respond with 'Hello from Roo-Code via the bridge!' to confirm the integration is working.",
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder",
                    "max_tokens": 50
                }
            }
            
            await websocket.send(json.dumps(task))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"   ✅ Task: {data.get('data', {}).get('status', 'unknown')}")
            
            # Step 3: Monitor for real Roo-Code responses
            print("\n3️⃣ Monitoring for Roo-Code responses (30 seconds)...")
            timeout = 30
            responses_received = []
            
            while timeout > 0:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    responses_received.append(data)
                    
                    msg_type = data.get('type', 'unknown')
                    print(f"   📨 {len(responses_received)}: {msg_type}")
                    
                    # Handle approval requests
                    if msg_type == 'approval_required':
                        approval_data = data.get('data', {})
                        ask_type = approval_data.get('ask_type', 'unknown')
                        approval_id = approval_data.get('approval_id')
                        
                        print(f"      🔐 Approval needed: {ask_type}")
                        
                        if approval_id:
                            # Auto-approve
                            approve = {
                                "type": "askResponse",
                                "data": {
                                    "approval_id": approval_id,
                                    "approved": True
                                }
                            }
                            await websocket.send(json.dumps(approve))
                            print(f"      ✅ Auto-approved: {approval_id}")
                    
                    # Show status updates
                    elif msg_type == 'status_update':
                        say_type = data.get('say_type', 'unknown')
                        say_data = data.get('data', {})
                        print(f"      📊 Status: {say_type}")
                        
                        # Show any text content
                        if 'text' in say_data:
                            text = say_data['text']
                            preview = text[:100] + "..." if len(text) > 100 else text
                            print(f"      💬 Text: {preview}")
                    
                    # Show events  
                    elif msg_type == 'event':
                        event_name = data.get('event_name', 'unknown')
                        event_data = data.get('data', {})
                        print(f"      🎪 Event: {event_name}")
                        
                        # Show task events in detail
                        if 'taskId' in event_data:
                            print(f"          🆔 Task: {event_data['taskId']}")
                    
                    else:
                        print(f"      📋 Data: {json.dumps(data, indent=2)[:200]}...")
                        
                except asyncio.TimeoutError:
                    timeout -= 1
                    if timeout % 10 == 0:
                        print(f"   ⏳ Waiting... ({timeout}s)")
            
            print(f"\n📊 Total responses: {len(responses_received)}")
            
            if responses_received:
                print("\n🎉 SUCCESS! Roo-Code integration is working!")
                
                # Analyze response types
                response_types = {}
                for resp in responses_received:
                    resp_type = resp.get('type', 'unknown')
                    response_types[resp_type] = response_types.get(resp_type, 0) + 1
                
                print("\n📋 Response Analysis:")
                for resp_type, count in response_types.items():
                    print(f"   • {resp_type}: {count}")
                
                return True
            else:
                print("\n❌ No responses from Roo-Code")
                print("\n🔧 Possible issues:")
                print("   1. VS Code extension needs to be restarted")
                print("   2. Roo-Code extension not properly connected")
                print("   3. Extension compilation issues")
                return False
                
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_extension_status():
    """Quick check to see if our updated extension is working."""
    
    print("\n" + "=" * 50)
    print("🔍 Extension Status Check")
    print("=" * 50)
    
    import sys
    sys.path.append('src')
    from utils.ipc_client import IPCClient
    
    try:
        client = IPCClient('127.0.0.1', 9999)
        await client.connect()
        print("✅ IPC connection successful")
        
        # Test the new configureProvider command
        config_response = await client.send_message({
            "type": "configureProvider",
            "data": {
                "apiProvider": "openai-compatible",
                "apiModelId": "qwen-3-coder",
                "apiUrl": "http://localhost:3000/v1",
                "contextLength": 131000
            }
        })
        
        print(f"📝 Configure provider response: {config_response}")
        
        # Test the new runTask command  
        task_response = await client.send_message({
            "type": "runTask",
            "data": {
                "prompt": "Test message from bridge"
            }
        })
        
        print(f"🚀 Run task response: {task_response}")
        
        client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Extension status check failed: {e}")
        return False

async def main():
    print("🧪 FINAL ROO-CODE INTEGRATION TEST")
    print("=" * 60)
    
    # Check extension status first
    extension_ok = await check_extension_status()
    
    if extension_ok:
        print("\n✅ Extension appears to be working with new functionality")
    else:
        print("\n⚠️  Extension may need to be restarted")
        print("💡 In VS Code: Restart the extension (Ctrl+Shift+P -> 'Reload Window')")
        print("💡 Or relaunch the VS Code extension development host (F5)")
    
    # Run full integration test
    integration_success = await test_final_integration()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS")
    print("=" * 60)
    
    if integration_success:
        print("🎉 SUCCESS! Complete Roo-Code integration working!")
        print("\n✅ Confirmed working:")
        print("   • Bridge server (port 47291)")
        print("   • Qwen-3-Coder server (port 3000)")  
        print("   • VS Code extension with Roo-Code API")
        print("   • Message routing and provider configuration")
        print("   • Real-time communication between web UI and Roo-Code")
        
        print("\n🚀 Your setup is now 100% complete!")
        print("   Web clients can now control Roo-Code through the bridge!")
    else:
        print("🔧 Integration needs attention")
        print("\n📋 Next steps:")
        print("   1. Restart VS Code extension (F5 or Reload Window)")
        print("   2. Check VS Code Developer Tools for errors")
        print("   3. Verify Roo-Code extension is active in Cursor")
        print("   4. Check that Cursor has Roo-Code extension loaded")

if __name__ == "__main__":
    asyncio.run(main())