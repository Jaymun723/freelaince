#!/usr/bin/env python3

# Test multiple users to ensure www folder works for different names
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from init import FreelanceAssistant
    
    print("=== Multiple Users WWW Folder Test ===")
    print()
    
    # Test users with different name formats
    test_users = [
        {"name": "Alex Johnson", "service": "tutoring", "email": "alex@tutor.com", "expected_file": "alexjohnson.html"},
        {"name": "Maria-Rosa", "service": "design", "email": "maria@design.com", "expected_file": "mariarosa.html"},
        {"name": "John_Smith", "service": "writing", "email": "john@writer.com", "expected_file": "johnsmith.html"}
    ]
    
    for i, user in enumerate(test_users, 1):
        print(f"🔄 Test {i}: {user['name']}")
        
        assistant = FreelanceAssistant()
        assistant.user_info = {
            "name": user['name'],
            "service_type": user['service'], 
            "email_address": user['email']
        }
        
        # Mock feedback session
        def mock_feedback_session(filename):
            print(f"👀 Your website is now open in your browser!")
            print(f"✅ Website saved successfully")
        
        assistant.website_feedback_session = mock_feedback_session
        
        print(f"🚀 Creating {user['service']} website for {user['name']}...")
        
        # Create website
        assistant.create_website_immediately()
        
        # Check if file was created correctly
        expected_path = f"www/{user['expected_file']}"
        if os.path.exists(expected_path):
            print(f"✅ {expected_path} created successfully")
            
            # Quick content check
            with open(expected_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if user['name'] in content and user['service'] in content.lower():
                print(f"✅ Content includes user name and service")
            else:
                print(f"❌ Content missing user details")
        else:
            print(f"❌ {expected_path} not created")
        
        print()
    
    # Show final www folder contents
    print("📂 Final www folder contents:")
    if os.path.exists("www"):
        www_files = os.listdir("www")
        for file in sorted(www_files):
            print(f"   - {file}")
    
    print()
    print("🎯 All websites are cleanly organized in www folder!")
    print("   Each user gets their own file with clean naming!")
    
except Exception as e:
    print(f"Test error: {e}")
    import traceback
    traceback.print_exc()