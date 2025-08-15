#!/usr/bin/env python3
"""
Phase 1 Integration Test Suite
Tests the core infrastructure: VS Code extension IPC + WebSocket server + REST API
"""

import asyncio
import json
import socket
import httpx
import websockets
from typing import Dict, Any

# Configuration
IPC_HOST = "127.0.0.1"
IPC_PORT = 9999
API_HOST = "localhost"
API_PORT = 8000
WS_URL = f"ws://{API_HOST}:{API_PORT}/ws/test-client"
API_URL = f"http://{API_HOST}:{API_PORT}"

async def test_ipc_connection():
    """Test direct connection to VS Code extension IPC server"""
    print("\n🔍 Testing IPC Connection to VS Code Extension...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((IPC_HOST, IPC_PORT))
        print("   ✅ Connected to IPC server")
        
        # Send ping
        message = json.dumps({"type": "ping"}) + "\n"
        sock.send(message.encode())
        
        # Receive response
        response = sock.recv(1024).decode()
        print(f"   📨 Received: {response[:100]}")
        sock.close()
        return True
    except Exception as e:
        print(f"   ❌ IPC connection failed: {e}")
        return False

async def test_websocket_connection():
    """Test WebSocket connection to the bridge server"""
    print("\n🔍 Testing WebSocket Connection...")
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("   ✅ Connected to WebSocket server")
            
            # Send a test message
            await websocket.send(json.dumps({
                "type": "ping",
                "data": {"test": True}
            }))
            
            # Wait for response (with timeout)
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            print(f"   📨 Received: {data}")
            return True
    except Exception as e:
        print(f"   ❌ WebSocket connection failed: {e}")
        return False

async def test_rest_api():
    """Test REST API endpoints"""
    print("\n🔍 Testing REST API Endpoints...")
    
    async with httpx.AsyncClient() as client:
        # Test health endpoint
        try:
            response = await client.get(f"{API_URL}/health")
            if response.status_code == 200:
                print(f"   ✅ Health check: {response.json()}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ API connection failed: {e}")
            return False
        
        # Test authentication and get token
        try:
            # For demo purposes, using simple auth
            token = "demo-token"
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test providers endpoint
            response = await client.get(f"{API_URL}/api/config/providers", headers=headers)
            if response.status_code in [200, 401]:
                print(f"   ✅ Providers endpoint responsive")
            
            return True
        except Exception as e:
            print(f"   ❌ API test failed: {e}")
            return False

async def test_full_flow():
    """Test a complete flow: API -> WebSocket -> IPC -> VS Code"""
    print("\n🔍 Testing Full Integration Flow...")
    
    try:
        # 1. Connect to WebSocket
        async with websockets.connect(WS_URL) as websocket:
            print("   ✅ WebSocket connected")
            
            # 2. Send task start message
            await websocket.send(json.dumps({
                "type": "task.start",
                "data": {
                    "prompt": "Test task from integration test",
                    "config": {"model": "test"}
                }
            }))
            
            # 3. Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            print(f"   📨 Task response: {data.get('type')}")
            
            # 4. Send a message
            await websocket.send(json.dumps({
                "type": "message.send",
                "data": {
                    "content": "Hello from integration test"
                }
            }))
            
            # 5. Receive stream response
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            print(f"   📨 Message response: {data.get('type')}")
            
            print("   ✅ Full flow completed successfully")
            return True
            
    except Exception as e:
        print(f"   ❌ Full flow test failed: {e}")
        return False

async def main():
    """Run all Phase 1 tests"""
    print("=" * 50)
    print("🚀 PHASE 1 INTEGRATION TEST SUITE")
    print("=" * 50)
    
    results = {
        "IPC Connection": await test_ipc_connection(),
        "WebSocket Connection": await test_websocket_connection(),
        "REST API": await test_rest_api(),
        "Full Flow": await test_full_flow()
    }
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print("-" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("-" * 50)
    if all_passed:
        print("🎉 ALL PHASE 1 TESTS PASSED!")
        print("Core infrastructure is working correctly")
    else:
        print("⚠️  Some tests failed. Please check:")
        print("   1. VS Code is running with the extension")
        print("   2. The FastAPI server is running (python src/main.py)")
        print("   3. All ports are available (9999 for IPC, 8000 for API)")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())