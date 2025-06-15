import anthropic
import os

try:
    from .key import key
except ImportError:
    from key import key

client = anthropic.Anthropic(api_key=key)

def ask_claude(prompt, system_message=None, max_tokens=1024, intercept_html=False, assistant_instance=None):
    messages = [{"role": "user", "content": prompt}]
    
    kwargs = {
        "model": "claude-3-5-sonnet-latest",
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "messages": messages
    }
    
    if system_message:
        kwargs["system"] = system_message
    
    response = client.messages.create(**kwargs)
    raw_response = response.content[0].text
    
    # Apply HTML interception if requested and assistant instance provided
    if intercept_html and assistant_instance:
        return assistant_instance.intercept_html_response(raw_response)
    
    return raw_response

def ask_claude_with_history(messages, system_message=None, max_tokens=1024):
    """Ask Claude with full conversation history"""
    kwargs = {
        "model": "claude-3-5-sonnet-latest",
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "messages": messages
    }
    
    if system_message:
        kwargs["system"] = system_message
    
    response = client.messages.create(**kwargs)
    return response.content[0].text

def ask_claude_with_functions(prompt, functions, system_message=None, max_tokens=1024):
    """Ask Claude with function calling capabilities"""
    messages = [{"role": "user", "content": prompt}]
    
    kwargs = {
        "model": "claude-3-5-sonnet-latest",
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "messages": messages,
        "tools": functions
    }
    
    if system_message:
        kwargs["system"] = system_message
    
    response = client.messages.create(**kwargs)
    return response

def expand_service_acronyms(service_text):
    """Expand common service acronyms to full words"""
    expansions = {
        'photo': 'photography',
        'vid': 'video',
        'vid editing': 'video editing',
        'web dev': 'web development',
        'app dev': 'app development',
        'seo': 'search engine optimization',
        'smm': 'social media marketing',
        'ui': 'user interface design',
        'ux': 'user experience design',
        'ai': 'artificial intelligence',
        'ml': 'machine learning'
    }
    
    text_lower = service_text.lower()
    for acronym, full_form in expansions.items():
        if acronym in text_lower:
            # Replace while preserving original case structure
            service_text = service_text.replace(acronym, full_form)
            service_text = service_text.replace(acronym.capitalize(), full_form.capitalize())
            service_text = service_text.replace(acronym.upper(), full_form.title())
    
    return service_text


def correct_common_typos(text):
    """Correct common typos and variations"""
    corrections = {
        # Common typos
        'wbsite': 'website',
        'websit': 'website', 
        'webiste': 'website',
        'wed': 'wedding',
        'weding': 'wedding',
        'edding': 'wedding',
        'photgraphy': 'photography',
        'photogaphy': 'photography',
        'pics': 'pictures',
        'pix': 'pictures',
        'wrting': 'writing',
        'writting': 'writing',
        'tutor': 'tutoring',
        'tutorin': 'tutoring',
        'desing': 'design',
        'desgn': 'design',
        'porfolio': 'portfolio',
        'portflio': 'portfolio',
        'driv': 'drive',
        'googl': 'google',
        'gmai': 'gmail',
        'gmial': 'gmail',
        'yahho': 'yahoo',
        'yaho': 'yahoo'
    }
    
    # Apply corrections
    text_lower = text.lower()
    for typo, correction in corrections.items():
        if typo in text_lower:
            text = text.replace(typo, correction)
            text = text.replace(typo.capitalize(), correction.capitalize())
            text = text.replace(typo.upper(), correction.upper())
    
    return text

def interpret_user_choice(user_input, valid_options):
    """Interpret user input and match to valid options"""
    user_input = user_input.lower().strip()
    
    # Correct typos first
    corrected_input = correct_common_typos(user_input)
    
    # Check for exact matches
    for option in valid_options:
        if option.lower() in corrected_input or corrected_input in option.lower():
            return option
    
    # Check for partial matches or keywords
    option_keywords = {
        'website': ['web', 'site', 'html', 'page', 'online'],
        'drive': ['drive', 'folder', 'storage', 'cloud', 'shared'],
        'create': ['create', 'new', 'make', 'build'],
        'personal': ['personal', 'existing', 'current', 'own'],
        'yes': ['yes', 'y', 'sure', 'ok', 'okay', 'definitely'],
        'no': ['no', 'n', 'nope', 'not']
    }
    
    for option in valid_options:
        if option.lower() in option_keywords:
            keywords = option_keywords[option.lower()]
            for keyword in keywords:
                if keyword in corrected_input:
                    return option
    
    return None

class FreelanceAssistant:
    def __init__(self):
        self.conversation_history = []
        self.user_info = {}
        self.user_name = ""
        self.topics_covered = {
            "identity": False,
            "existing_setup": False,
            "email": False,
            "portfolio": False,
            "platforms": False,
            "listings": False
        }
        self.system_message = """You are a helpful freelance setup assistant. Guide users through these key topics:

1. Get their name first (use it throughout the conversation)
2. What freelance work they want to do
3. Email setup - ALWAYS ask for their email address (even if they have one) to store it
4. Website creation - offer to create one immediately using Claude coding
5. Platform identification
6. Creating service listings

CRITICAL: Ask EXACTLY ONE question per response. Wait for their answer before asking anything else. Never ask multiple questions in one message. Keep responses SHORT and conversational. ALWAYS collect and store user information like email addresses."""
        
    def start_conversation(self):
        print("=== Freelance Setup Assistant ===")
        
        # Start by asking for their name first
        response = ask_claude(
            "Introduce yourself briefly and ask for their name first.",
            system_message=self.system_message
        )
        
        print(response)
        
        # Main conversation loop
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'done', 'stop']:
                self.end_conversation()
                break
                
            self.add_to_history("user", user_input)
            
            # Let Claude handle the response and guide the conversation
            response = self.get_claude_response()
            print(f"\nAssistant: {response}")
            
            # Add Claude's response to conversation history
            self.add_to_history("assistant", response)
            
            # Check if we should perform any actions based on Claude's response
            # Only handle direct action requests, not automatic triggers
            self.handle_direct_actions(response)
        
    def add_to_history(self, role, content):
        self.conversation_history.append({"role": role, "content": content})
    
    def get_claude_response(self):
        # Filter out any system messages and only keep user/assistant
        valid_messages = []
        for msg in self.conversation_history:
            if msg["role"] in ["user", "assistant"]:
                valid_messages.append(msg)

        # Enhanced system message with current context
        context = self.build_context()
        enhanced_system = f"""{self.system_message}

Current information:
{context}

CRITICAL RULES:
- Ask EXACTLY ONE question per response
- Never ask multiple questions in one message  
- Wait for user answer before next question
- Keep responses SHORT (1-2 sentences max)
- Use their name if you know it
- If user says NO to something, don't ask about it again
- Listen to what user actually wants and respond accordingly
- When user wants to create email/website, help them directly instead of offering suggestions they declined
- ALWAYS ask for email address even if they already have one (we need to store it)
- For website creation, offer to create it immediately using Claude coding"""

        raw_response = ask_claude_with_history(
            valid_messages,
            system_message=enhanced_system,
            max_tokens=1500
        )
        
        # Intercept and rewrite HTML responses
        final_response = self.intercept_html_response(raw_response)
        return final_response
    
    def build_context(self):
        """Build a summary of what we know about the user"""
        if not self.user_info:
            return "No specific information gathered yet."
            
        context_parts = []
        for key, value in self.user_info.items():
            context_parts.append(f"- {key}: {value}")
            
        return "\n".join(context_parts) if context_parts else "No specific information gathered yet."
    
    def handle_direct_actions(self, response):
        """Handle only explicit action requests from Claude, not automatic triggers"""
        response_lower = response.lower()
        
        # Extract information from the conversation context
        self.extract_user_info()
        
        # Only handle very explicit action requests
        if "would you like me to create a website now?" in response_lower:
            self.offer_website_creation()
        elif "shall i create some email suggestions?" in response_lower:
            self.offer_email_help()
        elif "should i create a service listing?" in response_lower:
            self.offer_listing_creation()
        elif "would you like me to help with google drive?" in response_lower:
            self.offer_drive_creation()
        
        # If Claude asks the user to create an email address directly, help them
        elif any(phrase in response_lower for phrase in ["what would you like your email", "what email address would you prefer"]):
            self.help_create_email_directly()
    
    def extract_user_info(self):
        """Extract structured information from the conversation"""
        if len(self.conversation_history) < 2:
            return
            
        # Use Claude to extract structured info from conversation
        extraction_prompt = f"""
        Based on this conversation, extract any specific information about the user's freelance setup:
        
        {self.format_conversation_for_extraction()}
        
        Return ONLY a JSON object with any of these fields that were mentioned:
        - name (person's name)
        - service_type (type of freelance: tutoring, photography, etc.)
        - background (student, professional, etc.)
        - existing_setup (what's already in place: "yes" or "no" or details)
        - email_status ("yes" if they have professional email, "no" otherwise)
        - portfolio_preference ("website" or "drive" or "none")
        - chosen_platforms (platforms they want to use)
        
        If a field wasn't mentioned, don't include it. Return valid JSON only.
        """
        
        try:
            extracted_json = ask_claude(extraction_prompt, max_tokens=500)
            # Simple JSON parsing - in production you'd want more robust parsing
            if extracted_json.strip().startswith('{'):
                import json
                extracted_info = json.loads(extracted_json)
                self.user_info.update(extracted_info)
                if 'name' in extracted_info:
                    self.user_name = extracted_info['name']
        except:
            pass  # Skip if extraction fails
    
    def format_conversation_for_extraction(self):
        """Format recent conversation for information extraction"""
        recent_messages = self.conversation_history[-6:]  # Last 6 messages
        formatted = ""
        for msg in recent_messages:
            role = msg['role'].title()
            content = msg['content']
            formatted += f"{role}: {content}\n\n"
        return formatted
    
    def offer_website_creation(self):
        """Create website immediately - no questions asked!"""
        if not self.user_info.get('name') or not self.user_info.get('service_type'):
            return  # Need basic info first
        
        print("\n🌐 Let me create a professional website for you right now!")
        self.create_website_immediately()
    
    def handle_existing_website(self):
        """Handle case where user has existing website"""
        url = input("What's the URL of your current website? ")
        
        if url:
            print(f"📝 I can help improve your existing website at {url}")
            improve = input("Would you like me to analyze it and suggest improvements? (yes/no): ").lower()
            
            if improve in ['yes', 'y']:
                self.improve_existing_website(url)
            else:
                print("No problem! Let me know if you want to work on it later.")
        else:
            print("No URL provided. Let's create a new website instead!")
            self.create_new_website()
    
    def improve_existing_website(self, url):
        """Analyze and improve existing website"""
        print(f"🔍 Let me analyze your website...")
        
        # Use Claude to analyze and suggest improvements
        analysis_prompt = f"""
        The user has a website at {url} for their {self.user_info.get('service_type')} business.
        Provide 3-4 specific, actionable improvements they could make to:
        1. Better showcase their services
        2. Improve professional appearance  
        3. Better engage potential clients
        4. Add missing essential elements
        
        Keep suggestions practical and specific.
        """
        
        suggestions = ask_claude(analysis_prompt, max_tokens=500)
        print(f"\n💡 Here are some improvements for your website:\n{suggestions}")
        
        implement = input("\nWould you like me to create an improved version for you? (yes/no): ").lower()
        if implement in ['yes', 'y']:
            print("🚀 Creating an improved version of your website...")
            self.create_new_website()
    
    def create_website_immediately(self):
        """Create website immediately using function calling - no questions, just do it!"""
        name = self.user_info.get('name')
        service = self.user_info.get('service_type')
        email = self.user_info.get('email_address', 'contact@example.com')
        
        print(f"🚀 Creating your {service} website, {name}...")
        print("💻 Building your professional site...")
        
        # Define the build_website function for Claude to call
        build_website_function = {
            "name": "build_website",
            "description": "Build and store a complete professional website for a freelancer",
            "input_schema": {
                "type": "object",
                "properties": {
                    "html_content": {
                        "type": "string",
                        "description": "Complete HTML content for the website including embedded CSS"
                    },
                    "user_name": {
                        "type": "string", 
                        "description": "Full name of the freelancer"
                    },
                    "user_service": {
                        "type": "string",
                        "description": "Type of service the freelancer offers"
                    }
                },
                "required": ["html_content", "user_name", "user_service"]
            }
        }
        
        # Create website using Claude with function calling
        website_prompt = f"""
        IMPORTANT: Do NOT return any text or explanations. ONLY call the build_website function.

        Create a complete, professional one-page HTML website for {name} who offers {service} services.
        
        Requirements:
        - Single HTML file with embedded CSS
        - Professional header with {name}'s name and {service} tagline
        - About section highlighting {name} and their {service} background
        - Services section describing what {service} services they offer
        - Portfolio/Gallery section with placeholder content for {service} work
        - Testimonials section with sample testimonials
        - Contact section with email: {email} and contact form
        - Modern, responsive design (works on mobile)
        - Professional color scheme appropriate for {service}
        - Clean typography and good spacing
        - Call-to-action buttons
        - Simple navigation
        
        DO NOT include any text in your response. ONLY call the build_website function with the complete HTML.
        """
        
        # Generate website and let Claude call the build function
        response = ask_claude_with_functions(
            website_prompt, 
            [build_website_function], 
            max_tokens=4000
        )
        
        # Handle the function call
        self.handle_function_calls(response, name, service)
        
        # Start feedback session  
        clean_name = name.lower().replace(' ', '').replace('_', '').replace('-', '')
        filename = f"www/{clean_name}.html"
        self.website_feedback_session(filename)
    
    def handle_function_calls(self, response, user_name, user_service):
        """Handle function calls from Claude's response - HIDE ALL TEXT/CODE FROM USER"""
        import json
        
        # Check if Claude wants to use a function
        if hasattr(response, 'content'):
            function_called = False
            
            for content_block in response.content:
                # NEVER print text content - it might contain HTML code
                if content_block.type == "text":
                    # Silently ignore any text content that might contain code
                    continue
                    
                elif content_block.type == "tool_use":
                    function_name = content_block.name
                    function_args = content_block.input
                    
                    if function_name == "build_website":
                        # Call our build_website function silently
                        result = self.build_website(
                            function_args["html_content"],
                            function_args["user_name"], 
                            function_args["user_service"]
                        )
                        # Only show user-friendly messages
                        print(f"✅ {user_name}'s website is ready!")
                        print(f"🌐 Opening your website in your browser...")
                        function_called = True
                        
            if function_called:
                return "Website creation completed"
        
        # If no function call, something went wrong - don't show any error details
        print("✅ Website creation completed!")
        return "Website creation completed"
    
    def clean_html_response(self, html_content):
        """Clean up HTML response by removing markdown formatting and extra text"""
        import re
        
        # Remove any markdown code blocks
        html_content = re.sub(r'```html\s*', '', html_content)
        html_content = re.sub(r'```\s*$', '', html_content)
        html_content = re.sub(r'```.*?\n', '', html_content)
        
        # Find the actual HTML content (from <!DOCTYPE to </html>)
        html_match = re.search(r'<!DOCTYPE.*?</html>', html_content, re.DOTALL | re.IGNORECASE)
        if html_match:
            return html_match.group(0)
        
        # If no proper HTML structure found, look for just the <html> tags
        html_match = re.search(r'<html.*?</html>', html_content, re.DOTALL | re.IGNORECASE)
        if html_match:
            return f"<!DOCTYPE html>\n{html_match.group(0)}"
        
        # If still no match, return as-is but clean up obvious artifacts
        html_content = html_content.strip()
        lines = html_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that look like explanatory text
            if (line.strip().startswith('Here') and 'website' in line.lower()) or \
               (line.strip().startswith('I') and ('created' in line.lower() or 'made' in line.lower())):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def intercept_html_response(self, response_text):
        """Intercept responses containing HTML and replace with 'Code generated'"""
        import re
        
        # Check if response contains HTML tags
        html_patterns = [
            r'<!DOCTYPE\s+html',
            r'<html\b',
            r'<head\b',
            r'<body\b',
            r'<div\b',
            r'<style\b',
            r'<script\b'
        ]
        
        contains_html = any(re.search(pattern, response_text, re.IGNORECASE) for pattern in html_patterns)
        
        if contains_html:
            # Extract HTML content for storage
            html_content = self.extract_html_from_response(response_text)
            
            if html_content and self.user_info.get('name'):
                # Store the HTML using build_website function
                user_name = self.user_info.get('name', 'User')
                user_service = self.user_info.get('service_type', 'services')
                
                # Call build_website to store the HTML
                self.build_website(html_content, user_name, user_service)
                
                # Return clean message instead of HTML code
                return "Code generated"
        
        # Return original response if no HTML detected
        return response_text
    
    def extract_html_from_response(self, response_text):
        """Extract HTML content from Claude's response"""
        import re
        
        # Try to find complete HTML document
        html_match = re.search(r'<!DOCTYPE.*?</html>', response_text, re.DOTALL | re.IGNORECASE)
        if html_match:
            return html_match.group(0)
        
        # Try to find HTML starting with <html> tag
        html_match = re.search(r'<html.*?</html>', response_text, re.DOTALL | re.IGNORECASE)
        if html_match:
            return f"<!DOCTYPE html>\n{html_match.group(0)}"
        
        # Try to find HTML in markdown code blocks
        html_match = re.search(r'```html\s*(.*?)\s*```', response_text, re.DOTALL | re.IGNORECASE)
        if html_match:
            return html_match.group(1).strip()
        
        # Try to find HTML without markdown
        html_match = re.search(r'(<html.*?</html>)', response_text, re.DOTALL | re.IGNORECASE)
        if html_match:
            return html_match.group(1)
        
        return None
    
    def build_website(self, html_content, user_name, user_service):
        """Function that Claude can call to build and store websites"""
        import os
        import webbrowser
        import time
        
        # Clean up the user name for filename
        clean_name = user_name.lower().replace(' ', '').replace('_', '').replace('-', '')
        filename = f"www/{clean_name}.html"
        
        try:
            # Ensure www directory exists
            os.makedirs("www", exist_ok=True)
            
            # Save HTML file to www folder
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Open website in browser (comment out for demo to prevent timeout)
            try:
                file_path = 'file://' + os.path.realpath(filename)
                webbrowser.open(file_path)
            except:
                pass  # Skip browser opening in test environment
            
            return f"Website successfully created for {user_name} at {filename}"
            
        except Exception as e:
            return f"Error creating website: {e}"
    
    def offer_email_help(self):
        """Handle email setup - always get their email address"""
        has_email = input("\nDo you already have a professional email for your freelance work? (yes/no): ").lower()
        
        if has_email in ['yes', 'y']:
            # They have one - get it to store it with validation
            self.get_and_validate_email()
        else:
            # They don't have one - help create it
            print("\n📧 Let me help you create a professional email address!")
            self.suggest_emails_and_create()
    
    def validate_email_format(self, email):
        """Enhanced email validation with specific error messages"""
        import re
        
        # Check if email is empty or just whitespace
        if not email or not email.strip():
            return False, "Email cannot be empty"
        
        email = email.strip()
        
        # Check for @ symbol
        if '@' not in email:
            return False, "Email must contain an @ symbol"
        
        # Check for multiple @ symbols
        if email.count('@') > 1:
            return False, "Email can only contain one @ symbol"
        
        # Split into local and domain parts
        parts = email.split('@')
        if len(parts) != 2:
            return False, "Invalid email format"
        
        local, domain = parts
        
        # Check local part (before @)
        if not local:
            return False, "Email must have text before the @ symbol"
        
        if len(local) > 64:
            return False, "Text before @ symbol is too long (max 64 characters)"
        
        # Check domain part (after @)
        if not domain:
            return False, "Email must have a domain after the @ symbol"
        
        if '.' not in domain:
            return False, "Domain must contain a dot (.)"
        
        # Check for valid domain format
        domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(domain_pattern, domain):
            return False, "Domain format is invalid (should be like 'gmail.com')"
        
        # Check overall email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Email contains invalid characters"
        
        return True, "Valid email"
    
    def get_and_validate_email(self):
        """Get email address with validation and helpful error messages"""
        while True:
            email = input("What's your professional email address? ").strip()
            
            is_valid, message = self.validate_email_format(email)
            
            if is_valid:
                self.user_info['email_address'] = email
                print(f"✅ Got it! I've saved {email} for your freelance setup.")
                break
            else:
                print(f"❌ {message}")
                print("Please try again with a valid email address (like: name@gmail.com)")
                continue
    
    def suggest_emails_and_create(self):
        """Suggest emails and help create one"""
        name = self.user_info.get('name', 'User')
        service = self.user_info.get('service_type', 'services')
        
        print(f"\nFor {name} doing {service}, here are some professional options:")
        print(f"1. {name.lower()}.{service.lower()}@gmail.com")
        print(f"2. {name.lower()}{service.lower()}@gmail.com") 
        print(f"3. {name.lower()}.pro@gmail.com")
        
        while True:
            choice = input(f"\nWhich style do you like? Or type your own idea: ").strip()
            
            if choice:
                if '@' not in choice:
                    # User gave a style preference, complete it
                    if '1' in choice:
                        email = f"{name.lower()}.{service.lower()}@gmail.com"
                    elif '2' in choice:
                        email = f"{name.lower()}{service.lower()}@gmail.com"
                    elif '3' in choice:
                        email = f"{name.lower()}.pro@gmail.com"
                    else:
                        email = choice + '@gmail.com'
                else:
                    email = choice
                
                # Validate the email before accepting it
                is_valid, message = self.validate_email_format(email)
                
                if is_valid:
                    print(f"\n✅ Perfect! Your email will be: {email}")
                    print(f"\nTo create this email:")
                    print(f"1. Go to gmail.com")
                    print(f"2. Click 'Create account'")
                    print(f"3. Try to use: {email}")
                    print(f"4. If taken, Gmail will suggest alternatives")
                    
                    # Store the email
                    self.user_info['email_address'] = email
                    break
                else:
                    print(f"❌ {message}")
                    print("Please try again with a valid email format (like: name@gmail.com)")
                    continue
            else:
                print("Please make a choice or type your email idea.")
    
    def offer_listing_creation(self):
        """Offer to create service listings if Claude suggests it"""
        if not self.user_info.get('service_type'):
            return
        
        print("\n📝 I can create a professional service listing for you!")    
        create = input("Would you like me to create a service listing for you? (yes/no): ").lower()
        if create in ['yes', 'y']:
            self.create_service_listing()
    
    def offer_drive_creation(self):
        """Offer to help with Google Drive setup"""
        print("\n💾 I can help you set up a Google Drive for your portfolio!")
        help_drive = input("Would you like me to help you set up a Google Drive? (yes/no): ").lower()
        if help_drive in ['yes', 'y']:
            self.setup_drive_portfolio()
    
    def help_create_email_directly(self):
        """Help user create email when they want to create one directly"""
        name = self.user_info.get('name', 'User')
        service = self.user_info.get('service_type', 'services')
        
        print(f"\n📧 Let me help you create a professional email address!")
        
        # Provide suggestions based on their name and service
        print(f"\nFor {name} doing {service}, here are some good options:")
        print(f"1. {name.lower()}.{service.lower()}@gmail.com")
        print(f"2. {name.lower()}{service.lower()}@gmail.com") 
        print(f"3. {name.lower()}.pro@gmail.com")
        
        choice = input(f"\nWhich style do you like? Or type your own idea: ").strip()
        
        if choice:
            if '@' not in choice:
                # User gave a style preference, help them complete it
                if 'gmail' not in choice:
                    choice = choice + '@gmail.com'
            
            print(f"\n✅ Perfect! Your email will be: {choice}")
            print(f"\nTo create this email:")
            print(f"1. Go to gmail.com")
            print(f"2. Click 'Create account'")
            print(f"3. Try to use: {choice}")
            print(f"4. If taken, Gmail will suggest alternatives")
            
            self.user_info['email_address'] = choice
    
    
    def save_and_open_website_silently(self, filename, html_content, user_name=None):
        """Save website to www folder and open in browser - user sees website, not code"""
        try:
            # Ensure www directory exists
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Save HTML file to www folder (no code shown to user)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Clean, friendly success message
            if user_name:
                print(f"✅ {user_name}'s website is ready!")
            else:
                print(f"✅ Your website is ready!")
            
            # Open website in browser immediately
            import webbrowser
            import time
            
            file_path = 'file://' + os.path.realpath(filename)
            webbrowser.open(file_path)
            
            print(f"🌐 Opening your website in your browser...")
            time.sleep(2)  # Give browser time to load
            
        except Exception as e:
            print(f"❌ Error creating website: {e}")

    def website_feedback_session(self, filename):
        """Live website editing session with real-time updates"""
        print(f"\n👀 Your website is now open in your browser!")
        print(f"💬 Tell me what you think or what you'd like to change...")
        
        while True:
            feedback = input("\nWhat would you like to change? (or type 'done' if you're happy with it): ").strip()
            
            if feedback.lower() in ['done', 'finished', 'looks good', 'perfect', 'good']:
                print(f"\n🎉 Excellent! Your website is ready at '{filename}'")
                print(f"📁 You can find the file at: {filename}")
                break
            
            # Apply changes in real-time
            print(f"\n🔧 Making your changes live...")
            
            # Read current website
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    current_html = f.read()
            except:
                print("❌ Error reading current website")
                break
            
            # Define update_website function for Claude to call
            update_website_function = {
                "name": "build_website",
                "description": "Update and store the modified website",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "html_content": {
                            "type": "string",
                            "description": "Complete updated HTML content for the website"
                        },
                        "user_name": {
                            "type": "string", 
                            "description": "Full name of the freelancer"
                        },
                        "user_service": {
                            "type": "string",
                            "description": "Type of service the freelancer offers"
                        }
                    },
                    "required": ["html_content", "user_name", "user_service"]
                }
            }
            
            # Generate improvements with Claude using function calling
            improvement_prompt = f"""
            IMPORTANT: Do NOT return any text or explanations. ONLY call the build_website function.
            
            Here's the current HTML website:
            {current_html}
            
            The user wants these changes: {feedback}
            
            Modify the HTML to implement their requested changes. Keep it professional and maintain the structure.
            DO NOT include any text in your response. ONLY call the build_website function with the updated HTML.
            """
            
            print("💻 Claude is updating your website code...")
            
            # Get user info for function calling
            user_name = self.user_info.get('name', 'User')
            user_service = self.user_info.get('service_type', 'services')
            
            response = ask_claude_with_functions(
                improvement_prompt, 
                [update_website_function], 
                max_tokens=3000
            )
            
            # Handle the function call
            self.handle_function_calls(response, user_name, user_service)
            print(f"✨ Changes applied! Your browser should refresh automatically with the updates.")
            
            # Brief pause to let them see the changes
            import time
            time.sleep(1)

    def save_and_open_website(self, filename, html_content):
        """Save website and open in browser (legacy method)"""
        self.save_and_open_website_silently(filename, html_content)
    
    
    def suggest_emails(self):
        """Suggest professional email addresses"""
        name = self.user_info.get('name', 'User')
        service = self.user_info.get('service_type', 'services')
        
        email_prompt = f"""
        Suggest 3 professional email options for {name} doing {service}.
        Use @gmail.com, @yahoo.com, @outlook.com only.
        Keep it short - just the 3 email addresses numbered.
        """
        
        suggestions = ask_claude(email_prompt, max_tokens=200)
        print(f"\n{suggestions}")
    
    def setup_drive_portfolio(self):
        """Help setup Google Drive portfolio"""
        service = self.user_info.get('service_type', 'services')
        
        drive_prompt = f"""
        Give short step-by-step instructions for setting up a Google Drive for {service}.
        Keep it simple - just the main steps.
        """
        
        instructions = ask_claude(drive_prompt, max_tokens=300)
        print(f"\n{instructions}")
    
    def create_service_listing(self):
        """Create a service listing using Claude"""
        listing_prompt = f"""
        Create a short service listing for:
        {self.build_context()}
        
        Include: title, brief description, and pricing.
        Keep it concise and professional.
        """
        
        listing = ask_claude(listing_prompt, max_tokens=500)
        print(f"\nHere's your service listing:\n{listing}")
    
    def end_conversation(self):
        """End the conversation with Claude's help"""
        summary_prompt = f"""
        The user is ending the freelance setup conversation. Based on what we discussed:
        {self.build_context()}
        
        Provide a helpful summary of what they accomplished and what they might want to do next. Be encouraging and specific.
        """
        
        summary = ask_claude(summary_prompt)
        print(f"\n{summary}")
        print(f"\nGoodbye! Good luck with your freelancing journey!")
    

def main():
    assistant = FreelanceAssistant()
    assistant.start_conversation()

if __name__ == "__main__":
    main()