#!/usr/bin/env python3
"""
Check which version of the extension is running
"""

import asyncio
import json
import socket

async def check_raw_connection():
    """Check the raw connection to see the welcome message."""
    
    print("🔍 Checking Extension Version")
    print("=" * 30)
    
    try:
        # Create raw TCP connection
        reader, writer = await asyncio.open_connection('127.0.0.1', 9999)
        print("✅ Connected to port 9999")
        
        # Read the welcome message
        print("\n📨 Reading welcome message...")
        try:
            data = await asyncio.wait_for(reader.readuntil(b'\n'), timeout=5.0)
            welcome_msg = data.decode().strip()
            print(f"📋 Raw welcome: {welcome_msg}")
            
            # Parse as JSON
            try:
                welcome_data = json.loads(welcome_msg)
                capabilities = welcome_data.get('data', {}).get('capabilities', {})
                
                print(f"\n📊 Extension capabilities:")
                print(f"   Version: {capabilities.get('version', 'unknown')}")
                print(f"   Commands: {capabilities.get('commands', [])}")
                print(f"   Tools: {capabilities.get('tools', [])}")
                print(f"   Features: {capabilities.get('features', [])}")
                
                # Check if this looks like our new extension
                commands = capabilities.get('commands', [])
                if 'configureProvider' in str(commands) or 'approvalResponse' in str(commands):
                    print("\n✅ NEW extension detected!")
                else:
                    print("\n⚠️  OLD extension detected (no new commands)")
                    print("💡 Extension needs to be recompiled/restarted")
                
            except json.JSONDecodeError:
                print(f"❌ Welcome message not JSON: {welcome_msg}")
                
        except asyncio.TimeoutError:
            print("⏰ No welcome message received")
        
        # Close connection
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

async def check_build_status():
    """Check if the extension was built correctly."""
    
    print("\n" + "=" * 30)
    print("🔧 Build Status Check")
    print("=" * 30)
    
    import os
    extension_path = "/Users/neweyesiss/roo-code-bridge/extension"
    
    # Check if out directory exists
    out_dir = os.path.join(extension_path, "out")
    if os.path.exists(out_dir):
        print("✅ 'out' directory exists")
        
        # Check for main files
        extension_js = os.path.join(out_dir, "extension.js")
        roo_interface_js = os.path.join(out_dir, "roo-code-interface.js")
        
        if os.path.exists(extension_js):
            print("✅ extension.js compiled")
            
            # Check file modification time
            import datetime
            mtime = os.path.getmtime(extension_js)
            mod_time = datetime.datetime.fromtimestamp(mtime)
            print(f"   📅 Modified: {mod_time}")
        else:
            print("❌ extension.js not found")
            
        if os.path.exists(roo_interface_js):
            print("✅ roo-code-interface.js compiled")
            
            # Check file size (new version should be larger)
            size = os.path.getsize(roo_interface_js)
            print(f"   📊 Size: {size} bytes")
            
            if size > 10000:  # New version should be significantly larger
                print("   ✅ File size suggests new code")
            else:
                print("   ⚠️  File size suggests old code")
        else:
            print("❌ roo-code-interface.js not found")
    else:
        print("❌ 'out' directory not found - extension not compiled")
        print("💡 Run: cd extension && npm run compile")

async def main():
    await check_raw_connection()
    await check_build_status()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS")
    print("=" * 50)
    print("If the extension shows OLD version:")
    print("1. The installation might be from wrong location")
    print("2. VS Code might be caching the old extension")
    print("3. The extension host needs a restart")
    print("\n💡 Try:")
    print("1. Ctrl+Shift+P -> 'Developer: Reload Window'")
    print("2. Or completely close VS Code and reopen")
    print("3. Or run: cd extension && npm run compile && F5")

if __name__ == "__main__":
    asyncio.run(main())