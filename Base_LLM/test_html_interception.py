#!/usr/bin/env python3

# Test HTML interception and rewriting functionality
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from init import FreelanceAssistant, ask_claude
    
    print("=== HTML INTERCEPTION TEST ===")
    print()
    
    assistant = FreelanceAssistant()
    
    # Set up user info for testing
    assistant.user_info = {
        "name": "HTML Test User",
        "service_type": "web development", 
        "email_address": "test@html.com"
    }
    
    print("📊 Testing HTML interception...")
    print("When Claude returns HTML, it should be rewritten to 'Code generated'")
    print()
    
    # Test 1: Direct HTML interception
    print("🧪 Test 1: Direct HTML response interception")
    sample_html_response = """
    Here's a simple website for you:
    
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Site</title>
    </head>
    <body>
        <h1>Hello World</h1>
    </body>
    </html>
    
    This website is ready to use!
    """
    
    intercepted = assistant.intercept_html_response(sample_html_response)
    print(f"Original response length: {len(sample_html_response)} characters")
    print(f"Intercepted response: '{intercepted}'")
    
    if intercepted == "Code generated":
        print("✅ HTML successfully intercepted and rewritten")
    else:
        print("❌ HTML interception failed")
    
    print()
    
    # Test 2: Check if HTML was stored
    expected_file = "www/htmltestuser.html"
    if os.path.exists(expected_file):
        print("✅ HTML was automatically stored via build_website function")
        with open(expected_file, 'r') as f:
            content = f.read()
        print(f"📏 Stored HTML size: {len(content)} characters")
        
        if "Hello World" in content and "Test Site" in content:
            print("✅ Stored HTML contains expected content")
        else:
            print("❌ Stored HTML missing expected content")
    else:
        print("❌ HTML was not stored automatically")
    
    print()
    
    # Test 3: Real Claude API with HTML interception
    print("🧪 Test 3: Real Claude API with HTML interception")
    
    # Ask Claude to create HTML (should be intercepted)
    html_prompt = "Create a simple HTML page with a header saying 'Test Page' and a paragraph saying 'This is a test'."
    
    # Use the enhanced ask_claude with interception
    response = ask_claude(
        html_prompt, 
        max_tokens=500, 
        intercept_html=True, 
        assistant_instance=assistant
    )
    
    print(f"Claude's response: '{response}'")
    
    if response == "Code generated":
        print("✅ Real Claude HTML response successfully intercepted")
    else:
        print("❌ Real Claude HTML response not intercepted")
        print(f"Response was: {response[:100]}...")
    
    print()
    
    # Test 4: Non-HTML response (should pass through)
    print("🧪 Test 4: Non-HTML response (should pass through unchanged)")
    
    normal_response = "Hello! I'm here to help you with your freelance business."
    intercepted_normal = assistant.intercept_html_response(normal_response)
    
    if intercepted_normal == normal_response:
        print("✅ Non-HTML response correctly passed through unchanged")
    else:
        print("❌ Non-HTML response was incorrectly modified")
    
    print()
    print("🎯 SUMMARY:")
    print("- HTML responses are detected and rewritten to 'Code generated'")
    print("- HTML content is automatically extracted and stored via build_website()")
    print("- Non-HTML responses pass through unchanged")
    print("- Users never see HTML code, only friendly messages")
    
except Exception as e:
    print(f"Test error: {e}")
    import traceback
    traceback.print_exc()