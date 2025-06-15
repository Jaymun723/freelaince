#!/usr/bin/env python3

# Test the function calling implementation for website creation
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from init import FreelanceAssistant
    
    print("=== Function Calling Website Creation Test ===")
    print()
    
    assistant = FreelanceAssistant()
    
    # Set up user info
    assistant.user_info = {
        "name": "Emma Rodriguez",
        "service_type": "graphic design", 
        "email_address": "emma@design.com"
    }
    
    print("📊 User data set up:")
    print("- Name: Emma Rodriguez")
    print("- Service: graphic design")
    print("- Email: emma@design.com")
    print()
    
    print("🔧 Testing function calling approach...")
    print("Expected behavior:")
    print("✅ Claude generates HTML and calls build_website function")
    print("✅ Function stores HTML in www/emmarodriguez.html")
    print("✅ User sees only friendly messages (no HTML code)")
    print("✅ Browser opens automatically")
    print()
    print("=" * 60)
    
    # Patch the website_feedback_session to avoid interactive input
    def mock_feedback_session(filename):
        print(f"👀 Your website is now open in your browser!")
        print(f"💬 Tell me what you think or what you'd like to change...")
        print(f"[Function calling test completed - website at {filename}]")
    
    # Replace the method temporarily
    original_method = assistant.website_feedback_session
    assistant.website_feedback_session = mock_feedback_session
    
    # Test the function calling flow
    assistant.create_website_immediately()
    
    # Restore original method
    assistant.website_feedback_session = original_method
    
    print("=" * 60)
    print()
    
    # Check the results
    expected_filename = "www/emmarodriguez.html"
    if os.path.exists(expected_filename):
        print(f"✅ Website file '{expected_filename}' was created via function calling")
        
        # Check the file content
        with open(expected_filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.strip().startswith('<!DOCTYPE html>'):
            print("✅ File contains proper HTML structure")
        else:
            print("❌ File doesn't start with DOCTYPE")
        
        if 'Emma Rodriguez' in content:
            print("✅ Website contains user's name")
        else:
            print("❌ Website missing user's name")
            
        if 'graphic design' in content.lower():
            print("✅ Website contains service type")
        else:
            print("❌ Website missing service type")
            
        if 'emma@design.com' in content:
            print("✅ Website contains user's email")
        else:
            print("❌ Website missing user's email")
            
        print(f"📏 Website file size: {len(content)} characters")
        
    else:
        print(f"❌ Website file '{expected_filename}' was not created")
    
    # Show www folder contents
    print()
    print("📂 Contents of www folder:")
    if os.path.exists("www"):
        www_files = os.listdir("www")
        for file in sorted(www_files):
            print(f"   - {file}")
    
    print()
    print("🎯 Function calling allows Claude to directly call build_website()")
    print("   with the generated HTML as arguments - clean separation!")
    
except Exception as e:
    print(f"Test error: {e}")
    import traceback
    traceback.print_exc()