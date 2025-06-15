#!/usr/bin/env python3
"""
Test script to verify conversation history functionality
"""
import asyncio
import websockets
import json
import time

async def test_history():
    """Test the conversation history feature"""
    uri = "ws://localhost:8080"
    
    print("🧪 Testing conversation history feature...")
    print("Make sure server.py is running and has some conversation history!")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to server")
            
            # Wait for welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print("📨 Welcome:", welcome_data['message'])
            
            # Check if we receive history
            try:
                history_msg = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                history_data = json.loads(history_msg)
                
                if history_data.get('type') == 'conversation_history':
                    history = history_data.get('history', [])
                    print(f"📜 Received {len(history)} historical messages:")
                    
                    for i, msg in enumerate(history[-5:], 1):  # Show last 5
                        msg_type = "🗣️" if msg['type'] == 'user_message' else "🤖"
                        timestamp = msg['timestamp'][:19]  # Remove microseconds
                        print(f"  {i}. {msg_type} [{timestamp}] {msg['message']}")
                        
                    if len(history) > 5:
                        print(f"  ... and {len(history) - 5} more messages")
                else:
                    print("⚠️ Expected conversation_history but got:", history_data.get('type'))
                    
            except asyncio.TimeoutError:
                print("ℹ️ No conversation history received (this is normal for new users)")
            
            # Send a test message to add to history
            test_message = {
                "type": "user_message", 
                "message": "test message for history",
                "timestamp": int(time.time() * 1000)
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Sent test message")
            
            # Wait for response
            response = await websocket.recv()
            response_data = json.loads(response)
            print("📨 Response:", response_data['message'])
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_history())