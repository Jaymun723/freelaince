#!/usr/bin/env python3

# Test improved website creation with clean HTML output
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from init import FreelanceAssistant
    
    print("=== Clean Website Creation Test ===")
    print()
    
    assistant = FreelanceAssistant()
    
    # Set up user info
    assistant.user_info = {
        "name": "Sarah",
        "service_type": "photography", 
        "email_address": "sarah@gmail.com"
    }
    
    print("📊 Testing clean HTML generation...")
    print("🎯 Should create pure HTML without any markdown or explanatory text")
    print()
    
    # Create website prompt (similar to what happens in create_website_immediately)
    name = assistant.user_info.get('name')
    service = assistant.user_info.get('service_type')
    email = assistant.user_info.get('email_address')
    
    website_prompt = f"""
    IMPORTANT: Return ONLY pure HTML code - no explanations, no markdown code blocks, no additional text.

    Create a complete, professional one-page HTML website for {name} who offers {service} services.
    
    Requirements:
    - Single HTML file with embedded CSS
    - Professional header with {name}'s name and {service} tagline
    - About section highlighting {name} and their {service} background
    - Services section describing what {service} services they offer
    - Contact section with email: {email}
    - Modern, responsive design
    - Professional color scheme
    
    Return ONLY the HTML code starting with <!DOCTYPE html> and ending with </html>. No markdown, no explanations.
    """
    
    # Import the ask_claude function
    from init import ask_claude
    
    print("🚀 Generating website with Claude API...")
    raw_html = ask_claude(website_prompt, max_tokens=4000)
    
    print(f"📏 Raw response length: {len(raw_html)} characters")
    print("🔍 First 100 characters of raw response:")
    print(repr(raw_html[:100]))
    print()
    
    print("🧹 Cleaning HTML response...")
    clean_html = assistant.clean_html_response(raw_html)
    
    print(f"📏 Clean response length: {len(clean_html)} characters")
    print("🔍 First 100 characters of clean response:")
    print(repr(clean_html[:100]))
    print()
    
    # Save the clean HTML
    filename = "clean_test_website.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(clean_html)
    
    print(f"✅ Clean website saved as '{filename}'")
    print("🌐 Check the file to verify it contains only pure HTML")
    
    # Check if it starts with proper HTML
    if clean_html.strip().startswith('<!DOCTYPE html>'):
        print("✅ Clean HTML starts with proper DOCTYPE")
    else:
        print("❌ Clean HTML doesn't start with DOCTYPE")
        print(f"Actually starts with: {clean_html[:50]}")
    
except Exception as e:
    print(f"Test error: {e}")
    import traceback
    traceback.print_exc()