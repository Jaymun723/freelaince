# CLAUDE.md - Freelaince WebSocket Server

This file provides guidance to Claude Code (claude.ai/code) when working with the Freelaince WebSocket server.

## Server Overview

The **Freelaince WebSocket Server** is the central backend that handles all communication between Chrome extensions and the offer discovery system. It provides chat functionality, offer management, and tab navigation services.

## Architecture

### Core Components

- **FreelainceServer Class**: Main server handling WebSocket connections
- **CSV Logging**: Persistent conversation storage in `conversations.csv`
- **Erwan Integration**: Connection to offer discovery system
- **Message Router**: Handles different message types and responses

### Key Features

1. **Multi-Client Support**
   - Unique client IDs for each connection
   - IP-based conversation history
   - Concurrent connection handling
   - Graceful client disconnection

2. **Chat Processing**
   - AI-powered responses for freelance advice
   - Navigation request handling (open websites)
   - Echo responses for testing
   - Help system with feature explanations

3. **Offer Management**
   - Integration with Erwan offer discovery
   - Real-time offer status updates
   - Persistent storage in pickle format
   - Sample data fallback system

4. **Tab Management**
   - URL opening commands sent to extensions
   - Popular website shortcuts (GitHub, LinkedIn, etc.)
   - Custom URL handling

## Message Types

### Incoming Messages
- `user_message`: Regular chat from users
- `sync_history`: Request for conversation history
- `get_offers`: Request for job offers data
- `update_offer_status`: Change offer status (pending/accepted/declined/completed)

### Outgoing Messages
- `bot_response`: Simple echo responses
- `chat_answer`: Intelligent AI responses with freelance advice
- `open_tab`: Commands extension to open URL in new tab
- `conversation_history`: Historical messages for client IP
- `offers_data`: Job offers information with full details
- `offer_status_updated`: Confirmation of status changes
- `system_message`: System notifications and errors

## Development Setup

### Requirements
```bash
python3.12 -m pip install websockets
```

### Starting the Server
```bash
cd server
python3.12 server.py
```

Server runs on `ws://localhost:8080` by default.

### Environment Setup
- Automatically detects Erwan system in `../Erwan/`
- Loads existing offers from `../Erwan/offers_backup.pickle`
- Creates sample offers if none exist
- Initializes CSV logging file

## Message Processing Flow

```
WebSocket Connection → Client Registration → Message Handler
                                                 ↓
                                    Route by Message Type
                                                 ↓
                              Process & Generate Response
                                                 ↓
                                    Send Response to Client
                                                 ↓
                                      Log to CSV File
```

## Offer System Integration

### Erwan System Connection
```python
# Server automatically imports Erwan classes
from offer_manager import OfferManager, PhotographyOffer, OfferFinder

# Loads existing offers
self.offer_manager.load_from_file("../Erwan/offers_backup.pickle", "pickle")

# Creates sample offers if none exist
self.create_sample_offers()
```

### Offer Data Format
```python
{
    'offer_id': '12345678',
    'job_title': 'Photography',
    'client_name': 'Client Name',
    'client_company': 'Company Name',
    'client_contact': 'contact@email.com',
    'date_time': datetime_object,
    'location': 'Location',
    'status': 'pending',  # pending/accepted/declined/completed
    'description': 'Job description...',
    'payment_terms': '$X for Y hours',
    'requirements': 'Requirements...',
    'duration': 'X hours',
    'specific_details': {
        'event_type': 'wedding',
        'photos_expected': 500,
        'equipment_requirements': [...],
        # ... more details
    }
}
```

## Chat Response System

### Navigation Requests
- **Keywords**: "open", "visit", "go to", "navigate"
- **Supported Sites**: GitHub, LinkedIn, Upwork, Fiverr, etc.
- **Response**: `open_tab` message + follow-up chat

### Freelance Advice
- **Keywords**: "freelance", "work", "project", "client"
- **Responses**: Randomized professional advice
- **Topics**: Portfolio, pricing, time management, contracts

### Help System
- **Keywords**: "help", "what can you do", "commands"
- **Response**: Comprehensive feature list with examples

### Offer Queries
- **Keywords**: "offer", "offers", "job", "jobs"
- **Response**: Information about available opportunities

## Data Storage

### CSV Conversation Log
Format: `date,sender,message,client_id,client_ip,timestamp`
- **Persistent Storage**: All conversations logged
- **IP Tracking**: History tied to client IP addresses
- **Message Types**: user, bot, system
- **Automatic Creation**: File created if doesn't exist

### Offer Persistence
- **Pickle Format**: Binary serialization of offer objects
- **Auto-Save**: Status updates trigger save to file
- **Backup Location**: `../Erwan/offers_backup.pickle`
- **Error Handling**: Graceful fallback if save fails

## Error Handling

### Connection Management
- **Graceful Shutdown**: SIGINT/SIGTERM handlers
- **Client Disconnection**: Automatic cleanup
- **WebSocket Errors**: Logged and handled gracefully
- **Reconnection Support**: No server-side state issues

### Message Processing
- **JSON Parsing**: Try/catch for malformed messages
- **Unknown Types**: Logged warnings for debugging
- **Duplicate Prevention**: Hash-based message deduplication
- **Timeout Handling**: Commands have reasonable timeouts

### Offer System Errors
- **Import Failures**: Graceful fallback to sample data
- **File Access**: Error logging for pickle file issues
- **Status Updates**: Validation and error responses

## Performance Considerations

### Message Deduplication
- **Hash System**: Prevents duplicate message processing
- **Memory Management**: Limited to 1000 recent hashes
- **Client-Based**: Per-client message tracking

### Connection Limits
- **Concurrent Clients**: No artificial limits
- **Memory Usage**: Client data cleaned on disconnect
- **Resource Cleanup**: Proper WebSocket closure

### Response Times
- **Simulated Delay**: 0.5-1.5s for realistic feel
- **Non-Blocking**: Async message processing
- **Quick Responses**: System messages sent immediately

## Configuration

### Server Settings
```python
self.port = 8080
self.host = 'localhost'
self.csv_file = 'conversations.csv'
self.max_reconnect_attempts = 5
```

### Message Limits
- **History Limit**: 50 recent messages per IP
- **Hash Retention**: 1000 recent message hashes
- **WebSocket Settings**: 30s ping interval, 10s timeout

## Development Guidelines

1. **Message Format**: Always use proper JSON with type field
2. **Error Responses**: Include error type and descriptive message
3. **Logging**: Use descriptive console messages with emojis
4. **Client IDs**: Short UUIDs for easy debugging
5. **Async Operations**: All WebSocket operations must be async

## Integration Points

### Extension Integration
- **Background Scripts**: Persistent WebSocket connections
- **Popup Interface**: Real-time chat messaging
- **Offers Page**: Data fetching and status updates
- **Tab Management**: URL opening coordination

### Erwan System Integration
- **Automatic Import**: Detects and loads offer management classes
- **Data Synchronization**: Reads/writes pickle files
- **Sample Generation**: Creates demo offers for testing
- **Status Management**: Updates offer states persistently

## Troubleshooting

### Common Issues

**WebSocket Connection Refused**
- Check if port 8080 is available
- Verify no firewall blocking localhost
- Ensure server started successfully

**Offers Not Loading**
- Check Erwan system availability
- Verify pickle file permissions
- Review server console for import errors

**Message History Empty**
- Check CSV file creation/permissions
- Verify client IP tracking
- Ensure proper message logging

**Status Updates Failing**
- Verify offer ID validity
- Check Erwan system integration
- Review pickle file write permissions

### Debug Information
- **Client Connections**: Logged with IP and unique ID
- **Message Processing**: Full message content logged
- **Error Tracking**: Exceptions caught and logged
- **Offer Operations**: Success/failure status logged

## Security Considerations

- **No Authentication**: Server assumes trusted local network
- **Input Validation**: JSON parsing with error handling
- **File Access**: Limited to designated directories
- **CORS**: Not implemented (WebSocket local only)

For extension-side development, see `extension/CLAUDE.md`.