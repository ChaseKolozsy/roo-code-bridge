#!/usr/bin/env python3
"""
Show the configuration format for Qwen-3-Coder
"""

import json

def show_config_format():
    print("🔍 Qwen-3-Coder Configuration Format")
    print("=" * 50)
    
    # Input configuration from web client
    input_config = {
        "provider": "openai-compatible",
        "model": "qwen-3-coder",
        "base_url": "http://localhost:3000/v1",
        "context_length": 131000,
        "max_tokens": 4096,
        "temperature": 0.7
    }
    
    print("📝 Input Configuration (from web client):")
    print(json.dumps(input_config, indent=2))
    
    # Configuration that gets sent to Roo-Code
    roo_code_config = {
        "type": "saveApiConfiguration",
        "data": {
            "apiProvider": "openai-compatible",
            "apiModelId": "qwen-3-coder",
            "apiUrl": "http://localhost:3000/v1", 
            "maxTokens": 4096,
            "temperature": 0.7,
            "contextLength": 131000,
            "topP": None,
            "topK": None,
            "customInstructions": None
        }
    }
    
    print("\n📤 Message sent to Roo-Code:")
    print(json.dumps(roo_code_config, indent=2))
    
    print("\n🎯 Key Points:")
    print("  • Bridge server runs on port 47291 (uncommon)")
    print("  • Model: qwen-3-coder")
    print("  • Base URL: http://localhost:3000/v1")
    print("  • Context Window: 131,000 tokens")
    print("  • Provider type: openai-compatible")
    
    print("\n📋 Available Models for OpenAI Compatible:")
    models = ["qwen-3-coder", "qwen-2.5-coder", "deepseek-coder", "codellama", "custom"]
    for model in models:
        marker = "⭐" if model == "qwen-3-coder" else "  "
        print(f"  {marker} {model}")

if __name__ == "__main__":
    show_config_format()