#!/usr/bin/env python3
"""
Test raw TCP connection to port 9999 to understand the protocol
"""

import asyncio
import json
import socket

async def test_raw_tcp():
    """Test raw TCP connection to see what Roo-Code expects."""
    
    print("🔌 Testing Raw TCP Connection to Port 9999")
    print("=" * 50)
    
    try:
        # Create TCP connection
        reader, writer = await asyncio.open_connection('127.0.0.1', 9999)
        print("✅ TCP connection established!")
        
        # Try to read initial message (if any)
        print("\n📥 Waiting for initial message from server...")
        try:
            data = await asyncio.wait_for(reader.read(1024), timeout=3.0)
            if data:
                print(f"📨 Received: {data.decode('utf-8', errors='ignore')}")
            else:
                print("📭 No initial message")
        except asyncio.TimeoutError:
            print("⏰ No initial message (timeout)")
        
        # Try sending a simple message
        print("\n📤 Sending test message...")
        test_messages = [
            '{"type": "ping", "data": {}}\n',
            'ping\n',
            'hello\n',
            '{"command": "ping"}\n'
        ]
        
        for i, msg in enumerate(test_messages, 1):
            print(f"\n🔄 Test {i}: Sending '{msg.strip()}'")
            writer.write(msg.encode())
            await writer.drain()
            
            # Try to read response
            try:
                response = await asyncio.wait_for(reader.read(1024), timeout=2.0)
                if response:
                    print(f"✅ Response: {response.decode('utf-8', errors='ignore')}")
                else:
                    print("📭 No response")
            except asyncio.TimeoutError:
                print("⏰ No response (timeout)")
        
        # Close connection
        writer.close()
        await writer.wait_closed()
        print("\n🔌 Connection closed")
        
    except Exception as e:
        print(f"❌ TCP test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_our_ipc_client():
    """Test our IPC client with more debugging."""
    
    print("\n" + "=" * 50)
    print("🔍 Testing Our IPC Client with Debug Info")
    print("=" * 50)
    
    import sys
    sys.path.append('src')
    from utils.ipc_client import IPCClient
    
    try:
        client = IPCClient('127.0.0.1', 9999)
        
        # Let's look at the connect method
        print("📡 Attempting IPC client connection...")
        
        # Override the connect method to add debugging
        original_connect = client.connect
        
        async def debug_connect():
            try:
                print("🔌 Opening connection...")
                client.reader, client.writer = await asyncio.open_connection(
                    client.host, client.port
                )
                print("✅ TCP connection established!")
                
                # Try to read welcome message
                print("📥 Waiting for welcome message...")
                try:
                    data = await asyncio.wait_for(client.reader.readuntil(b'\n'), timeout=5.0)
                    welcome_msg = data.decode().strip()
                    print(f"📨 Welcome: {welcome_msg}")
                    
                    # Try to parse as JSON
                    try:
                        welcome_data = json.loads(welcome_msg)
                        print(f"✅ Parsed welcome: {json.dumps(welcome_data, indent=2)}")
                        return True
                    except json.JSONDecodeError:
                        print(f"⚠️  Welcome not JSON: {welcome_msg}")
                        return False
                        
                except asyncio.TimeoutError:
                    print("⏰ No welcome message received")
                    return False
                    
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return False
        
        client.connect = debug_connect
        connected = await client.connect()
        
        if connected:
            print("🎉 IPC client connected successfully!")
        else:
            print("❌ IPC client connection failed")
            
        # Clean up
        if hasattr(client, 'writer') and client.writer:
            client.writer.close()
            await client.writer.wait_closed()
            
    except Exception as e:
        print(f"❌ IPC client test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_raw_tcp()
    await test_our_ipc_client()
    
    print("\n" + "=" * 50)
    print("💡 Next Steps:")
    print("   1. Check if we need to adjust our IPC protocol")
    print("   2. Verify Roo-Code extension is properly loaded")
    print("   3. Look at Roo-Code's IPC server implementation")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())