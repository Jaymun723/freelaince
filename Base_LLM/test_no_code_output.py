#!/usr/bin/env python3

# Test that NO CODE is printed to user
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from init import FreelanceAssistant
    
    print("=== NO CODE OUTPUT TEST ===")
    print()
    print("This test checks that users NEVER see any HTML code")
    print("Expected output: Only friendly messages, NO code")
    print()
    print("=" * 60)
    
    assistant = FreelanceAssistant()
    
    # Set up user info
    assistant.user_info = {
        "name": "Clean Test",
        "service_type": "consulting", 
        "email_address": "clean@test.com"
    }
    
    # Mock feedback session to avoid interaction
    def mock_feedback_session(filename):
        print(f"👀 Your website is now open in your browser!")
        print(f"💬 Website creation completed successfully")
    
    assistant.website_feedback_session = mock_feedback_session
    
    # Create website - this should show NO CODE to user
    print("🚀 Testing website creation (should show NO code)...")
    assistant.create_website_immediately()
    
    print("=" * 60)
    print()
    
    # Check if website was created
    expected_file = "www/cleantest.html"
    if os.path.exists(expected_file):
        print(f"✅ Website created: {expected_file}")
        
        # Check file content
        with open(expected_file, 'r') as f:
            content = f.read()
        
        # Verify it's proper HTML
        if content.strip().startswith('<!DOCTYPE html>') and 'Clean Test' in content:
            print("✅ Website contains proper HTML and user data")
        else:
            print("❌ Website content issue")
            
        print(f"📏 File size: {len(content)} characters")
    else:
        print(f"❌ Website not created")
    
    print()
    print("🎯 RESULT: If you saw any HTML code above, that's the bug!")
    print("   Users should only see friendly messages like:")
    print("   🚀 Creating your website...")
    print("   ✅ Website ready!")
    print("   🌐 Opening in browser...")
    
except Exception as e:
    print(f"❌ Test error: {e}")
    import traceback
    traceback.print_exc()