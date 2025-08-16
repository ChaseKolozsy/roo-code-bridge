#!/usr/bin/env python3
"""
Send a chat message to Roo-Code about Flappy Bird gravity flip
"""
import socket
import json
import time

def send_chat_message():
    print("💬 SENDING CHAT MESSAGE TO ROO-CODE")
    print("=" * 60)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect(('127.0.0.1', 9999))
        
        # Auth
        data = sock.recv(4096).decode('utf-8')
        auth_message = {"type": "authenticate", "data": {"apiKey": "test-key"}}
        sock.send((json.dumps(auth_message) + '\n').encode('utf-8'))
        time.sleep(1)
        sock.recv(4096)
        print("🔐 Authenticated")
        
        # Try different message types for chat
        message_types = [
            {"type": "chat", "data": {"message": "I want to add a gravity flip feature to Flappy Bird. As a random event, gravity should flip where Flappy Bird now has to flap in the opposite direction. This should happen automatically - the player just keeps pressing space but the bird moves in the opposite direction. Can you help implement this feature?"}},
            {"type": "userMessage", "data": {"text": "I want to add a gravity flip feature to Flappy Bird. As a random event, gravity should flip where Flappy Bird now has to flap in the opposite direction. This should happen automatically - the player just keeps pressing space but the bird moves in the opposite direction. Can you help implement this feature?"}},
            {"type": "chatMessage", "data": {"content": "I want to add a gravity flip feature to Flappy Bird. As a random event, gravity should flip where Flappy Bird now has to flap in the opposite direction. This should happen automatically - the player just keeps pressing space but the bird moves in the opposite direction. Can you help implement this feature?"}}
        ]
        
        for i, message in enumerate(message_types):
            print(f"\n🎮 Trying message type {i+1}: {message['type']}")
            
            sock.send((json.dumps(message) + '\n').encode('utf-8'))
            time.sleep(2)
            
            try:
                response_data = sock.recv(4096).decode('utf-8')
                if response_data.strip():
                    response = json.loads(response_data.strip())
                    print(f"📨 Response: {response}")
                    
                    if response.get('type') != 'error':
                        print(f"✅ Success with message type: {message['type']}")
                        break
                    
            except:
                print("📝 No immediate response")
        
        sock.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("💬 GOAL: Find working message type for Roo-Code chat")
    print("🎮 Request Flappy Bird gravity flip feature")
    print()
    
    success = send_chat_message()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Chat message attempts completed!")
    else:
        print("❌ Failed to send messages")
    print("=" * 60)