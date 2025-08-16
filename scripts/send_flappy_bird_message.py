#!/usr/bin/env python3
"""
Send a natural message to Roo-Code about adding gravity flip to Flappy Bird
"""
import socket
import json
import time

def send_flappy_bird_message():
    print("🎮 SENDING FLAPPY BIRD GRAVITY FLIP MESSAGE TO ROO-CODE")
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
        
        # Send the Flappy Bird feature request as a natural message
        print("\n🎮 Sending Flappy Bird gravity flip feature request...")
        
        message = {
            "type": "message",
            "data": {
                "text": "I want to add a gravity flip feature to Flappy Bird. As a random event, gravity should flip where Flappy Bird now has to flap in the opposite direction. This should happen automatically - the player just keeps pressing space but the bird moves in the opposite direction. Can you help implement this feature?"
            }
        }
        
        sock.send((json.dumps(message) + '\n').encode('utf-8'))
        
        # Listen for responses
        print("👂 Listening for Roo-Code responses...")
        start_time = time.time()
        
        while time.time() - start_time < 60:  # Wait up to 60 seconds
            try:
                sock.settimeout(5)
                response_data = sock.recv(8192).decode('utf-8')
                
                if response_data.strip():
                    for line in response_data.strip().split('\n'):
                        if line.strip():
                            try:
                                response = json.loads(line.strip())
                                print(f"📨 Response: {response}")
                                
                            except json.JSONDecodeError:
                                print(f"📝 Raw response: {line}")
                                
            except socket.timeout:
                print("   ⏳ Still waiting for response...")
                continue
            except Exception as e:
                print(f"   ⚠️  Error reading response: {e}")
                break
        
        print("\n✅ Message sent to Roo-Code")
        sock.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎮 GOAL: Request Flappy Bird gravity flip feature from Roo-Code")
    print("💬 Send as natural conversation message")
    print()
    
    success = send_flappy_bird_message()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Flappy Bird feature request sent!")
        print("🎮 Check Roo-Code interface for response and implementation")
    else:
        print("❌ Failed to send message")
    print("=" * 60)