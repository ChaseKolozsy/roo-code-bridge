#!/usr/bin/env python3
"""
Test actual Roo-Code API integration WITH AUTHENTICATION
"""
import socket
import json
import time

def test_roo_code_api_with_auth():
    print("🔍 TESTING ROO-CODE API WITH AUTHENTICATION")
    print("=" * 60)
    
    try:
        # Connect to our extension
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 9999))
        
        # Read welcome message
        data = sock.recv(4096).decode('utf-8')
        print(f"📋 Extension connected: {json.loads(data.strip())['type']}")
        
        # STEP 1: Authenticate first!
        print("\n🔐 STEP 1: Authenticating with extension...")
        auth_message = {
            "type": "authenticate",
            "data": {
                "apiKey": "test-key-123"  # Any non-empty key works
            }
        }
        
        sock.send((json.dumps(auth_message) + '\n').encode('utf-8'))
        time.sleep(1)
        
        auth_response_data = sock.recv(4096).decode('utf-8')
        if auth_response_data.strip():
            auth_response = json.loads(auth_response_data.strip())
            print(f"   📨 Auth Response: {auth_response}")
            
            if auth_response.get('type') == 'authenticated':
                print("   ✅ Authentication SUCCESS")
            else:
                print("   ❌ Authentication FAILED")
                return False
        
        # STEP 2: Test configureProvider (now authenticated)
        print("\n🧪 STEP 2: Configuring Roo-Code provider...")
        config_message = {
            "type": "configureProvider",
            "data": {
                "provider": "openai-compatible",
                "model": "qwen-3-coder",
                "baseUrl": "http://localhost:3000/v1",
                "contextLength": 131000
            }
        }
        
        sock.send((json.dumps(config_message) + '\n').encode('utf-8'))
        time.sleep(2)
        
        response_data = sock.recv(4096).decode('utf-8')
        if response_data.strip():
            response = json.loads(response_data.strip())
            print(f"   📨 Config Response: {response}")
            
            if response.get('success') == True:
                print("   ✅ Provider configuration SUCCESS")
            elif 'Roo-Code API not available' in str(response):
                print("   ❌ Roo-Code extension not found - this is the real test!")
                print("   💡 Extension ID 'saoudrizwan.claude-dev' not found or not activated")
                return False
            else:
                print(f"   ⚠️  Config response: {response}")
        
        # STEP 3: Test runTask (the ultimate test)
        print("\n🧪 STEP 3: Testing Roo-Code task execution...")
        task_message = {
            "type": "runTask", 
            "data": {
                "prompt": "Hello from the Roo-Code Bridge! Please respond to confirm the bridge is working.",
                "config": {
                    "apiProvider": "openai-compatible",
                    "apiModelId": "qwen-3-coder", 
                    "apiUrl": "http://localhost:3000/v1",
                    "contextLength": 131000
                }
            }
        }
        
        sock.send((json.dumps(task_message) + '\n').encode('utf-8'))
        time.sleep(5)  # Give more time for Roo-Code to respond
        
        task_response_data = sock.recv(4096).decode('utf-8')
        if task_response_data.strip():
            task_response = json.loads(task_response_data.strip())
            print(f"   📨 Task Response: {task_response}")
            
            if task_response.get('success'):
                print("   🎉 ROO-CODE TASK EXECUTION SUCCESS!")
                print("   ✅ THE BRIDGE IS FULLY WORKING WITH REAL ROO-CODE!")
                if task_response.get('taskId'):
                    print(f"   🆔 Task ID: {task_response.get('taskId')}")
                return True
            else:
                error = task_response.get('error', 'Unknown error')
                print(f"   ❌ Roo-Code task FAILED: {error}")
                
                if 'Roo-Code API not available' in error:
                    print("   💡 This means the Roo-Code extension is not properly connected")
                    print("   🔧 Check: Is Roo-Code extension installed and activated?")
                return False
        else:
            print("   ❌ No task response received")
            return False
        
        sock.close()
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_roo_code_api_with_auth()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 FINAL RESULT: ROO-CODE BRIDGE IS FULLY WORKING!")
        print("✅ Authentication works")
        print("✅ Extension connects to real Roo-Code")  
        print("✅ Tasks can be sent through the bridge")
    else:
        print("❌ FINAL RESULT: Bridge has integration issues")
        print("🔧 The extension cannot properly communicate with Roo-Code")
    print("=" * 60)