#!/usr/bin/env python3
"""
Test script to verify the new Roo-Code integration capabilities
"""
import socket
import json
import time

def test_new_capabilities():
    print("🔍 Testing New Roo-Code Integration Capabilities")
    print("=" * 50)
    
    try:
        # Connect to extension
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 9999))
        
        # Read welcome message
        data = sock.recv(4096).decode('utf-8')
        welcome = json.loads(data.strip())
        
        print("📋 Extension Capabilities:")
        capabilities = welcome.get('data', {}).get('capabilities', {})
        commands = capabilities.get('commands', [])
        
        for cmd in commands:
            print(f"   ✓ {cmd}")
        
        # Check for new commands
        new_commands = ['configureProvider', 'approvalResponse']
        print(f"\n🔍 Checking for new commands:")
        
        for cmd in new_commands:
            if cmd in commands:
                print(f"   ✅ {cmd} - FOUND")
            else:
                print(f"   ❌ {cmd} - MISSING")
        
        # Test configureProvider command
        print(f"\n🧪 Testing configureProvider command...")
        test_message = {
            "type": "command",
            "data": {
                "command": "configureProvider",
                "args": {
                    "provider": "openai-compatible",
                    "model": "qwen-3-coder",
                    "baseUrl": "http://localhost:3000/v1",
                    "contextLength": 131000
                }
            }
        }
        
        sock.send((json.dumps(test_message) + '\n').encode('utf-8'))
        
        # Wait for response
        time.sleep(1)
        response_data = sock.recv(4096).decode('utf-8')
        if response_data:
            response = json.loads(response_data.strip())
            print(f"   📨 Response: {response}")
        else:
            print(f"   ❌ No response received")
        
        sock.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_new_capabilities()