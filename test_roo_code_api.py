#!/usr/bin/env python3
"""
Test actual Roo-Code API integration - THE MOST CRITICAL TEST
"""
import socket
import json
import time

def test_roo_code_api():
    print("🔍 TESTING ACTUAL ROO-CODE API INTEGRATION")
    print("=" * 60)
    print("This is the MOST IMPORTANT test - does our extension actually talk to Roo-Code?")
    print()
    
    try:
        # Connect to our extension
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 9999))
        
        # Read welcome message
        data = sock.recv(4096).decode('utf-8')
        print(f"📋 Extension connected: {json.loads(data.strip())['type']}")
        
        # Test 1: Configure Roo-Code provider
        print("\n🧪 TEST 1: Configuring Roo-Code provider...")
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
        
        # Wait for response
        time.sleep(2)
        response_data = sock.recv(4096).decode('utf-8')
        
        if response_data.strip():
            response = json.loads(response_data.strip())
            print(f"   📨 Response: {response}")
            
            if response.get('type') == 'success':
                print("   ✅ Provider configuration SUCCESS")
            elif response.get('type') == 'error':
                error_msg = response.get('error', {}).get('message', 'Unknown error')
                print(f"   ❌ Provider configuration FAILED: {error_msg}")
                if 'Roo-Code API not available' in error_msg:
                    print("   💡 This means Roo-Code extension is not found or not properly exposed")
                    return False
            else:
                print(f"   ⚠️  Unexpected response type: {response.get('type')}")
        else:
            print("   ❌ No response received")
            return False
        
        # Test 2: Try to run a simple task
        print("\n🧪 TEST 2: Running a simple Roo-Code task...")
        task_message = {
            "type": "runTask",
            "data": {
                "prompt": "Say hello and tell me you're working through the Roo-Code Bridge",
                "config": {
                    "apiProvider": "openai-compatible",
                    "apiModelId": "qwen-3-coder",
                    "apiUrl": "http://localhost:3000/v1",
                    "contextLength": 131000
                }
            }
        }
        
        sock.send((json.dumps(task_message) + '\n').encode('utf-8'))
        
        # Wait for response
        time.sleep(3)
        task_response_data = sock.recv(4096).decode('utf-8')
        
        if task_response_data.strip():
            task_response = json.loads(task_response_data.strip())
            print(f"   📨 Task Response: {task_response}")
            
            if task_response.get('success'):
                print("   ✅ Roo-Code task execution SUCCESS!")
                print("   🎉 THE BRIDGE IS WORKING WITH REAL ROO-CODE!")
                return True
            else:
                error = task_response.get('error', 'Unknown error')
                print(f"   ❌ Roo-Code task FAILED: {error}")
                return False
        else:
            print("   ❌ No task response received")
            return False
        
        sock.close()
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_roo_code_api()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 RESULT: Roo-Code API integration is WORKING!")
        print("✅ The bridge successfully communicates with real Roo-Code")
    else:
        print("❌ RESULT: Roo-Code API integration is NOT working")
        print("🔧 The extension cannot communicate with real Roo-Code")
    print("=" * 60)
    
    exit(0 if success else 1)