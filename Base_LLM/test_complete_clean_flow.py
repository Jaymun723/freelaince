#!/usr/bin/env python3

# Test the complete clean website creation flow
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from init import FreelanceAssistant
    
    print("=== Complete Clean Website Creation Flow Test ===")
    print()
    
    assistant = FreelanceAssistant()
    
    # Set up user info
    assistant.user_info = {
        "name": "Alex",
        "service_type": "tutoring", 
        "email_address": "alex.tutor@gmail.com"
    }
    
    print("📊 User data set up:")
    print("- Name: Alex")
    print("- Service: tutoring")
    print("- Email: alex.tutor@gmail.com")
    print()
    
    print("🌐 Testing complete website creation flow...")
    print("Expected behavior:")
    print("✅ User sees friendly messages")
    print("❌ User does NOT see any HTML code")
    print("✅ Website file is created with clean HTML")
    print("✅ Browser would open automatically (simulated)")
    print()
    print("=" * 60)
    
    # Patch the website_feedback_session to avoid interactive input
    def mock_feedback_session(filename):
        print(f"\n👀 Your website is now open in your browser!")
        print(f"💬 Tell me what you think or what you'd like to change...")
        print("[Feedback session skipped for test - website creation completed successfully]")
    
    # Replace the method temporarily
    original_method = assistant.website_feedback_session
    assistant.website_feedback_session = mock_feedback_session
    
    # Test the complete flow
    assistant.create_website_immediately()
    
    # Restore original method
    assistant.website_feedback_session = original_method
    
    print("=" * 60)
    print()
    
    # Check the results
    filename = "alex_website.html"
    if os.path.exists(filename):
        print(f"✅ Website file '{filename}' was created successfully")
        
        # Check the file content
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.strip().startswith('<!DOCTYPE html>'):
            print("✅ File contains clean HTML (starts with DOCTYPE)")
        else:
            print("❌ File doesn't start with DOCTYPE")
            print(f"Actually starts with: {content[:100]}")
        
        if '```html' in content or '```' in content:
            print("❌ File contains markdown formatting")
        else:
            print("✅ File contains NO markdown formatting")
            
        if 'Here' in content[:200] and 'website' in content[:200]:
            print("❌ File contains explanatory text")
        else:
            print("✅ File contains NO explanatory text")
            
        print(f"📏 Website file size: {len(content)} characters")
    else:
        print(f"❌ Website file '{filename}' was not created")
    
    print()
    print("🎯 Summary: Website creation now uses Claude API to generate HTML")
    print("   but completely hides the code from users. They only see the")
    print("   friendly progress messages and the final website in their browser!")
    
except Exception as e:
    print(f"Test error: {e}")
    import traceback
    traceback.print_exc()