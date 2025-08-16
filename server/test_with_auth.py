#!/usr/bin/env python3
"""
Test with authentication to see what the extension is actually doing
"""

import asyncio
import json
import sys

sys.path.append('src')
from utils.ipc_client import IPCClient

async def test_with_auth():
    """Test with proper authentication to see the actual capabilities."""
    
    print("🔑 Testing with Authentication")
    print("=" * 40)
    
    try:
        client = IPCClient('127.0.0.1', 9999)
        await client.connect()
        print("✅ Connected to IPC server")
        
        # First, let's try to authenticate
        print("\n🔐 Attempting authentication...")
        auth_response = await client.send_message({
            "type": "authenticate",
            "data": {
                "token": "test-token"
            }
        })
        print(f"📝 Auth response: {auth_response}")
        
        # If auth worked, try runTask
        if auth_response.get('type') != 'error':
            print("\n🚀 Testing runTask after auth...")
            task_response = await client.send_message({
                "type": "runTask",
                "data": {
                    "prompt": "Hello from the bridge!"
                }
            })
            print(f"📝 Task response: {task_response}")
            
            # Try the new configureProvider if available
            print("\n🔧 Testing configureProvider...")
            config_response = await client.send_message({
                "type": "configureProvider",
                "data": {
                    "apiProvider": "openai-compatible",
                    "apiModelId": "qwen-3-coder",
                    "apiUrl": "http://localhost:3000/v1"
                }
            })
            print(f"📝 Config response: {config_response}")
        
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

async def check_extension_logs():
    """Check what the extension is actually logging."""
    
    print("\n" + "=" * 40)
    print("📋 Extension Log Analysis")
    print("=" * 40)
    
    # We can check the bridge server logs to see what's happening
    print("💡 To check extension logs:")
    print("   1. In VS Code: View -> Output")
    print("   2. Select 'Roo-Code Bridge' from dropdown")
    print("   3. Look for connection and error messages")
    
    print("\n💡 To check if extension is using new code:")
    print("   1. Look for 'Connected to Roo-Code API successfully' message")
    print("   2. Check for any error messages about Roo-Code extension")
    
    # Let's also check what capabilities the extension is reporting
    try:
        client = IPCClient('127.0.0.1', 9999)
        await client.connect()
        
        # The welcome message should show capabilities
        print("\n📋 Extension capabilities from welcome message:")
        # This was shown when we connected - let's try a simple ping
        ping_response = await client.send_message({
            "type": "ping", 
            "data": {}
        })
        print(f"   Ping response: {ping_response}")
        
        client.disconnect()
        
    except Exception as e:
        print(f"   Error checking capabilities: {e}")

async def main():
    await test_with_auth()
    await check_extension_logs()
    
    print("\n" + "=" * 40)
    print("🎯 Next Steps")
    print("=" * 40)
    print("1. Check VS Code Output panel for 'Roo-Code Bridge' logs")
    print("2. Look for Roo-Code connection messages")
    print("3. If no Roo-Code connection, the extension may need debugging")
    print("4. The extension should log 'Connected to Roo-Code API successfully'")

if __name__ == "__main__":
    asyncio.run(main())