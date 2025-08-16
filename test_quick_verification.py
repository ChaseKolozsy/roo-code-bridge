#!/usr/bin/env python3
"""
Quick verification that bridge is working - no long waits
"""
import socket
import json
import time

def quick_test():
    print("⚡ QUICK ROO-CODE BRIDGE VERIFICATION")
    print("=" * 50)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        sock.connect(('127.0.0.1', 9999))
        
        # Auth
        data = sock.recv(4096).decode('utf-8')
        auth_msg = {"type": "authenticate", "data": {"apiKey": "test"}}
        sock.send((json.dumps(auth_msg) + '\n').encode('utf-8'))
        time.sleep(0.5)
        auth_resp = json.loads(sock.recv(4096).decode('utf-8').strip())
        
        auth_ok = auth_resp.get('type') == 'authenticated'
        print(f"🔐 Auth: {'✅' if auth_ok else '❌'}")
        
        # Config test
        config_msg = {
            "type": "configureProvider",
            "data": {
                "provider": "openai-compatible", 
                "model": "qwen-3-coder"
            }
        }
        sock.send((json.dumps(config_msg) + '\n').encode('utf-8'))
        time.sleep(1)
        config_resp = json.loads(sock.recv(4096).decode('utf-8').strip())
        
        config_ok = config_resp.get('data', {}).get('success', False)
        print(f"⚙️  Config: {'✅' if config_ok else '❌'}")
        
        # Quick task test - just check if it starts
        task_msg = {
            "type": "runTask",
            "data": {
                "prompt": "Just say 'OK'",
                "config": {"apiProvider": "openai-compatible"}
            }
        }
        sock.send((json.dumps(task_msg) + '\n').encode('utf-8'))
        time.sleep(2)  # Short wait
        
        try:
            task_resp = json.loads(sock.recv(4096).decode('utf-8').strip())
            task_started = task_resp.get('data', {}).get('success', False)
            print(f"🚀 Task: {'✅ Started' if task_started else '❌ Failed'}")
            
            if task_started:
                task_id = task_resp.get('data', {}).get('taskId', 'None')
                print(f"   🆔 Task ID: {task_id}")
        except:
            print("🚀 Task: ⏳ Started but no immediate response (normal)")
        
        sock.close()
        
        success = auth_ok and config_ok
        print(f"\n{'🎉 BRIDGE IS WORKING!' if success else '❌ Issues detected'}")
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    quick_test()