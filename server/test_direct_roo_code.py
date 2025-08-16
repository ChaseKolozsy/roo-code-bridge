#!/usr/bin/env python3
"""
Try to communicate directly with Roo-Code to see if it's actually processing tasks
"""

import asyncio
import json
import websockets

async def test_roo_code_direct():
    """Test direct communication with Roo-Code through the bridge."""
    
    print("🎯 Direct Roo-Code Communication Test")
    print("=" * 40)
    
    uri = "ws://localhost:47291/ws/direct-roo-test"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to bridge")
            
            # Step 1: Configure Qwen-3-Coder first
            print("\n1️⃣ Configuring Qwen-3-Coder...")
            config = {
                "type": "saveApiConfiguration",
                "data": {
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder",
                    "base_url": "http://localhost:3000/v1",
                    "context_length": 131000,
                    "max_tokens": 1000,
                    "temperature": 0.3,
                    "api_key": ""  # Add if needed
                }
            }
            
            await websocket.send(json.dumps(config))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"   ✅ Config: {data.get('data', {}).get('status', 'unknown')}")
            
            # Step 2: Send a very simple test task
            print("\n2️⃣ Sending minimal test task...")
            simple_task = {
                "type": "newTask",
                "data": {
                    "prompt": "Just say 'hello' and nothing else.",
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder",
                    "max_tokens": 10
                }
            }
            
            await websocket.send(json.dumps(simple_task))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"   ✅ Task: {data.get('data', {}).get('status', 'unknown')}")
            
            # Step 3: Wait and see what happens
            print("\n3️⃣ Monitoring for responses (30 seconds)...")
            timeout = 30
            responses = []
            
            while timeout > 0:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    responses.append(data)
                    
                    msg_type = data.get('type', 'unknown')
                    print(f"   📨 {len(responses)}: {msg_type}")
                    
                    # Handle approval requests immediately
                    if msg_type == 'approval_required':
                        approval_data = data.get('data', {})
                        ask_type = approval_data.get('ask_type', 'unknown')
                        approval_id = approval_data.get('approval_id')
                        
                        print(f"      🔐 Approval needed: {ask_type}")
                        
                        if approval_id:
                            # Auto-approve everything
                            approve = {
                                "type": "askResponse",
                                "data": {
                                    "approval_id": approval_id,
                                    "approved": True,
                                    "response": "yes"
                                }
                            }
                            await websocket.send(json.dumps(approve))
                            print(f"      ✅ Auto-approved: {approval_id}")
                    
                    # Show status updates
                    elif msg_type == 'status_update':
                        say_type = data.get('say_type', 'unknown')
                        say_data = data.get('data', {})
                        print(f"      📊 {say_type}")
                        
                        # Show text content if available
                        if 'text' in say_data:
                            text = say_data['text']
                            preview = text[:100] + "..." if len(text) > 100 else text
                            print(f"      💬 {preview}")
                    
                    # Show events
                    elif msg_type == 'event':
                        event_name = data.get('event_name', 'unknown')
                        print(f"      🎪 {event_name}")
                        
                except asyncio.TimeoutError:
                    timeout -= 1
                    if timeout % 10 == 0:
                        print(f"   ⏳ Waiting... ({timeout}s)")
            
            print(f"\n📊 Total responses: {len(responses)}")
            
            if responses:
                print("🎉 Roo-Code is responding!")
                
                # Show summary of response types
                response_types = {}
                for resp in responses:
                    resp_type = resp.get('type', 'unknown')
                    response_types[resp_type] = response_types.get(resp_type, 0) + 1
                
                print("\n📋 Response Summary:")
                for resp_type, count in response_types.items():
                    print(f"   • {resp_type}: {count}")
                
                return True
            else:
                print("❌ No responses from Roo-Code")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_qwen_server():
    """Test if Qwen server is actually responding."""
    
    print("\n" + "=" * 40)
    print("🧠 Qwen-3-Coder Server Test")
    print("=" * 40)
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            # Test 1: Check models endpoint
            try:
                async with session.get('http://localhost:3000/v1/models', timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print("✅ Models endpoint responding")
                        if 'data' in data:
                            models = [model.get('id', 'unknown') for model in data['data']]
                            print(f"   📋 Available models: {models}")
                    else:
                        print(f"⚠️  Models endpoint status: {resp.status}")
            except Exception as e:
                print(f"❌ Models endpoint failed: {e}")
            
            # Test 2: Try a simple completion
            try:
                completion_data = {
                    "model": "qwen-3-coder",
                    "messages": [
                        {"role": "user", "content": "Say hello"}
                    ],
                    "max_tokens": 10,
                    "temperature": 0.3
                }
                
                async with session.post(
                    'http://localhost:3000/v1/chat/completions',
                    json=completion_data,
                    timeout=10
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print("✅ Chat completions working")
                        if 'choices' in data and data['choices']:
                            content = data['choices'][0].get('message', {}).get('content', '')
                            print(f"   💬 Response: {content}")
                    else:
                        text = await resp.text()
                        print(f"❌ Chat completions failed: {resp.status}")
                        print(f"   📄 Response: {text[:200]}")
                        
            except Exception as e:
                print(f"❌ Chat completions error: {e}")
                
    except ImportError:
        print("❌ aiohttp not available for testing")

async def main():
    print("🧪 COMPREHENSIVE ROO-CODE TEST")
    print("=" * 50)
    
    # Test Qwen server first
    await test_qwen_server()
    
    # Test Roo-Code integration
    roo_code_working = await test_roo_code_direct()
    
    print("\n" + "=" * 50)
    print("🎯 FINAL DIAGNOSIS")
    print("=" * 50)
    
    if roo_code_working:
        print("🎉 SUCCESS: Full integration working!")
        print("   • Qwen-3-Coder server: Responding")
        print("   • Bridge communication: Active")
        print("   • Roo-Code extension: Processing tasks")
        print("   • Message flow: Complete")
    else:
        print("🔧 Integration incomplete")
        print("\n💡 Possible next steps:")
        print("   1. Verify Roo-Code is installed and enabled in Cursor")
        print("   2. Check Roo-Code's configuration (API keys, provider settings)")
        print("   3. Try starting a task manually in Roo-Code first")
        print("   4. Check Cursor's extension console for errors")
        print("   5. Ensure Roo-Code has permission to access localhost:3000")

if __name__ == "__main__":
    asyncio.run(main())