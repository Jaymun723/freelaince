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

class FreelainceServer:
    def __init__(self):
        self.clients = {}  # {client_id: {'websocket': ws, 'ip': ip, 'connected_at': timestamp}}
        self.port = 8080
        self.host = 'localhost'
        self.csv_file = 'conversations.csv'
        self.processed_messages = set()  # Track processed messages to prevent duplicates
        self.shutdown = False  # Shutdown flag
        self.setup_csv_logging()
        
    def setup_csv_logging(self):
        """Initialize CSV file for conversation logging"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['date', 'message_type', 'content', 'client_id', 'client_ip'])
                
    def log_to_csv(self, message_type, content, client_id, client_ip):
        """Log conversation to CSV file"""
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    datetime.now().isoformat(),
                    message_type,
                    content,
                    client_id,
                    client_ip
                ])
        except Exception as e:
            print(f"⚠️ Error logging to CSV: {e}")
    
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
                    row['message_type'] in ['user_message', 'bot_response', 'chat_answer']
                ]
                
                # Get the last N messages
                recent_messages = relevant_messages[-limit:] if len(relevant_messages) > limit else relevant_messages
                
                for row in recent_messages:
                    history.append({
                        'type': row['message_type'],
                        'message': row['content'],
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
        self.log_to_csv('connection', f'Client connected from {client_ip}', client_id, client_ip)
        
        # Send welcome message
        welcome_message = {
            "type": "bot_response",
            "message": f"Hello! I'm Freelaince, your AI Agent (ID: {client_id}). I can chat with you and help you open relevant tabs! 🚀",
            "timestamp": int(time.time() * 1000)
        }
        await websocket.send(json.dumps(welcome_message))
        self.log_to_csv('bot_response', welcome_message['message'], client_id, client_ip)
        
        # Load and send conversation history
        history = self.load_conversation_history(client_ip)
        if history:
            history_message = {
                "type": "conversation_history",
                "history": history,
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(history_message))
            print(f"📜 Sent {len(history)} historical messages to {client_id}")
        
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
            self.log_to_csv('disconnection', f'Client disconnected from {client_ip}', client_to_remove, client_ip)
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
            
            # Create message hash to prevent duplicates
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
            self.log_to_csv('user_message', user_message, client_id, client_ip)
            
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
            self.log_to_csv('system_message', error_response['message'], client_id, client_ip)
            
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
            self.log_to_csv('open_tab', f"Opened {found_url}", client_id, client_ip)
            
            # Follow up with a chat response
            followup_message = {
                "type": "chat_answer",
                "message": f"I've opened {found_url} in a new tab. Is there anything specific you'd like to do there?",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(followup_message))
            self.log_to_csv('chat_answer', followup_message['message'], client_id, client_ip)
        else:
            # Ask for clarification
            clarification_message = {
                "type": "chat_answer",
                "message": "I'd be happy to help you open a website! I can open popular freelance platforms like Upwork, Fiverr, LinkedIn, GitHub, and more. Which site would you like to visit?",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(clarification_message))
            self.log_to_csv('chat_answer', clarification_message['message'], client_id, client_ip)
            
    async def send_help_message(self, websocket, client_id, client_ip):
        """Send help information"""
        help_message = {
            "type": "chat_answer",
            "message": """Here's what I can help you with:

🌐 **Website Navigation**: Say "open LinkedIn", "go to GitHub", "visit Upwork", etc.
💼 **Freelance Support**: Ask about freelance work, projects, or clients
💬 **General Chat**: I'll respond to your messages and questions
🔗 **Quick Links**: I can open popular freelance platforms, social media, and development tools

Try saying: "open GitHub" or "help me with freelance work"!""",
            "timestamp": int(time.time() * 1000)
        }
        await websocket.send(json.dumps(help_message))
        self.log_to_csv('chat_answer', help_message['message'], client_id, client_ip)
        
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
        self.log_to_csv('chat_answer', response['message'], client_id, client_ip)
        
    async def send_echo_response(self, websocket, original_message, client_id, client_ip):
        """Send echo response for general messages"""
        response = {
            "type": "bot_response",
            "message": f"Echo: {original_message}",
            "timestamp": int(time.time() * 1000),
            "original_message": original_message
        }
        await websocket.send(json.dumps(response))
        self.log_to_csv('bot_response', response['message'], client_id, client_ip)
        
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
                    self.log_to_csv('system_message', shutdown_message['message'], client_id, data['ip'])
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
            print('   1. Load the Freelaince Chrome extension')
            print('   2. Open any webpage')
            print('   3. Click the Freelaince button and start messaging')
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