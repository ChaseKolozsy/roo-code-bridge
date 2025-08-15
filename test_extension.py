#!/usr/bin/env python3
"""
Simple test to check if VS Code extension IPC server is running
"""

import socket
import json

def test_ipc_connection():
    print("Testing IPC connection to VS Code extension...")
    print("="*50)
    
    try:
        # Try to connect to the IPC server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(('127.0.0.1', 9999))
        print("✅ Connected to IPC server on port 9999!")
        
        # Send a ping message
        message = json.dumps({"type": "ping", "data": {"test": True}}) + "\n"
        sock.send(message.encode())
        print("📤 Sent ping message")
        
        # Try to receive welcome message or response
        response = sock.recv(1024).decode()
        print(f"📥 Received: {response[:200]}")
        
        sock.close()
        print("\n✅ IPC server is running and responsive!")
        
    except ConnectionRefusedError:
        print("❌ Connection refused on port 9999")
        print("\nPlease make sure to:")
        print("1. Open VS Code/Cursor")
        print("2. Open Command Palette (Cmd+Shift+P)")
        print("3. Run: 'Roo-Code Bridge: Start Server'")
        print("4. Look for notification: 'Roo-Code Bridge server started on 127.0.0.1:9999'")
        
    except socket.timeout:
        print("❌ Connection timed out")
        print("The port might be open but not responding")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("="*50)

if __name__ == "__main__":
    test_ipc_connection()