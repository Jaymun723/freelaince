# Freelaince Server

WebSocket server for the Freelaince Chrome extension.

## Setup

Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
# Method 1: Direct execution
python3 server.py

# Method 2: Alternative runner (better Ctrl+C handling)
python3 run_server.py

# Method 3: Using npm scripts (from parent directory)
npm run start
npm run start-alt
```

## Server Features

- **Smart Responses**: Recognizes navigation requests, freelance advice, help commands
- **Tab Opening**: Can open URLs in new browser tabs via extension
- **Single Connection**: Prevents duplicate connections per IP
- **CSV Logging**: Logs all conversations to `conversations.csv`
- **Message Deduplication**: Prevents processing duplicate messages

## Server URL

Default: `ws://localhost:8080`

Configure in Chrome extension popup if using different host/port.

## Message Types

- `user_message`: Messages from extension users
- `bot_response`: Simple echo responses  
- `chat_answer`: Intelligent responses (advice, help)
- `open_tab`: Commands to open URLs in browser
- `system_message`: System notifications

## Testing

Use the test client:
```bash
python3 test_connection.py
```