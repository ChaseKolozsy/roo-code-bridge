#!/usr/bin/env python3
"""
Send natural messages to Roo-Code using the proper API flow:
1. Start a new task (which creates a conversation)
2. Send messages to that task naturally
"""
import socket
import json
import time

def send_natural_conversation():
    print("💬 NATURAL CONVERSATION WITH ROO-CODE")
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
        
        # Step 1: Start a new task with a simple greeting
        print("👋 Starting new task with greeting...")
        
        start_task_message = {
            "type": "runTask",
            "data": {
                "prompt": "Hello! I'd like some help with a coding project."
            }
        }
        
        sock.send((json.dumps(start_task_message) + '\n').encode('utf-8'))
        time.sleep(3)  # Give it time to process
        
        # Read the response
        try:
            response_data = sock.recv(8192).decode('utf-8')
            if response_data.strip():
                response = json.loads(response_data.strip())
                print(f"📨 Task start response: {response}")
                
                task_id = response.get('data', {}).get('taskId')
                if task_id:
                    print(f"✅ Task started with ID: {task_id}")
                else:
                    print("⚠️  No task ID received, but continuing...")
        except Exception as e:
            print(f"📝 Could not parse response: {e}")
        
        # Step 2: Send the actual Flappy Bird request using sendMessage equivalent
        print("\n🎮 Sending Flappy Bird feature request...")
        
        # Wait a moment for the task to be fully established
        time.sleep(2)
        
        send_message = {
            "type": "sendMessage",
            "data": {
                "message": "I want to add a gravity flip feature to Flappy Bird. As a random event, gravity should flip where Flappy Bird now has to flap in the opposite direction. This should happen automatically - the player just keeps pressing space but the bird moves in the opposite direction. Can you help implement this feature?",
                "images": []
            }
        }
        
        sock.send((json.dumps(send_message) + '\n').encode('utf-8'))
        
        # Listen for responses from the LLM
        print("👂 Listening for LLM responses...")
        start_time = time.time()
        
        while time.time() - start_time < 45:  # Wait longer for LLM processing
            try:
                sock.settimeout(5)
                response_data = sock.recv(8192).decode('utf-8')
                
                if response_data.strip():
                    for line in response_data.strip().split('\n'):
                        if line.strip():
                            try:
                                response = json.loads(line.strip())
                                print(f"📨 Response: {response}")
                                
                                # Look for LLM messages
                                if 'message' in str(response) or 'task' in str(response):
                                    print("🤖 LLM is responding!")
                                    
                            except json.JSONDecodeError:
                                print(f"📝 Raw response: {line}")
                                
            except socket.timeout:
                print("   ⏳ Still waiting for LLM response...")
                continue
            except Exception as e:
                print(f"   ⚠️  Error reading response: {e}")
                break
        
        print("\n✅ Natural conversation flow completed")
        sock.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 GOAL: Natural conversation flow with Roo-Code")
    print("💬 Start task with greeting, then send actual request")
    print("🎮 Let LLM naturally create the task structure")
    print()
    
    success = send_natural_conversation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Natural conversation completed!")
        print("🎮 Check Roo-Code interface - LLM should be processing the request")
        print("💡 This is the correct way to interact with Roo-Code")
    else:
        print("❌ Failed to complete conversation")
    print("=" * 60)