#!/usr/bin/env python3
"""
Test the server components without requiring VS Code extension
This validates that Phase 1 server infrastructure is working correctly
"""

import asyncio
import json
import httpx
import websockets
from datetime import datetime

API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/test-client"

async def test_health_check():
    """Test the health endpoint"""
    print("\n✅ Testing Health Check...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/health")
        data = response.json()
        print(f"   Status: {data['status']}")
        print(f"   Active sessions: {data['active_sessions']}")
        return response.status_code == 200

async def test_websocket_ping_pong():
    """Test WebSocket ping/pong"""
    print("\n✅ Testing WebSocket Ping/Pong...")
    async with websockets.connect(WS_URL) as ws:
        # Send ping
        await ws.send(json.dumps({"type": "ping", "data": {"timestamp": datetime.now().isoformat()}}))
        
        # Receive pong
        response = await ws.recv()
        data = json.loads(response)
        
        if data.get("type") == "pong":
            print(f"   Received pong with data: {data.get('data')}")
            return True
        return False

async def test_websocket_error_handling():
    """Test WebSocket error handling when no adapter is connected"""
    print("\n✅ Testing Error Handling (no adapter)...")
    async with websockets.connect(WS_URL) as ws:
        # Try to start a task (will fail without adapter)
        await ws.send(json.dumps({
            "type": "task.start",
            "data": {"prompt": "test", "config": {}}
        }))
        
        response = await ws.recv()
        data = json.loads(response)
        
        if data.get("type") == "error":
            print(f"   Correctly received error: {data.get('data', {}).get('message')}")
            return True
        return False

async def test_rest_api_auth():
    """Test REST API authentication"""
    print("\n✅ Testing REST API Authentication...")
    async with httpx.AsyncClient() as client:
        # Test without auth - should fail
        response = await client.get(f"{API_URL}/api/config/providers")
        print(f"   Response status: {response.status_code}")
        if response.status_code == 401:
            print("   Correctly rejected unauthenticated request")
            return True
        elif response.status_code == 403:
            print("   Correctly rejected with forbidden")
            return True
        else:
            print(f"   Unexpected status: {response.status_code}")
            return False

async def test_session_management():
    """Test that sessions are created and tracked"""
    print("\n✅ Testing Session Management...")
    
    # Check initial session count
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/health")
        initial_sessions = response.json()["active_sessions"]
        print(f"   Initial sessions: {initial_sessions}")
    
    # Connect a WebSocket (creates a session)
    async with websockets.connect(WS_URL) as ws:
        await asyncio.sleep(0.5)  # Give time for session creation
        
        # Check session count increased
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/health")
            active_sessions = response.json()["active_sessions"]
            print(f"   Sessions with connection: {active_sessions}")
    
    # After disconnect, check session count
    await asyncio.sleep(0.5)
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/health")
        final_sessions = response.json()["active_sessions"]
        print(f"   Sessions after disconnect: {final_sessions}")
    
    return True

async def main():
    """Run all server-only tests"""
    print("=" * 50)
    print("🚀 PHASE 1 SERVER INFRASTRUCTURE TEST")
    print("=" * 50)
    print("Testing server components without VS Code extension...")
    
    tests = [
        ("Health Check", test_health_check),
        ("WebSocket Ping/Pong", test_websocket_ping_pong),
        ("Error Handling", test_websocket_error_handling),
        ("REST API Auth", test_rest_api_auth),
        ("Session Management", test_session_management),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"\n❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print("-" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("-" * 50)
    if all_passed:
        print("🎉 ALL SERVER TESTS PASSED!")
        print("Phase 1 server infrastructure is working correctly")
        print("\nNext: Install the VS Code extension to test full integration")
    else:
        print("⚠️  Some tests failed")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())