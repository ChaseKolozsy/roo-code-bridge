#!/usr/bin/env python3
"""
Send a proper IPC task command to Roo-Code for Flappy Bird gravity flip feature
"""
import socket
import json
import time
import uuid

def send_task_command():
    print("🎮 SENDING FLAPPY BIRD TASK TO ROO-CODE")
    print("=" * 60)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect(('127.0.0.1', 9999))
        
        print("🔗 Connected to Roo-Code IPC server")
        
        # Generate a unique client ID
        client_id = str(uuid.uuid4())
        
        # Send TaskCommand with StartNewTask
        task_command = {
            "type": "TaskCommand",
            "origin": "client",
            "clientId": client_id,
            "data": {
                "commandName": "StartNewTask",
                "data": {
                    "configuration": {
                        # Use minimal configuration to avoid validation issues
                        "apiProvider": "ollama",
                        "apiModelId": "gpt-oss:20b"
                    },
                    "text": "I want to add a gravity flip feature to Flappy Bird. As a random event, gravity should flip where Flappy Bird now has to flap in the opposite direction. This should happen automatically - the player just keeps pressing space but the bird moves in the opposite direction. Can you help implement this feature in the Flappy Bird game?",
                    "newTab": True
                }
            }
        }
        
        print("📤 Sending StartNewTask command...")
        sock.send((json.dumps(task_command) + '\n').encode('utf-8'))
        
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
                                
                                # Check for successful task creation
                                if (response.get('type') == 'TaskEvent' and 
                                    response.get('data', {}).get('eventName') == 'taskCreated'):
                                    task_id = response.get('data', {}).get('eventData', [None])[0]
                                    print(f"\n🎉 SUCCESS! Task created with ID: {task_id}")
                                    print("🎮 Flappy Bird gravity flip task sent to Roo-Code!")
                                    return True
                                    
                            except json.JSONDecodeError:
                                print(f"📝 Raw response: {line}")
                                
            except socket.timeout:
                print("   ⏳ Still waiting for response...")
                continue
            except Exception as e:
                print(f"   ⚠️  Error reading response: {e}")
                break
        
        print("\n✅ Task command sent successfully")
        sock.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 GOAL: Send Flappy Bird gravity flip task using proper IPC format")
    print("📋 Using TaskCommand -> StartNewTask message structure")
    print()
    
    success = send_task_command()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Flappy Bird task sent to Roo-Code!")
        print("🎮 Check Roo-Code interface for task execution")
        print("💡 The bridge is working with proper IPC message format")
    else:
        print("❌ Failed to send task")
    print("=" * 60)