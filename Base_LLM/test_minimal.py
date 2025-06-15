#!/usr/bin/env python3

# Minimal test to check basic functionality
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from init import FreelanceAssistant
    
    print("=== MINIMAL TEST ===")
    
    assistant = FreelanceAssistant()
    assistant.user_info = {
        "name": "Test User",
        "service_type": "testing", 
        "email_address": "test@example.com"
    }
    
    print("Testing HTML detection...")
    
    # Simple HTML test
    html_input = "<!DOCTYPE html><html><body>Test</body></html>"
    
    print("Calling intercept_html_response...")
    result = assistant.intercept_html_response(html_input)
    print(f"Result: {result}")
    
    print("Test completed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()