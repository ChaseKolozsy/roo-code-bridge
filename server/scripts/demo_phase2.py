#!/usr/bin/env python3
"""
Interactive demo of Phase 2 features:
- Provider configuration management
- Message routing
- Approval flows
- Image handling

Run after starting the server with: uv run python src/main.py
"""

import asyncio
import json
import websockets
from datetime import datetime
import sys

class Phase2Demo:
    def __init__(self, client_id="demo-phase2"):
        self.client_id = client_id
        self.uri = f"ws://localhost:8000/ws/{client_id}"
        self.websocket = None
        
    async def connect(self):
        """Connect to the WebSocket server."""
        self.websocket = await websockets.connect(self.uri)
        print(f"✅ Connected to WebSocket as {self.client_id}")
        
    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            print("👋 Disconnected from WebSocket")
            
    async def send_and_receive(self, message: dict):
        """Send a message and receive the response."""
        print(f"\n📤 Sending: {message['type']}")
        await self.websocket.send(json.dumps(message))
        
        try:
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            print(f"📥 Response: {json.dumps(response_data, indent=2)}")
            return response_data
        except asyncio.TimeoutError:
            print("⏱️  No response (timeout)")
            return None
            
    async def demo_provider_config(self):
        """Demonstrate provider configuration."""
        print("\n" + "=" * 50)
        print("🔧 PROVIDER CONFIGURATION DEMO")
        print("=" * 50)
        
        providers = [
            {
                "provider": "anthropic",
                "model": "claude-3-opus",
                "max_tokens": 8192,
                "temperature": 0.7,
                "context_length": 200000
            },
            {
                "provider": "openai",
                "model": "gpt-4-turbo",
                "max_tokens": 4096,
                "temperature": 0.5,
                "context_length": 128000
            },
            {
                "provider": "gemini",
                "model": "gemini-1.5-pro",
                "max_tokens": 8192,
                "temperature": 0.8,
                "context_length": 1000000
            }
        ]
        
        for config in providers:
            print(f"\n📝 Configuring {config['provider']} with {config['model']}...")
            message = {
                "type": "saveApiConfiguration",
                "data": config
            }
            await self.send_and_receive(message)
            await asyncio.sleep(1)
            
    async def demo_task_management(self):
        """Demonstrate task management."""
        print("\n" + "=" * 50)
        print("📋 TASK MANAGEMENT DEMO")
        print("=" * 50)
        
        # Start a new task with specific provider
        print("\n🚀 Starting new task with specific provider...")
        message = {
            "type": "newTask",
            "data": {
                "prompt": "Create a Python function to calculate fibonacci numbers",
                "provider": "anthropic",
                "model": "claude-3-sonnet",
                "max_tokens": 2048
            }
        }
        response = await self.send_and_receive(message)
        
        # Cancel task
        print("\n❌ Cancelling task...")
        message = {
            "type": "cancelTask",
            "data": {
                "taskId": "demo-task-123"
            }
        }
        await self.send_and_receive(message)
        
    async def demo_image_handling(self):
        """Demonstrate image handling."""
        print("\n" + "=" * 50)
        print("🖼️  IMAGE HANDLING DEMO")
        print("=" * 50)
        
        # Small test image (1x1 red pixel)
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx8gAAAABJRU5ErkJggg=="
        
        print("\n📸 Sending task with image...")
        message = {
            "type": "newTask",
            "data": {
                "prompt": "Analyze this UI mockup and suggest improvements"
            },
            "images": [
                {
                    "type": "base64",
                    "data": test_image,
                    "mime_type": "image/png",
                    "name": "ui_mockup.png"
                }
            ]
        }
        await self.send_and_receive(message)
        
        print("\n🎨 Selecting multiple images...")
        message = {
            "type": "selectImages",
            "images": [
                {
                    "type": "base64",
                    "data": test_image,
                    "mime_type": "image/png",
                    "name": "design1.png"
                },
                {
                    "type": "base64",
                    "data": test_image,
                    "mime_type": "image/png",
                    "name": "design2.png"
                }
            ]
        }
        await self.send_and_receive(message)
        
    async def demo_approval_flow(self):
        """Demonstrate approval flow simulation."""
        print("\n" + "=" * 50)
        print("✅ APPROVAL FLOW DEMO")
        print("=" * 50)
        
        print("\n📝 Simulating approval response...")
        print("(In real usage, this would respond to an actual approval request from Roo-Code)")
        
        # Simulate responding to an approval request
        message = {
            "type": "askResponse",
            "data": {
                "approval_id": "simulated-approval-123",
                "approved": True,
                "response": "Yes, proceed with the operation"
            }
        }
        await self.send_and_receive(message)
        
    async def run_interactive_mode(self):
        """Run interactive mode for custom messages."""
        print("\n" + "=" * 50)
        print("💬 INTERACTIVE MODE")
        print("=" * 50)
        print("\nYou can now send custom messages.")
        print("Type 'help' for available message types or 'quit' to exit.\n")
        
        while True:
            try:
                msg_type = input("Message type (or 'quit'): ").strip()
                
                if msg_type.lower() == 'quit':
                    break
                    
                if msg_type.lower() == 'help':
                    print("\nAvailable message types:")
                    print("  - newTask: Start a new task")
                    print("  - saveApiConfiguration: Configure provider")
                    print("  - cancelTask: Cancel a task")
                    print("  - resumeTask: Resume a paused task")
                    print("  - askResponse: Respond to approval request")
                    print("  - selectImages: Select images")
                    print("  - draggedImages: Handle dragged images")
                    continue
                    
                data_str = input("Data (JSON format): ").strip()
                try:
                    data = json.loads(data_str) if data_str else {}
                except json.JSONDecodeError:
                    print("❌ Invalid JSON format")
                    continue
                    
                message = {"type": msg_type, "data": data}
                await self.send_and_receive(message)
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
                
    async def run(self):
        """Run the complete demo."""
        try:
            await self.connect()
            
            # Run demos
            await self.demo_provider_config()
            await self.demo_task_management()
            await self.demo_image_handling()
            await self.demo_approval_flow()
            
            # Offer interactive mode
            print("\n" + "=" * 50)
            choice = input("\nWould you like to enter interactive mode? (y/n): ")
            if choice.lower() == 'y':
                await self.run_interactive_mode()
                
        finally:
            await self.disconnect()

async def main():
    print("=" * 50)
    print("PHASE 2 FEATURE DEMO")
    print("Roo-Code Bridge Communication")
    print("=" * 50)
    
    demo = Phase2Demo()
    await demo.run()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()