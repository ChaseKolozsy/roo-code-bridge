#!/usr/bin/env python3
"""
Test script for configuring Qwen-3-Coder with OpenAI compatible endpoint
"""

import asyncio
import json
import websockets

async def test_qwen_configuration():
    uri = "ws://localhost:47291/ws/qwen-test-client"
    
    print("🚀 Connecting to Roo-Code Bridge (port 47291)...")
    async with websockets.connect(uri) as websocket:
        print("✅ Connected!")
        
        # Configure your specific setup
        print("\n🔧 Configuring Qwen-3-Coder with OpenAI Compatible endpoint...")
        config = {
            "type": "saveApiConfiguration",
            "data": {
                "provider": "openai-compatible",
                "model": "qwen-3-coder",
                "base_url": "http://localhost:3000/v1",
                "context_length": 131000,
                "max_tokens": 4096,
                "temperature": 0.7
            }
        }
        
        await websocket.send(json.dumps(config))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"✅ Configuration response: {json.dumps(data, indent=2)}")
        
        # Test creating a task with this configuration
        print("\n📝 Testing task creation with Qwen-3-Coder...")
        task = {
            "type": "newTask",
            "data": {
                "prompt": "Write a Python function to implement a binary search algorithm",
                "provider": "openai-compatible",
                "model": "qwen-3-coder",
                "base_url": "http://localhost:3000/v1",
                "context_length": 131000,
                "max_tokens": 2048,
                "temperature": 0.3  # Lower temperature for coding tasks
            }
        }
        
        await websocket.send(json.dumps(task))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"✅ Task creation response: {json.dumps(data, indent=2)}")
        
        # Test other providers for comparison
        print("\n🔍 Testing other available providers...")
        test_configs = [
            {
                "provider": "anthropic",
                "model": "claude-3-sonnet",
                "max_tokens": 4096,
                "temperature": 0.7
            },
            {
                "provider": "openai",
                "model": "gpt-4-turbo",
                "max_tokens": 4096,
                "temperature": 0.7
            }
        ]
        
        for config_data in test_configs:
            provider_name = config_data["provider"]
            print(f"   🔧 Testing {provider_name}...")
            
            config_msg = {
                "type": "saveApiConfiguration",
                "data": config_data
            }
            
            await websocket.send(json.dumps(config_msg))
            response = await websocket.recv()
            data = json.loads(response)
            status = data.get('data', {}).get('status', 'unknown')
            print(f"   ✅ {provider_name}: {status}")
        
        # Switch back to your preferred configuration
        print(f"\n🎯 Switching back to Qwen-3-Coder configuration...")
        final_config = {
            "type": "saveApiConfiguration",
            "data": {
                "provider": "openai-compatible",
                "model": "qwen-3-coder",
                "base_url": "http://localhost:3000/v1",
                "context_length": 131000,
                "max_tokens": 4096,
                "temperature": 0.7
            }
        }
        
        await websocket.send(json.dumps(final_config))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"✅ Final configuration set: {json.dumps(data, indent=2)}")
        
        print("\n🎉 Qwen-3-Coder configuration test completed!")
        print("📋 Configuration Summary:")
        print("   • Provider: openai-compatible")
        print("   • Model: qwen-3-coder")
        print("   • Base URL: http://localhost:3000/v1")
        print("   • Context Length: 131,000 tokens")
        print("   • Bridge Port: 47291")

async def main():
    print("=" * 60)
    print("🧠 QWEN-3-CODER CONFIGURATION TEST")
    print("=" * 60)
    
    try:
        await test_qwen_configuration()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())