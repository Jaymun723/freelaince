# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Freelaince** is an AI-powered platform that helps freelancers in their journey by combining multiple intelligent systems:

1. **Browser Extension** (`extension/`): Chrome extension with popup-based chat interface for real-time assistance
2. **WebSocket Server** (`server/`): Central Python server handling chat, offers, and tab management
3. **Offer Discovery System** (`Erwan/`): AI-powered job opportunity finder with web search capabilities
4. **Legacy Extension** (`front/`): Original overlay-based extension (deprecated)
5. **LLM Orchestration** (`Base_LLM/`): Central intelligence layer coordinating all features (planned)

The platform provides a comprehensive solution for freelancers to manage their workflow, discover opportunities, and get intelligent assistance through a seamless browser-based interface.

## Architecture Overview

### Current Extension (`extension/`)
- **Chrome Extension**: Popup-based chat interface (appears in browser action)
- **WebSocket Communication**: Real-time connection to central server
- **Offers Management**: Dedicated page for viewing and managing job opportunities
- **Tab Management**: Can open relevant websites and resources
- **Persistent Storage**: Conversation history and settings
- **Modern UI**: Dark mode support with professional styling

**Key Components:**
- `manifest.json`: Extension configuration and permissions
- `background.js`: WebSocket manager and message routing
- `popup.html/js`: Main chat interface (popup window)
- `offers.html/js`: Offers management page with filtering and status updates

### Legacy Extension (`front/`) - Deprecated
- **Original implementation**: Chat overlay on webpages
- **Still functional**: Can be used but not actively maintained
- **Content Script**: Injected overlay UI (`content.js`)
- **Server included**: Local Python WebSocket server (`front/server/`)

### Central Server (`server/`)
- **WebSocket Server**: Handles all extension connections
- **Chat Processing**: AI responses, navigation requests, freelance advice
- **Offer Integration**: Connects to Erwan system for job opportunities
- **Message Storage**: CSV-based conversation logging
- **Tab Management**: Commands extension to open URLs

### Backend - Offer Discovery (`Erwan/`)
- **Offer Management**: Core data models for different offer types
- **AI Discovery**: LLM-powered job opportunity finder
- **Web Search Integration**: Automated offer discovery from various sources
- **Data Integrity**: Strict validation and duplicate prevention
- **Extensible Architecture**: Support for multiple freelance domains

**Key Components:**
- `offer_manager/`: Core package with data models and management
- `offer_finder.py`: AI-powered opportunity discovery
- `photography_offer.py`: Specialized offer type implementation
- Integration with smolagents for enhanced AI capabilities

### LLM Orchestration (`Base_LLM/`)
*[Planned]* Central intelligence layer that will coordinate:
- Chat responses and user assistance
- Offer discovery triggers and personalization
- Cross-system communication and state management
- Advanced AI features and workflow automation

## Development Setup

### Quick Start
```bash
# Install all dependencies
npm install  # Frontend dependencies
cd Erwan && python3 -m pip install -r requirements.txt  # If requirements.txt exists

# Start the central WebSocket server
cd server && python3.12 server.py
# Server runs on ws://localhost:8080

# Test offer discovery system
cd Erwan && python3 main.py
```

### Browser Extension Development
1. Load extension in Chrome:
   - Open `chrome://extensions/`
   - Enable Developer mode
   - Click "Load unpacked" and select the `extension/` directory

2. Start the server:
   - Run `cd server && python3.12 server.py`
   - Server will start on `ws://localhost:8080`

3. Use the extension:
   - Click extension icon in browser toolbar
   - Chat appears as popup window
   - Click 📋 icon to view offers page
   - Configure server URL via ⚙️ settings if needed

### Offer Discovery Testing
```bash
cd Erwan

# Core system demo
python3 main.py

# AI discovery demo
python3 offer_finder_demo.py

# Advanced AI integration (requires smolagents)
python3 smolagents_demo.py
```

## Integration Points

### Extension ⟷ Offer Discovery
The browser extension can trigger offer discovery and display results through:
- WebSocket message types for offer requests
- Tab opening for found opportunities
- Chat interface for offer management commands

### Future LLM Orchestration
The planned `Base_LLM` system will:
- Process all chat interactions from the extension
- Trigger appropriate offer discovery based on user context
- Provide personalized recommendations and workflow assistance
- Coordinate between all system components

## Key Features

### Current Extension
- **Popup-based chat**: Professional interface in browser action
- **Offers management**: Dedicated page with filtering, search, and status updates
- **Real-time WebSocket**: Connection to central server with live status indicator
- **Smart tab management**: Navigation and website opening capabilities
- **Conversation history**: Persistent storage and sync across sessions
- **Freelance-specific guidance**: Advice, tips, and platform recommendations
- **Modern dark UI**: Professional styling with responsive design
- **CSP compliant**: No inline JavaScript, proper event handling

### Offer Discovery
- AI-powered job opportunity finder
- Multiple offer type support (Photography, etc.)
- Automatic web search and data extraction
- Duplicate prevention and data validation
- Extensible architecture for new domains

### Data Management
- Dual-storage architecture for performance
- Strict data integrity rules
- URL-based deduplication
- Persistent conversation and offer history

## Message Flow

```
User ←→ Extension Popup ←→ Background Script ←→ Central WebSocket Server
                                                            ↓
                                            [Future] Base_LLM Orchestrator
                                                            ↓
                                                   Offer Discovery System (Erwan)
```

## File Structure

```
freelaince/
├── CLAUDE.md                 # This file - global project guidance
├── README.md                 # Project documentation
├── extension/                # Current Chrome extension
│   ├── manifest.json        # Chrome extension config
│   ├── background.js        # WebSocket manager and message routing
│   ├── popup.html/js        # Main chat interface (popup)
│   ├── offers.html/js       # Offers management page
│   └── icon*.png           # Extension icons
├── server/                   # Central WebSocket server
│   ├── server.py            # Main server with chat, offers, tab management
│   └── conversations.csv    # Message storage
├── front/                    # Legacy browser extension (deprecated)
│   ├── CLAUDE.md            # Legacy extension guidance
│   ├── manifest.json        # Legacy extension config
│   ├── content.js           # Chat overlay UI (deprecated)
│   ├── background.js        # Legacy WebSocket manager
│   ├── server/              # Legacy Python WebSocket server
│   └── ...
├── Erwan/                    # Offer discovery system
│   ├── CLAUDE.md            # Offer system guidance
│   ├── offer_manager/       # Core package
│   ├── main.py              # Demo applications
│   └── ...
└── Base_LLM/                 # [Planned] LLM orchestration
    └── CLAUDE.md            # Will contain orchestration guidance
```

## Development Guidelines

1. **Follow existing patterns**: Each component has established conventions
2. **Data integrity first**: Never fabricate data, use explicit "NOT_AVAILABLE" markers
3. **Extensible design**: Support for new offer types and features
4. **Real-time communication**: Maintain responsive WebSocket connections
5. **User experience focus**: Keep the interface fast and intuitive

## Testing

### Extension Testing
- Load unpacked extension from `extension/` folder in Chrome
- Start server with `cd server && python3.12 server.py`
- Test WebSocket connectivity (connection status indicator)
- Verify popup chat functionality and message history
- Test offers page: filtering, status updates, server sync
- Check tab opening capabilities
- Verify conversation persistence and settings storage

### Offer Discovery Testing
- Run demo scripts to verify functionality
- Test AI integration with various LLM backends
- Validate data extraction and deduplication
- Check offer type extensibility

For detailed component-specific guidance, refer to the CLAUDE.md files in each respective folder.