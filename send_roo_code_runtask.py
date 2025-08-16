#!/usr/bin/env python3
"""
Send runTask command to Roo-Code for Flappy Bird gravity flip feature
"""
import socket
import json
import time

def send_run_task():
    print("🎮 SENDING RUNTASK TO ROO-CODE")
    print("=" * 60)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect(('127.0.0.1', 9999))
        
        # Auth first
        data = sock.recv(4096).decode('utf-8')
        auth_message = {"type": "authenticate", "data": {"apiKey": "test-key"}}
        sock.send((json.dumps(auth_message) + '\n').encode('utf-8'))
        time.sleep(1)
        sock.recv(4096)
        print("🔐 Authenticated")
        
        # Send runTask command (from the capabilities list)
        print("🎮 Sending runTask command...")
        
        run_task_message = {
            "type": "runTask",
            "data": {
                "prompt": "I want to add a gravity flip feature to Flappy Bird. As a random event, gravity should flip where Flappy Bird now has to flap in the opposite direction. This should happen automatically - the player just keeps pressing space but the bird moves in the opposite direction. Can you help implement this feature in the Flappy Bird game?"
            }
        }
        
        sock.send((json.dumps(run_task_message) + '\n').encode('utf-8'))
        
        # Listen for responses
        print("👂 Listening for Roo-Code responses...")
        start_time = time.time()
        
        while time.time() - start_time < 30:  # Wait up to 30 seconds
            try:
                sock.settimeout(5)
                response_data = sock.recv(8192).decode('utf-8')
                
                if response_data.strip():
                    for line in response_data.strip().split('\n'):
                        if line.strip():
                            try:
                                response = json.loads(line.strip())
                                print(f"📨 Response: {response}")
                                
                                # Check for task success
                                if response.get('data', {}).get('success'):
                                    task_id = response.get('data', {}).get('taskId')
                                    print(f"\n🎉 SUCCESS! Task started with ID: {task_id}")
                                    print("🎮 Flappy Bird gravity flip task is running!")
                                    return True
                                    
                            except json.JSONDecodeError:
                                print(f"📝 Raw response: {line}")
                                
            except socket.timeout:
                print("   ⏳ Still waiting for response...")
                continue
            except Exception as e:
                print(f"   ⚠️  Error reading response: {e}")
                break
        
        print("\n✅ RunTask command sent")
        sock.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 GOAL: Use runTask command from Roo-Code capabilities")
    print("📋 Send Flappy Bird gravity flip feature request")
    print()
    
    success = send_run_task()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Flappy Bird runTask sent to Roo-Code!")
        print("🎮 Check Roo-Code interface - task should be executing")
        print("💡 Bridge can successfully send tasks to Roo-Code")
    else:
        print("❌ Failed to send runTask")
    print("=" * 60)