#!/usr/bin/env python3

# Test email validation functionality
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from init import FreelanceAssistant
    
    print("=== Email Validation Test ===")
    print()
    
    assistant = FreelanceAssistant()
    
    # Test various email formats
    test_emails = [
        # Valid emails
        ("john@gmail.com", True),
        ("sarah.photo@gmail.com", True),
        ("user123@yahoo.com", True),
        ("test.email@domain.co.uk", True),
        ("name_test@outlook.com", True),
        
        # Invalid emails
        ("", False),
        ("   ", False),
        ("plaintext", False),
        ("@gmail.com", False),
        ("user@", False),
        ("user@@gmail.com", False),
        ("user@gmail", False),
        ("user@.com", False),
        ("user@gmail.", False),
        ("user name@gmail.com", False),
        ("user@gmai l.com", False),
    ]
    
    print("Testing email validation:")
    print("-" * 50)
    
    for email, expected_valid in test_emails:
        is_valid, message = assistant.validate_email_format(email)
        status = "✅ PASS" if (is_valid == expected_valid) else "❌ FAIL"
        
        print(f"{status} | '{email}' -> {is_valid} ({message})")
    
    print()
    print("=== Interactive Demo ===")
    print("Try entering some invalid emails to see the validation in action:")
    print("Examples to try:")
    print("- 'plaintext' (missing @)")
    print("- 'user@' (missing domain)")
    print("- 'user@@gmail.com' (double @)")
    print("- 'user@gmail' (missing .com)")
    print("- '' (empty)")
    print("- Finally enter a valid email like 'test@gmail.com'")
    print()
    
    # Set up some test data
    assistant.user_info = {"name": "Test User", "service_type": "testing"}
    
    # Test the interactive validation
    assistant.get_and_validate_email()
    
    print(f"\n✅ Final stored email: {assistant.user_info.get('email_address')}")
    
except Exception as e:
    print(f"Test error: {e}")
    import traceback
    traceback.print_exc()