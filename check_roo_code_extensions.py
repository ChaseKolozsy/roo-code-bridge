#!/usr/bin/env python3
"""
Check what Roo-Code related extensions are installed
"""
import socket
import json
import time

def check_roo_code_extensions():
    print("🔍 CHECKING FOR ROO-CODE EXTENSIONS")
    print("=" * 50)
    
    try:
        # Connect and authenticate
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 9999))
        
        # Read welcome and authenticate
        data = sock.recv(4096).decode('utf-8')
        
        auth_message = {
            "type": "authenticate",
            "data": {"apiKey": "test-key-123"}
        }
        sock.send((json.dumps(auth_message) + '\n').encode('utf-8'))
        time.sleep(1)
        sock.recv(4096)  # consume auth response
        
        # Try to get extension information
        info_message = {
            "type": "execute",
            "data": {
                "command": "code",
                "args": ["--list-extensions"]
            }
        }
        
        sock.send((json.dumps(info_message) + '\n').encode('utf-8'))
        time.sleep(2)
        
        response_data = sock.recv(4096).decode('utf-8')
        if response_data.strip():
            response = json.loads(response_data.strip())
            print(f"📋 Extensions list response: {response}")
        
        sock.close()
        
    except Exception as e:
        print(f"❌ Error checking extensions: {e}")

if __name__ == "__main__":
    check_roo_code_extensions()