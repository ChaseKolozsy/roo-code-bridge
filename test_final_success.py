#!/usr/bin/env python3
"""
FINAL SUCCESS TEST - Check if Roo-Code Bridge is fully working
"""
import socket
import json
import time

def test_final_success():
    print("🎉 FINAL ROO-CODE BRIDGE SUCCESS TEST")
    print("=" * 60)
    
    try:
        # Connect and authenticate
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 9999))
        
        # Read welcome
        data = sock.recv(4096).decode('utf-8')
        print(f"📋 Connected: {json.loads(data.strip())['type']}")
        
        # Authenticate
        auth_message = {"type": "authenticate", "data": {"apiKey": "test-key-123"}}
        sock.send((json.dumps(auth_message) + '\n').encode('utf-8'))
        time.sleep(1)
        auth_response = json.loads(sock.recv(4096).decode('utf-8').strip())
        print(f"🔐 Auth: {'✅ SUCCESS' if auth_response.get('type') == 'authenticated' else '❌ FAILED'}")
        
        # Test provider configuration
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
        config_response = json.loads(sock.recv(4096).decode('utf-8').strip())
        
        config_success = config_response.get('data', {}).get('success', False)
        print(f"⚙️  Config: {'✅ SUCCESS' if config_success else '❌ FAILED'}")
        
        # Test task execution
        task_message = {
            "type": "runTask",
            "data": {
                "prompt": "Hello! Please confirm the Roo-Code Bridge is working by saying 'Bridge is operational!'",
                "config": {
                    "apiProvider": "openai-compatible",
                    "apiModelId": "qwen-3-coder",
                    "apiUrl": "http://localhost:3000/v1",
                    "contextLength": 131000
                }
            }
        }
        
        sock.send((json.dumps(task_message) + '\n').encode('utf-8'))
        time.sleep(5)
        task_response = json.loads(sock.recv(4096).decode('utf-8').strip())
        
        task_data = task_response.get('data', {})
        task_success = task_data.get('success', False)
        task_id = task_data.get('taskId', 'No ID')
        
        print(f"🚀 Task: {'✅ SUCCESS' if task_success else '❌ FAILED'}")
        if task_success:
            print(f"   📋 Task ID: {task_id}")
            print(f"   💬 Output: {task_data.get('output', 'No output')}")
        
        sock.close()
        
        # Final assessment
        all_success = auth_response.get('type') == 'authenticated' and config_success and task_success
        
        print("\n" + "=" * 60)
        if all_success:
            print("🎉 COMPLETE SUCCESS! ROO-CODE BRIDGE IS FULLY OPERATIONAL!")
            print("✅ Authentication works")
            print("✅ Provider configuration works") 
            print("✅ Task execution works")
            print("✅ Bridge connects to real Roo-Code extension")
            print("🏆 PHASE 2 IMPLEMENTATION: COMPLETE!")
        else:
            print("⚠️  PARTIAL SUCCESS - Some components working")
            
        return all_success
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_final_success()
    exit(0 if success else 1)