#!/usr/bin/env python3
import asyncio
import websockets
import json
import time
import random
import signal
import sys
import csv
import uuid
from datetime import datetime
import os
import importlib.util
from pathlib import Path

class FreelainceServer:
    def __init__(self):
        self.clients = {}  # {client_id: {'websocket': ws, 'ip': ip, 'connected_at': timestamp}}
        self.port = 8080
        self.host = 'localhost'
        self.csv_file = 'conversations.csv'
        self.processed_messages = set()  # Track processed messages to prevent duplicates
        self.shutdown = False  # Shutdown flag
        self.offer_manager = None  # Will be initialized if Erwan system is available
        self.schedule_manager = None  # Will be initialized if schedule system is available
        self.setup_csv_logging()
        self.init_offer_system()
        self.init_schedule_system()
        
    def setup_csv_logging(self):
        """Initialize CSV file for conversation logging"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['date', 'sender', 'message', 'client_id', 'client_ip', 'timestamp'])
                
    def log_to_csv(self, sender, message, client_id, client_ip):
        """Log conversation to CSV file"""
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    datetime.now().isoformat(),
                    sender,
                    message,
                    client_id,
                    client_ip,
                    int(time.time() * 1000)
                ])
        except Exception as e:
            print(f"⚠️ Error logging to CSV: {e}")
    
    def init_offer_system(self):
        """Initialize the Erwan offer management system if available"""
        try:
            # Try to import the Erwan offer management system
            erwan_path = Path(__file__).parent.parent / "Erwan"
            if erwan_path.exists():
                sys.path.insert(0, str(erwan_path))
                
                # Import the offer management classes
                from offer_manager import OfferManager, PhotographyOffer, OfferFinder
                
                self.offer_manager = OfferManager()
                
                # Try to load existing offers from pickle file
                offers_file = erwan_path / "offers_backup.pickle"
                if offers_file.exists():
                    try:
                        self.offer_manager.load_from_file(str(offers_file), "pickle")
                        print(f"✅ Loaded {len(self.offer_manager)} existing offers from Erwan system")
                    except Exception as e:
                        print(f"⚠️ Could not load existing offers: {e}")
                        
                # Create sample offers if none exist
                if len(self.offer_manager) == 0:
                    self.create_sample_offers()
                    
                print("🎯 Offer management system initialized successfully")
                
            else:
                print("⚠️ Erwan offer system not found - offers functionality will use sample data")
                
        except ImportError as e:
            print(f"⚠️ Could not import Erwan offer system: {e}")
        except Exception as e:
            print(f"⚠️ Error initializing offer system: {e}")
    
    def init_schedule_system(self):
        """Initialize the schedule management system if available"""
        try:
            # Try to import the schedule management system
            schedule_path = Path(__file__).parent.parent / "schedule"
            if schedule_path.exists():
                sys.path.insert(0, str(schedule_path))
                
                # Import the schedule management classes
                from schedule_agent import ScheduleManager, Event
                
                self.schedule_manager = ScheduleManager()
                print(f"✅ Loaded {len(self.schedule_manager.events)} existing events from schedule system")
                print("📅 Schedule management system initialized successfully")
                
            else:
                print("⚠️ Schedule system not found - calendar functionality will use sample data")
                
        except ImportError as e:
            print(f"⚠️ Could not import schedule system: {e}")
        except Exception as e:
            print(f"⚠️ Error initializing schedule system: {e}")
    
    def create_sample_offers(self):
        """Create sample offers for demonstration"""
        try:
            from offer_manager import PhotographyOffer
            
            # Sample photography offers
            sample_offers = [
                {
                    'client_name': 'Sarah Johnson',
                    'client_contact': 'sarah@johsonevents.com',
                    'client_company': 'Johnson Events Co.',
                    'job_description': 'Wedding photography for outdoor ceremony and reception. Need professional photographer with experience in natural lighting and candid shots.',
                    'date_time': datetime(2024, 12, 20, 14, 0),
                    'duration': '8 hours',
                    'location': 'Central Park, New York',
                    'payment_terms': '$2,500 for full day coverage',
                    'requirements': 'Professional camera equipment, 2+ years experience, portfolio required',
                    'event_type': 'wedding',
                    'photos_expected': 500,
                    'equipment_requirements': ['DSLR Camera', 'External Flash', 'Backup Equipment'],
                    'post_processing_requirements': 'Color correction, basic retouching, album-ready edits',
                    'delivery_format': 'digital_download',
                    'delivery_timeline': '2 weeks after event',
                    'additional_services': ['Engagement shoot', 'Print package'],
                    'source_url': 'https://example.com/wedding-photographer-needed'
                },
                {
                    'client_name': 'Tech Corp Inc.',
                    'client_contact': '+1-555-0123',
                    'client_company': 'Tech Corp Inc.',
                    'job_description': 'Corporate headshots for new employees. Professional business portraits needed for company website and marketing materials.',
                    'date_time': datetime(2024, 6, 25, 9, 0),
                    'duration': '4 hours',
                    'location': 'Downtown Office Building',
                    'payment_terms': '$150 per person (20 people)',
                    'requirements': 'Studio lighting setup, professional backdrop, business attire coordination',
                    'event_type': 'corporate',
                    'photos_expected': 60,
                    'equipment_requirements': ['Studio Lights', 'Backdrop', 'Professional Camera'],
                    'post_processing_requirements': 'Professional retouching, consistent lighting, business-appropriate editing',
                    'delivery_format': 'cloud_storage',
                    'delivery_timeline': '1 week after shoot',
                    'additional_services': ['LinkedIn profile optimization'],
                    'source_url': 'https://example.com/corporate-headshots'
                },
                {
                    'client_name': 'Maria Rodriguez',
                    'client_contact': 'maria.r@email.com',
                    'client_company': 'Self',
                    'job_description': 'Family portrait session at sunset. Looking for natural, candid shots of family of 5 including grandparents.',
                    'date_time': datetime(2024, 6, 18, 16, 0),
                    'duration': '2 hours',
                    'location': 'Beach Location, Miami',
                    'payment_terms': '$800 for 2-hour session',
                    'requirements': 'Experience with family photography, good with children, natural lighting expertise',
                    'event_type': 'family',
                    'photos_expected': 100,
                    'equipment_requirements': ['DSLR Camera', 'Prime Lens', 'Reflector'],
                    'post_processing_requirements': 'Natural color grading, light retouching, family-friendly editing',
                    'delivery_format': 'digital_download',
                    'delivery_timeline': '1 week after session',
                    'additional_services': ['Printed album options'],
                    'source_url': 'https://example.com/family-portraits'
                }
            ]
            
            for offer_data in sample_offers:
                try:
                    offer = PhotographyOffer(**offer_data)
                    offer_id = self.offer_manager.add_offer(offer)
                    print(f"✅ Created sample offer: {offer_id[:8]} - {offer.client_name}")
                except Exception as e:
                    print(f"⚠️ Error creating sample offer: {e}")
                    
        except Exception as e:
            print(f"⚠️ Error creating sample offers: {e}")
    
    def load_conversation_history(self, client_ip, limit=50):
        """Load recent conversation history for a client IP"""
        history = []
        try:
            if not os.path.exists(self.csv_file):
                return history
                
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                all_rows = list(reader)
                
                # Filter messages for this IP, exclude system messages
                relevant_messages = [
                    row for row in all_rows 
                    if row['client_ip'] == client_ip and 
                    row['sender'] in ['user', 'bot']
                ]
                
                # Get the last N messages
                recent_messages = relevant_messages[-limit:] if len(relevant_messages) > limit else relevant_messages
                
                for row in recent_messages:
                    history.append({
                        'sender': row['sender'],
                        'message': row['message'],
                        'timestamp': row['date'],
                        'client_id': row['client_id']
                    })
                    
        except Exception as e:
            print(f"⚠️ Error loading conversation history: {e}")
            
        return history
        
    async def register_client(self, websocket):
        """Register a new client connection with unique ID"""
        client_ip = websocket.remote_address[0]
        
        # Create new client with unique ID
        client_id = str(uuid.uuid4())[:8]  # Short UUID
        
        # Check if client from this IP already exists (but don't close it, just log)
        existing_clients = [cid for cid, data in self.clients.items() if data['ip'] == client_ip]
        if existing_clients:
            print(f"⚠️ Multiple connections from {client_ip}. New ID: {client_id}")
        
        self.clients[client_id] = {
            'websocket': websocket,
            'ip': client_ip,
            'connected_at': time.time()
        }
        
        print(f"✅ New client connected: {client_id} from {client_ip}")
        self.log_to_csv('system', f'Client connected from {client_ip}', client_id, client_ip)
        
        # Always load and send conversation history on sync_history request
        return client_id
        
    async def unregister_client(self, websocket):
        """Unregister client connection"""
        # Find client by websocket
        client_to_remove = None
        for client_id, data in self.clients.items():
            if data['websocket'] == websocket:
                client_to_remove = client_id
                break
                
        if client_to_remove:
            client_data = self.clients[client_to_remove]
            client_ip = client_data['ip']
            print(f"❌ Client {client_to_remove} ({client_ip}) disconnected")
            self.log_to_csv('system', f'Client disconnected from {client_ip}', client_to_remove, client_ip)
            del self.clients[client_to_remove]
        
    async def handle_message(self, websocket, message_data):
        """Handle incoming messages from clients"""
        # Find client ID by websocket
        client_id = None
        client_ip = websocket.remote_address[0]
        
        for cid, data in self.clients.items():
            if data['websocket'] == websocket:
                client_id = cid
                break
                
        if not client_id:
            print(f"⚠️ Message from unregistered client {client_ip}")
            return
        
        try:
            message = json.loads(message_data)
            
            # Handle sync_history request
            if message.get('type') == 'sync_history' or message.get('message') == 'sync_history':
                history = self.load_conversation_history(client_ip)
                if history:
                    history_message = {
                        "type": "conversation_history",
                        "history": history,
                        "timestamp": int(time.time() * 1000)
                    }
                    await websocket.send(json.dumps(history_message))
                    print(f"📜 Sent {len(history)} historical messages to {client_id}")
                return
            
            # Handle non-chat messages (offers and schedule systems)
            if message.get('type') in ['get_offers', 'update_offer_status']:
                await self.handle_offers_message(websocket, message, client_id, client_ip)
                return
            elif message.get('type') in ['get_schedule', 'add_event', 'update_event', 'delete_event']:
                await self.handle_schedule_message(websocket, message, client_id, client_ip)
                return
            
            # Create message hash to prevent duplicates for chat messages
            message_hash = f"{client_id}:{message.get('message', '')}:{message.get('timestamp', time.time())}"
            if message_hash in self.processed_messages:
                print(f"🔄 Duplicate message ignored from {client_id}")
                return
            
            self.processed_messages.add(message_hash)
            # Keep only last 1000 message hashes to prevent memory bloat
            if len(self.processed_messages) > 1000:
                self.processed_messages = set(list(self.processed_messages)[-500:])
            
            print(f"📨 Received from {client_id} ({client_ip}): {message}")
            
            # Log incoming message
            user_message = message.get('message', '')
            self.log_to_csv('user', user_message, client_id, client_ip)
            
            # Extract user message
            user_message_lower = user_message.lower().strip()
            
            # Simulate processing delay
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Determine response type based on message content
            if any(keyword in user_message_lower for keyword in ['open', 'visit', 'go to', 'navigate']):
                await self.handle_navigation_request(websocket, user_message_lower, user_message, client_id, client_ip)
            elif any(keyword in user_message_lower for keyword in ['help', 'what can you do', 'commands']):
                await self.send_help_message(websocket, client_id, client_ip)
            elif any(keyword in user_message_lower for keyword in ['freelance', 'work', 'project', 'client']):
                await self.send_freelance_advice(websocket, user_message, client_id, client_ip)
            elif any(keyword in user_message_lower for keyword in ['offer', 'offers', 'job', 'jobs']):
                await self.send_offers_info(websocket, client_id, client_ip)
            else:
                await self.send_echo_response(websocket, user_message, client_id, client_ip)
                
        except json.JSONDecodeError:
            print(f"❌ Error parsing message from {client_id} ({client_ip})")
            error_response = {
                "type": "system_message",
                "message": "Sorry, I couldn't understand that message format.",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(error_response))
            self.log_to_csv('system', error_response['message'], client_id, client_ip)
            
    async def handle_navigation_request(self, websocket, user_message_lower, original_message, client_id, client_ip):
        """Handle requests to open URLs"""
        # Simple URL detection and suggestions
        url_suggestions = {
            'github': 'https://github.com',
            'linkedin': 'https://linkedin.com',
            'upwork': 'https://upwork.com',
            'fiverr': 'https://fiverr.com',
            'freelancer': 'https://freelancer.com',
            'behance': 'https://behance.net',
            'dribbble': 'https://dribbble.com',
            'stackoverflow': 'https://stackoverflow.com',
            'google': 'https://google.com',
            'youtube': 'https://youtube.com',
            'twitter': 'https://twitter.com',
            'facebook': 'https://facebook.com'
        }
        
        found_url = None
        for keyword, url in url_suggestions.items():
            if keyword in user_message_lower:
                found_url = url
                break
                
        if found_url:
            # Send tab opening command
            tab_message = {
                "type": "open_tab",
                "url": found_url,
                "message": f"Opening {found_url} for you!",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(tab_message))
            self.log_to_csv('system', f"Opened {found_url}", client_id, client_ip)
            
            # Follow up with a chat response
            followup_message = {
                "type": "chat_answer",
                "message": f"I've opened {found_url} in a new tab. Is there anything specific you'd like to do there?",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(followup_message))
            self.log_to_csv('bot', followup_message['message'], client_id, client_ip)
        else:
            # Ask for clarification
            clarification_message = {
                "type": "chat_answer",
                "message": "I'd be happy to help you open a website! I can open popular freelance platforms like Upwork, Fiverr, LinkedIn, GitHub, and more. Which site would you like to visit?",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(clarification_message))
            self.log_to_csv('bot', clarification_message['message'], client_id, client_ip)
            
    async def send_help_message(self, websocket, client_id, client_ip):
        """Send help information"""
        help_message = {
            "type": "chat_answer",
            "message": """Here's what I can help you with:

🌐 **Website Navigation**: Say "open LinkedIn", "go to GitHub", "visit Upwork", etc.
💼 **Freelance Support**: Ask about freelance work, projects, or clients
📋 **Offers Management**: Ask about job offers or opportunities
💬 **General Chat**: I'll respond to your messages and questions
🔗 **Quick Links**: I can open popular freelance platforms, social media, and development tools

Try saying: "open GitHub", "help me with freelance work", or "show me job offers"!""",
            "timestamp": int(time.time() * 1000)
        }
        await websocket.send(json.dumps(help_message))
        self.log_to_csv('bot', help_message['message'], client_id, client_ip)
        
    async def send_freelance_advice(self, websocket, original_message, client_id, client_ip):
        """Send freelance-related advice"""
        advice_options = [
            "As a freelancer, building a strong portfolio is crucial. Make sure to showcase your best work and client testimonials!",
            "Time management is key in freelance work. Consider using tools like Toggl or Clockify to track your time effectively.",
            "Don't undervalue your work! Research market rates and price your services competitively but fairly.",
            "Building long-term client relationships is more valuable than one-off projects. Focus on delivering exceptional service!",
            "Always have a clear contract before starting any project. This protects both you and your client.",
            "Diversify your income streams - don't rely on just one client or platform for all your work.",
            "Keep learning new skills to stay competitive. The freelance market is always evolving!"
        ]
        
        advice = random.choice(advice_options)
        response = {
            "type": "chat_answer", 
            "message": f"Great question about freelancing! {advice}",
            "timestamp": int(time.time() * 1000)
        }
        await websocket.send(json.dumps(response))
        self.log_to_csv('bot', response['message'], client_id, client_ip)

    async def send_offers_info(self, websocket, client_id, client_ip):
        """Send information about offers"""
        if self.offer_manager and len(self.offer_manager) > 0:
            offer_count = len(self.offer_manager)
            response_message = f"I have {offer_count} job offers available! These include photography gigs, corporate work, and family sessions. You can view detailed information about each offer through the offers system."
        else:
            response_message = "I don't have any job offers loaded at the moment. The offers system can help you discover and manage freelance opportunities when available."
        
        response = {
            "type": "chat_answer",
            "message": response_message,
            "timestamp": int(time.time() * 1000)
        }
        await websocket.send(json.dumps(response))
        self.log_to_csv('bot', response['message'], client_id, client_ip)
        
    async def send_echo_response(self, websocket, original_message, client_id, client_ip):
        """Send echo response for general messages"""
        response = {
            "type": "bot_response",
            "message": f"Echo: {original_message}",
            "timestamp": int(time.time() * 1000),
            "original_message": original_message
        }
        await websocket.send(json.dumps(response))
        self.log_to_csv('bot', response['message'], client_id, client_ip)
    
    async def handle_offers_message(self, websocket, message, client_id, client_ip):
        """Handle offers-related messages"""
        message_type = message.get('type')
        
        try:
            if message_type == 'get_offers':
                await self.handle_get_offers(websocket, message, client_id, client_ip)
            elif message_type == 'update_offer_status':
                await self.handle_update_offer_status(websocket, message, client_id, client_ip)
            else:
                print(f"⚠️ Unknown offers message type: {message_type}")
                
        except Exception as e:
            print(f"❌ Error handling offers message: {e}")
            error_response = {
                "type": "error",
                "message": f"Error processing offers request: {str(e)}",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(error_response))
    
    async def handle_get_offers(self, websocket, message, client_id, client_ip):
        """Handle get_offers request"""
        print(f"📋 Get offers request from {client_id}")
        
        try:
            if self.offer_manager:
                # Get offers data from the manager
                offers_data = self.offer_manager.list_offers(format_output=False)
                
                # Convert offers to the format expected by the frontend
                formatted_offers = []
                for offer_summary in offers_data:
                    # Get full offer details
                    full_offer = self.offer_manager.get_offer_by_id(offer_summary['offer_id'])
                    
                    if full_offer:
                        # Convert to frontend format
                        formatted_offer = {
                            'offer_id': offer_summary['offer_id'],
                            'job_title': offer_summary['job_title'],
                            'client_name': offer_summary['client_name'],
                            'client_company': full_offer.client_company,
                            'client_contact': full_offer.client_contact,
                            'date_time': offer_summary['date_time'].isoformat(),
                            'location': offer_summary['location'],
                            'status': offer_summary['status'],
                            'description': offer_summary['description'],
                            'source_url': offer_summary.get('source_url'),
                            'created_at': offer_summary['created_at'].isoformat(),
                            'payment_terms': full_offer.payment_terms,
                            'requirements': full_offer.requirements,
                            'duration': full_offer.duration
                        }
                        
                        # Add specific details if available
                        specific_details = full_offer.get_specific_details()
                        if specific_details:
                            formatted_offer['specific_details'] = specific_details
                            
                        formatted_offers.append(formatted_offer)
                
                response = {
                    "type": "offers_data",
                    "offers": formatted_offers,
                    "timestamp": int(time.time() * 1000),
                    "total_count": len(formatted_offers)
                }
                
                print(f"✅ Sending {len(formatted_offers)} offers to {client_id}")
                
            else:
                # Fallback: send sample data if offer manager is not available
                response = {
                    "type": "offers_data",
                    "offers": [],
                    "timestamp": int(time.time() * 1000),
                    "total_count": 0,
                    "message": "Offer management system not available"
                }
                print(f"⚠️ Offer manager not available, sending empty response to {client_id}")
            
            await websocket.send(json.dumps(response))
            self.log_to_csv('system', f"Sent {response.get('total_count', 0)} offers", client_id, client_ip)
            
        except Exception as e:
            print(f"❌ Error getting offers: {e}")
            error_response = {
                "type": "error",
                "message": f"Error retrieving offers: {str(e)}",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(error_response))
    
    async def handle_update_offer_status(self, websocket, message, client_id, client_ip):
        """Handle update_offer_status request"""
        offer_id = message.get('offer_id')
        new_status = message.get('status')
        
        print(f"📝 Update offer status request from {client_id}: {offer_id} -> {new_status}")
        
        try:
            if self.offer_manager and offer_id and new_status:
                success = self.offer_manager.update_status(offer_id, new_status)
                
                if success:
                    response = {
                        "type": "offer_status_updated",
                        "offer_id": offer_id,
                        "status": new_status,
                        "success": True,
                        "timestamp": int(time.time() * 1000)
                    }
                    print(f"✅ Updated offer {offer_id[:8]} status to {new_status}")
                    
                    # Save changes to file
                    try:
                        erwan_path = Path(__file__).parent.parent / "Erwan"
                        offers_file = erwan_path / "offers_backup.pickle"
                        self.offer_manager.save_to_file(str(offers_file), "pickle")
                        print(f"💾 Saved offers to {offers_file}")
                    except Exception as e:
                        print(f"⚠️ Could not save offers to file: {e}")
                        
                else:
                    response = {
                        "type": "offer_status_updated",
                        "offer_id": offer_id,
                        "status": new_status,
                        "success": False,
                        "error": "Offer not found or invalid status",
                        "timestamp": int(time.time() * 1000)
                    }
                    print(f"❌ Failed to update offer {offer_id[:8]} status")
                    
            else:
                response = {
                    "type": "offer_status_updated",
                    "offer_id": offer_id,
                    "status": new_status,
                    "success": False,
                    "error": "Missing offer_id, status, or offer manager not available",
                    "timestamp": int(time.time() * 1000)
                }
                print(f"❌ Invalid update request: offer_id={offer_id}, status={new_status}, manager={self.offer_manager is not None}")
            
            await websocket.send(json.dumps(response))
            self.log_to_csv('system', f"Updated {offer_id} to {new_status}", client_id, client_ip)
            
        except Exception as e:
            print(f"❌ Error updating offer status: {e}")
            error_response = {
                "type": "error",
                "message": f"Error updating offer status: {str(e)}",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(error_response))
    
    async def handle_schedule_message(self, websocket, message, client_id, client_ip):
        """Handle schedule-related messages"""
        message_type = message.get('type')
        
        if message_type == 'get_schedule':
            await self.handle_get_schedule(websocket, message, client_id, client_ip)
        elif message_type == 'add_event':
            await self.handle_add_event(websocket, message, client_id, client_ip)
        elif message_type == 'update_event':
            await self.handle_update_event(websocket, message, client_id, client_ip)
        elif message_type == 'delete_event':
            await self.handle_delete_event(websocket, message, client_id, client_ip)
        else:
            print(f"❌ Unknown schedule message type: {message_type}")
    
    async def handle_get_schedule(self, websocket, message, client_id, client_ip):
        """Handle get_schedule request"""
        print(f"📅 Get schedule request from {client_id}")
        
        try:
            if self.schedule_manager:
                # Format events for the client
                formatted_events = []
                for event in self.schedule_manager.events:
                    formatted_events.append({
                        'id': str(hash(f"{event.title}{event.start_time}")),  # Generate consistent ID
                        'title': event.title,
                        'start_time': event.start_time.isoformat(),
                        'end_time': event.end_time.isoformat(),
                        'description': event.description,
                        'location': event.location,
                        'priority': event.priority
                    })
                
                response = {
                    "type": "schedule_data",
                    "events": formatted_events,
                    "timestamp": int(time.time() * 1000),
                    "total_count": len(formatted_events)
                }
                
                print(f"✅ Sending {len(formatted_events)} events to {client_id}")
                
            else:
                # Fallback: send sample data if schedule manager is not available
                sample_events = [
                    {
                        'id': '1',
                        'title': 'Sample Meeting',
                        'start_time': datetime.now().isoformat(),
                        'end_time': datetime.now().replace(hour=datetime.now().hour + 1).isoformat(),
                        'description': 'Sample event description',
                        'location': 'Sample location',
                        'priority': 3
                    }
                ]
                response = {
                    "type": "schedule_data",
                    "events": sample_events,
                    "timestamp": int(time.time() * 1000),
                    "total_count": len(sample_events),
                    "message": "Schedule management system not available - showing sample data"
                }
                print(f"⚠️ Schedule manager not available, sending sample data to {client_id}")
            
            await websocket.send(json.dumps(response))
            self.log_to_csv('system', f"Sent {response.get('total_count', 0)} events", client_id, client_ip)
            
        except Exception as e:
            print(f"❌ Error getting schedule: {e}")
            error_response = {
                "type": "error",
                "message": f"Error retrieving schedule: {str(e)}",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(error_response))
    
    async def handle_add_event(self, websocket, message, client_id, client_ip):
        """Handle add_event request"""
        print(f"📅 Add event request from {client_id}: {message.get('title', 'No title')}")
        
        try:
            if self.schedule_manager:
                from schedule_agent import Event
                
                # Parse datetime strings
                start_time = datetime.fromisoformat(message['start_time'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(message['end_time'].replace('Z', '+00:00'))
                
                # Create new event
                new_event = Event(
                    title=message['title'],
                    start_time=start_time,
                    end_time=end_time,
                    description=message.get('description', ''),
                    location=message.get('location', ''),
                    priority=message.get('priority', 3)
                )
                
                result = self.schedule_manager.add_event(new_event)
                
                response = {
                    "type": "event_added",
                    "success": result['success'],
                    "message": result['message'],
                    "timestamp": int(time.time() * 1000)
                }
                
                if result['conflicts']:
                    response['conflicts'] = [
                        {
                            'title': conflict.title,
                            'start_time': conflict.start_time.isoformat(),
                            'end_time': conflict.end_time.isoformat()
                        }
                        for conflict in result['conflicts']
                    ]
                
                print(f"✅ Added event '{message['title']}' for {client_id}")
                
            else:
                response = {
                    "type": "event_added",
                    "success": False,
                    "message": "Schedule management system not available",
                    "timestamp": int(time.time() * 1000)
                }
                print(f"⚠️ Schedule manager not available for {client_id}")
            
            await websocket.send(json.dumps(response))
            self.log_to_csv('system', f"Added event: {message.get('title', 'No title')}", client_id, client_ip)
            
        except Exception as e:
            print(f"❌ Error adding event: {e}")
            error_response = {
                "type": "event_added",
                "success": False,
                "message": f"Error adding event: {str(e)}",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(error_response))
    
    async def handle_update_event(self, websocket, message, client_id, client_ip):
        """Handle update_event request"""
        print(f"📅 Update event request from {client_id}: {message.get('title', 'No title')}")
        
        try:
            response = {
                "type": "event_updated",
                "success": True,
                "message": "Event updated successfully (simulated)",
                "timestamp": int(time.time() * 1000)
            }
            
            await websocket.send(json.dumps(response))
            self.log_to_csv('system', f"Updated event: {message.get('title', 'No title')}", client_id, client_ip)
            
        except Exception as e:
            print(f"❌ Error updating event: {e}")
            error_response = {
                "type": "event_updated",
                "success": False,
                "message": f"Error updating event: {str(e)}",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(error_response))
    
    async def handle_delete_event(self, websocket, message, client_id, client_ip):
        """Handle delete_event request"""
        print(f"📅 Delete event request from {client_id}: {message.get('id', 'No ID')}")
        
        try:
            response = {
                "type": "event_deleted",
                "success": True,
                "message": "Event deleted successfully (simulated)",
                "timestamp": int(time.time() * 1000)
            }
            
            await websocket.send(json.dumps(response))
            self.log_to_csv('system', f"Deleted event: {message.get('id', 'No ID')}", client_id, client_ip)
            
        except Exception as e:
            print(f"❌ Error deleting event: {e}")
            error_response = {
                "type": "event_deleted",
                "success": False,
                "message": f"Error deleting event: {str(e)}",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(error_response))
        
    async def handle_client(self, websocket, path):
        """Handle individual client connections"""
        client_id = await self.register_client(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"⚠️ Error handling client: {e}")
        finally:
            await self.unregister_client(websocket)
            
    async def send_shutdown_message(self):
        """Send shutdown message to all connected clients"""
        if self.clients:
            shutdown_message = {
                "type": "system_message",
                "message": "Server is shutting down. Goodbye! 👋",
                "timestamp": int(time.time() * 1000)
            }
            message_str = json.dumps(shutdown_message)
            
            # Send to all connected clients
            disconnected = []
            for client_id, data in self.clients.items():
                try:
                    await data['websocket'].send(message_str)
                    self.log_to_csv('system', shutdown_message['message'], client_id, data['ip'])
                except:
                    disconnected.append(client_id)
            
            # Remove disconnected clients
            for client_id in disconnected:
                del self.clients[client_id]
                
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print('\n🛑 Shutting down server gracefully...')
        self.shutdown = True
        
    async def start_server(self):
        """Start the WebSocket server"""
        print('🚀 Freelaince WebSocket server starting...')
        
        # Set up signal handlers (non-blocking)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        async with websockets.serve(
            self.handle_client, 
            self.host, 
            self.port,
            subprotocols=None,
            ping_interval=30,
            ping_timeout=10
        ):
            print(f'🎯 WebSocket server is running on ws://{self.host}:{self.port}')
            print(f'📡 Ready to accept connections and help with freelance work!')
            print('')
            print('💡 To test the server:')
            print('   1. Load the Freelaince Chrome extension from the "extension" folder')
            print('   2. Click the extension icon in the browser toolbar')
            print('   3. Start chatting in the popup window')
            print('')
            print('🛑 Press Ctrl+C to stop the server')
            print('')
            
            # Keep the server running until shutdown
            try:
                while not self.shutdown:
                    await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                print('\n🛑 Shutting down server gracefully...')
                self.shutdown = True
            
            # Shutdown sequence
            await self.send_shutdown_message()
            print('✅ Server stopped cleanly')

if __name__ == '__main__':
    server = FreelainceServer()
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print('\n✅ Server stopped')
        sys.exit(0)