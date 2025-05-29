#!/usr/bin/env python3
"""
Setup script for Hammad Bhai AI Assistant
This script helps you configure your Gemini API key
"""

import os
import webbrowser
from pathlib import Path

def setup_gemini_api_key():
    print("🤖 HAMMAD BHAI AI Assistant Setup")
    print("=" * 50)
    print("👨‍💻 Created by: MUHAMMAD HAMMAD ZUBAIR")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path('.env')
    
    print("\n📋 Setting up your Gemini API Key...")
    print("\n🔑 To get your FREE Gemini API key:")
    print("1. Visit: https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the generated API key")
    
    # Ask if user wants to open the URL
    open_url = input("\n🌐 Would you like me to open the API key page in your browser? (y/n): ").lower().strip()
    if open_url in ['y', 'yes']:
        try:
            webbrowser.open('https://makersuite.google.com/app/apikey')
            print("✅ Browser opened! Get your API key and come back here.")
        except:
            print("❌ Could not open browser. Please visit the URL manually.")
    
    # Get API key from user
    print("\n🔐 Enter your Gemini API key:")
    api_key = input("API Key: ").strip()
    
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ No valid API key provided. Setup cancelled.")
        return False
    
    # Read existing .env content
    env_content = ""
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
    
    # Update or add the API key
    lines = env_content.split('\n')
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith('GEMINI_API_KEY='):
            lines[i] = f'GEMINI_API_KEY={api_key}'
            updated = True
            break
    
    if not updated:
        lines.append(f'GEMINI_API_KEY={api_key}')
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"\n✅ API key saved to {env_file}")
    print("\n🚀 Setup complete! You can now run the chatbot:")
    print("   python app.py")
    print("\n🌐 Then visit: http://localhost:5000")
    print("\n💡 Tip: Keep your API key secure and don't share it publicly!")
    
    return True

if __name__ == "__main__":
    try:
        setup_gemini_api_key()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
