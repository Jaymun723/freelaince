#!/usr/bin/env python3
"""
Test script for Freelaince server offers integration
"""

import asyncio
import websockets
import json
import time

async def test_offers_integration():
    """Test the offers functionality with the server"""
    uri = "ws://localhost:8080"
    
    try:
        print("🔗 Connecting to server...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to server")
            
            # Wait for welcome message
            welcome_msg = await websocket.recv()
            print(f"📨 Welcome: {json.loads(welcome_msg)}")
            
            # Test 1: Get offers
            print("\n📋 Testing get_offers request...")
            get_offers_msg = {
                "type": "get_offers",
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(get_offers_msg))
            
            response = await websocket.recv()
            offers_data = json.loads(response)
            print(f"✅ Received offers response: {offers_data.get('type')}")
            print(f"📊 Total offers: {offers_data.get('total_count', 0)}")
            
            if offers_data.get('offers'):
                print("🎯 Sample offer:")
                sample_offer = offers_data['offers'][0]
                print(f"   - ID: {sample_offer.get('offer_id', 'N/A')[:8]}...")
                print(f"   - Client: {sample_offer.get('client_name', 'N/A')}")
                print(f"   - Type: {sample_offer.get('job_title', 'N/A')}")
                print(f"   - Status: {sample_offer.get('status', 'N/A')}")
                
                # Test 2: Update offer status
                offer_id = sample_offer.get('offer_id')
                if offer_id:
                    print(f"\n📝 Testing update_offer_status for {offer_id[:8]}...")
                    update_msg = {
                        "type": "update_offer_status",
                        "offer_id": offer_id,
                        "status": "accepted",
                        "timestamp": int(time.time() * 1000)
                    }
                    await websocket.send(json.dumps(update_msg))
                    
                    update_response = await websocket.recv()
                    update_data = json.loads(update_response)
                    print(f"✅ Update response: {update_data}")
                    
                    if update_data.get('success'):
                        print("🎉 Status update successful!")
                    else:
                        print(f"❌ Status update failed: {update_data.get('error')}")
            
            print("\n✨ Test completed successfully!")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ Could not connect to server. Make sure the server is running on ws://localhost:8080")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🧪 Starting Freelaince offers integration test...")
    asyncio.run(test_offers_integration())