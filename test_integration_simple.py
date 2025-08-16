#!/usr/bin/env python3
"""
Simple integration test for the Roo-Code Bridge
"""
import socket
import json
import time

def test_integration():
    print("🔍 Testing Roo-Code Bridge Integration")
    print("=" * 50)
    
    # Test 1: Extension connectivity
    print("1. Testing extension connectivity...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 9999))
        
        data = sock.recv(4096).decode('utf-8')
        welcome = json.loads(data.strip())
        
        capabilities = welcome.get('data', {}).get('capabilities', {})
        commands = capabilities.get('commands', [])
        
        if 'configureProvider' in commands and 'approvalResponse' in commands:
            print("   ✅ Extension has new Roo-Code integration capabilities")
        else:
            print("   ❌ Extension missing new capabilities")
            return False
        
        sock.close()
        
    except Exception as e:
        print(f"   ❌ Extension connection failed: {e}")
        return False
    
    # Test 2: Bridge server connectivity
    print("2. Testing bridge server connectivity...")
    try:
        import requests
        response = requests.get("http://localhost:47291/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Bridge server is responding")
        else:
            print(f"   ❌ Bridge server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Bridge server connection failed: {e}")
        return False
    
    print("\n🎉 Integration test PASSED!")
    print("✅ Extension has new capabilities")
    print("✅ Bridge server is running")
    print("✅ Ready for full Phase 2 testing")
    
    return True

if __name__ == "__main__":
    success = test_integration()
    exit(0 if success else 1)