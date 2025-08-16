#!/usr/bin/env python3
"""
Inspect the exact configuration that gets sent to Roo-Code
"""

import sys
sys.path.append('src')

from config.provider_manager import ProviderManager
import asyncio
import json

async def inspect_qwen_config():
    manager = ProviderManager()
    
    print("🔍 Inspecting Qwen-3-Coder Configuration")
    print("=" * 50)
    
    # Test your exact configuration
    config_input = {
        "provider": "openai-compatible",
        "model": "qwen-3-coder",
        "base_url": "http://localhost:3000/v1",
        "context_length": 131000,
        "max_tokens": 4096,
        "temperature": 0.7
    }
    
    print("📝 Input Configuration:")
    print(json.dumps(config_input, indent=2))
    
    # Process through provider manager
    roo_code_message = await manager.set_provider("test-client", config_input)
    
    print("\n📤 Message that would be sent to Roo-Code:")
    print(json.dumps(roo_code_message, indent=2))
    
    print("\n📋 Available Providers:")
    providers = await manager.get_available_providers()
    for name, info in providers.items():
        print(f"  • {name}: {info['models']} (max context: {info['max_context']:,})")
    
    print("\n🎯 Default Configuration:")
    default = manager.get_default_config()
    print(json.dumps(default, indent=2))

if __name__ == "__main__":
    asyncio.run(inspect_qwen_config())