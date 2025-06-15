# CLAUDE.md - Freelaince Chrome Extension

This file provides guidance to Claude Code (claude.ai/code) when working with the current Freelaince Chrome extension.

## Extension Overview

The **Freelaince Chrome Extension** is a popup-based AI assistant that helps freelancers with their daily workflow. Unlike traditional overlay extensions, this provides a clean popup interface accessible via the browser toolbar.

## Architecture

### Core Components

- **manifest.json**: Extension configuration with permissions for tabs, storage, and WebSocket connections
- **popup.html/js**: Main chat interface that appears when clicking the extension icon
- **background.js**: Service worker handling WebSocket connections and message routing
- **offers.html/js**: Dedicated offers management page with filtering and status updates

### Key Features

1. **Popup Chat Interface**
   - Professional dark theme design
   - Real-time messaging with WebSocket server
   - Connection status indicator
   - Message history persistence
   - Auto-resizing input textarea

2. **Offers Management**
   - Dedicated full-page interface for job opportunities
   - Real-time filtering by status, type, client, location
   - Status updates with server synchronization
   - Statistics dashboard
   - CSP-compliant event handling

3. **WebSocket Integration**
   - Background service worker maintains persistent connection
   - Automatic reconnection with exponential backoff
   - Message routing between popup and server
   - Error handling and status reporting

## Message Flow

```
User Input → Popup → Background Script → WebSocket Server
                                              ↓
Server Response → Background Script → Popup → User Display
```

## Server Communication

### Message Types Sent
- `user_message`: Regular chat messages
- `sync_history`: Request conversation history
- `get_offers`: Request job offers data
- `update_offer_status`: Change offer status

### Message Types Received
- `bot_response`: Simple echo responses
- `chat_answer`: Intelligent AI responses
- `open_tab`: Commands to open URLs in new tabs
- `conversation_history`: Historical messages
- `offers_data`: Job offers information
- `offer_status_updated`: Confirmation of status changes
- `system_message`: System notifications

## Development Setup

### Quick Start
```bash
# Start the WebSocket server
cd server && python3.12 server.py

# Load extension in Chrome
# 1. Open chrome://extensions/
# 2. Enable Developer mode
# 3. Click "Load unpacked" and select the extension/ folder
```

### Testing Checklist
- [ ] Extension loads without errors
- [ ] WebSocket connection established (green indicator)
- [ ] Chat messages send and receive properly
- [ ] Message history loads on reconnect
- [ ] Offers page opens and displays data
- [ ] Offers filtering and search work
- [ ] Status updates sync with server
- [ ] Tab opening functionality works
- [ ] Settings modal allows URL configuration
- [ ] Connection status updates correctly

## File Structure

```
extension/
├── manifest.json           # Extension configuration
├── popup.html             # Main chat interface
├── popup.js               # Chat functionality and WebSocket client
├── background.js          # Service worker and WebSocket manager
├── offers.html            # Offers management page
├── offers.js              # Offers functionality with server sync
└── icon*.png             # Extension icons (16px, 48px, 128px)
```

## Key Implementation Details

### Content Security Policy Compliance
- No inline event handlers (onclick, etc.)
- Event listeners attached via JavaScript
- Data attributes used for button parameters
- No eval() or inline scripts

### WebSocket Management
- Background script maintains single connection
- Automatic reconnection on connection loss
- Message buffering during disconnection
- Connection status propagated to all extension contexts

### Data Storage
- Chrome storage API for settings (WebSocket URL)
- Local storage for cached offers data
- Message history synced from server
- Settings persistence across browser sessions

### Error Handling
- Graceful degradation when server unavailable
- Sample data fallback for offers page
- User-friendly error messages
- Connection retry mechanisms

## Extension Permissions

### Required Permissions
- `activeTab`: Access to current tab for URL opening
- `storage`: Settings and cache persistence
- `tabs`: Create new tabs and manage navigation

### Host Permissions
- `<all_urls>`: Required for opening any website via tab commands

## Development Guidelines

1. **UI Consistency**: Maintain dark theme and professional styling
2. **Performance**: Minimize WebSocket messages and DOM updates
3. **Error Handling**: Always provide user feedback for failures
4. **Security**: Follow CSP guidelines, no inline JavaScript
5. **Accessibility**: Proper ARIA labels and keyboard navigation

## Common Issues and Solutions

### WebSocket Connection Fails
- Verify server is running on correct port (8080)
- Check WebSocket URL in extension settings
- Ensure no firewall blocking localhost connections

### Offers Page Not Loading
- Check web accessible resources in manifest.json
- Verify offers.html and offers.js are included
- Check browser console for CSP violations

### Message History Not Syncing
- Ensure sync_history message is sent on connection
- Check server CSV file permissions
- Verify client IP tracking in server logs

### Extension Popup Not Showing
- Check for JavaScript errors in popup context
- Verify all files are in extension directory
- Ensure manifest.json is valid JSON

## Integration with Server

The extension connects to a central WebSocket server (`server/server.py`) that:
- Processes chat messages and provides AI responses
- Integrates with Erwan offer discovery system
- Manages conversation history in CSV format
- Handles tab opening commands
- Provides freelance-specific advice and navigation

For server-side development, see the main project CLAUDE.md file.