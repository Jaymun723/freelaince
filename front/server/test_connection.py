#!/usr/bin/env python3
import asyncio
import websockets
import json
import time

async def test_client():
    """Test client to verify no infinite requests"""
    uri = "ws://localhost:8080"
    
    try:
        print("🔗 Connecting to server...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Send a test message
            test_message = {
                "type": "user_message",
                "message": "hello",
                "timestamp": int(time.time() * 1000)
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Sent test message")
            
            # Wait for response
            response = await websocket.recv()
            print("📨 Received:", response)
            
            # Send another message to test duplicates
            await asyncio.sleep(1)
            await websocket.send(json.dumps(test_message))
            print("📤 Sent duplicate message")
            
            response2 = await websocket.recv()
            print("📨 Received:", response2)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing WebSocket connection...")
    print("Make sure server.py is running first!")
    asyncio.run(test_client())