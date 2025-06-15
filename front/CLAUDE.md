# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Freelaince is a Chrome extension that provides an AI-powered chat overlay to help freelancers with their daily workflow. The extension connects to a Python WebSocket server that can provide intelligent responses and perform actions like opening relevant websites in new tabs.

## Architecture

The project consists of two main components:

### Chrome Extension (Frontend)
- **manifest.json**: Extension configuration with permissions for tabs, storage, and activeTab
- **content.js**: `FreelainceOverlay` class that creates and manages the chat overlay UI on all web pages
- **background.js**: `WebSocketManager` service worker that handles WebSocket connections and message routing
- **popup.html/js**: Settings interface for configuring WebSocket server URL
- **styles.css**: Modern, sober UI styling with dark mode support

### Python WebSocket Server (Backend)
- **server.py**: `FreelainceServer` class that handles WebSocket connections and message processing
- Supports multiple message types: `bot_response`, `chat_answer`, `open_tab`, `system_message`
- Intelligent response system that recognizes navigation requests and provides freelance advice

## Communication Flow

1. Content script creates overlay UI and communicates with background script
2. Background script manages WebSocket connection to Python server
3. Server processes messages and can send responses or tab-opening commands
4. Background script handles `open_tab` messages by creating new browser tabs
5. All other messages are forwarded to content script for display

## Development Commands

### Server Setup and Running
```bash
# Install Python dependencies
cd server && pip install -r requirements.txt
# or
npm run install-deps

# Start the WebSocket server
cd server && python3 server.py
# or
npm start

# Alternative with better Ctrl+C handling
npm run start-alt

# Server runs on ws://localhost:8080
```

### Extension Development
1. Load extension in Chrome:
   - Open chrome://extensions/
   - Enable Developer mode
   - Click "Load unpacked" and select this directory

2. Test the extension:
   - Open any webpage
   - Click the Freelaince button (chat bubble icon)
   - Send messages to test WebSocket communication

### Message Types

The server supports these message types:
- `user_message`: Sent from extension to server
- `bot_response`: Simple echo responses
- `chat_answer`: Intelligent responses (freelance advice, help)
- `open_tab`: Commands extension to open URLs in new tabs
- `conversation_history`: Sends previous conversation history on connect
- `system_message`: System notifications

## Key Files to Understand

- **background.js**: Central message router between content script and WebSocket server
- **server/server.py**: Contains all AI logic for processing user messages and generating responses
- **content.js**: UI management and user interaction handling
- **manifest.json**: Extension permissions and configuration (note: requires `tabs` permission for URL opening)
- **.chromeignore**: Excludes Python files and cache when loading extension in Chrome

## Server Features

The Python server can:
- **Conversation History**: Automatically loads and syncs previous conversations from CSV
- **Smart Responses**: Recognizes navigation requests ("open GitHub", "visit LinkedIn")
- **Freelance Advice**: Provides context-specific guidance and tips
- **Tab Management**: Opens URLs in new browser tabs via extension
- **Persistent Logging**: All conversations saved to `conversations.csv`
- **Help System**: Explains available features and commands