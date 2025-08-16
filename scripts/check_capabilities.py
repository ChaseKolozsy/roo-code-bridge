#!/usr/bin/env python3
"""
Check Roo-Code capabilities and find the right message format
"""
import socket
import json
import time

def check_capabilities():
    print("🔍 CHECKING ROO-CODE CAPABILITIES")
    print("=" * 60)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect(('127.0.0.1', 9999))
        
        # Read the welcome message
        data = sock.recv(4096).decode('utf-8')
        print("📨 Welcome message:")
        try:
            welcome = json.loads(data.strip())
            print(json.dumps(welcome, indent=2))
            
            capabilities = welcome.get('data', {}).get('capabilities', {})
            commands = capabilities.get('commands', [])
            
            print(f"\n📋 Available commands: {commands}")
            
            # Check if there are user input related commands
            user_commands = [cmd for cmd in commands if 'message' in cmd.lower() or 'send' in cmd.lower() or 'input' in cmd.lower()]
            print(f"💬 Message-related commands: {user_commands}")
            
        except Exception as e:
            print(f"Raw welcome: {data}")
            print(f"Parse error: {e}")
        
        sock.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_capabilities()