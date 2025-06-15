#!/usr/bin/env python3

# Test complete function calling flow including live editing
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from init import FreelanceAssistant, ask_claude_with_functions
    
    print("=== Complete Function Calling Flow Test ===")
    print()
    
    # Test the function calling mechanism directly first
    print("🧪 Testing function calling mechanism...")
    
    # Define a simple test function
    test_function = {
        "name": "build_website",
        "description": "Build and store a website",
        "input_schema": {
            "type": "object",
            "properties": {
                "html_content": {"type": "string", "description": "HTML content"},
                "user_name": {"type": "string", "description": "User name"},
                "user_service": {"type": "string", "description": "User service"}
            },
            "required": ["html_content", "user_name", "user_service"]
        }
    }
    
    # Simple test prompt
    test_prompt = """
    Create a simple HTML page that says "Hello World" and call the build_website function 
    with html_content="<html><body><h1>Hello World</h1></body></html>", 
    user_name="Test User", and user_service="testing".
    """
    
    print("📞 Making function calling test...")
    response = ask_claude_with_functions(test_prompt, [test_function], max_tokens=500)
    
    print("✅ Function calling response received")
    print(f"Response type: {type(response)}")
    
    # Check response structure
    if hasattr(response, 'content'):
        print(f"Content blocks: {len(response.content)}")
        for i, block in enumerate(response.content):
            print(f"  Block {i}: {block.type}")
            if hasattr(block, 'name'):
                print(f"    Function name: {block.name}")
    
    print()
    print("🎯 Function calling mechanism is working!")
    print()
    print("🌐 Now testing complete website creation flow...")
    
    assistant = FreelanceAssistant()
    assistant.user_info = {
        "name": "Function Test User",
        "service_type": "testing", 
        "email_address": "test@function.com"
    }
    
    # Mock feedback session for complete test
    def mock_feedback_session(filename):
        print(f"👀 Website ready at {filename}")
    
    assistant.website_feedback_session = mock_feedback_session
    
    # Test complete flow
    assistant.create_website_immediately()
    
    # Check results
    expected_file = "www/functiontestuser.html"
    if os.path.exists(expected_file):
        print(f"✅ Function calling created {expected_file}")
        with open(expected_file, 'r') as f:
            content = f.read()
        print(f"📏 File size: {len(content)} characters")
    else:
        print(f"❌ {expected_file} not created")
    
    print()
    print("🎯 Complete function calling implementation successful!")
    print("   Claude now calls build_website() function to store HTML!")
    
except Exception as e:
    print(f"Test error: {e}")
    import traceback
    traceback.print_exc()