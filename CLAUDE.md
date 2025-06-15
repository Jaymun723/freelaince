# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-component freelance assistance platform with three distinct subsystems:

1. **Erwan/**: Freelance Offer Manager System - Python package for managing freelance job offers with AI-powered discovery capabilities
2. **front/**: Chrome Extension with WebSocket Server - AI-powered chat overlay for freelancers with intelligent tab management
3. **Base_LLM/**: Legacy Claude API Integration - Original anthropic-based conversation system (deprecated in favor of HuggingFace models)

## Development Commands

### Erwan (Offer Management System)
```bash
# Core system demo
cd Erwan && python3 main.py

# AI discovery demos
cd Erwan && python3 offer_finder_demo.py
cd Erwan && python3 smolagents_demo.py

# Module validation
cd Erwan && python3 -c "from offer_manager import OfferManager, StandardOffer, PhotographyOffer, OfferFinder; print('✓ All modules import successfully')"
```

### Front (Chrome Extension + Server)
```bash
# Server setup and run
cd front && npm run install-deps
cd front && npm start
# Alternative: npm run start-alt

# Extension loading: chrome://extensions/ -> Load unpacked -> select front/ directory
```

### Base_LLM (Legacy System)
```bash
# Requires anthropic API key in key.py
cd Base_LLM && python3 init.py
```

## Architecture Overview

### Multi-System Architecture
The repository contains three independent but related systems that can work together or separately:

- **Erwan/** handles job discovery and management with AI-powered search capabilities
- **front/** provides real-time chat assistance via Chrome extension with WebSocket communication
- **Base_LLM/** contains legacy Claude API integration (superseded by HuggingFace implementations)

### Cross-System Integration Points

1. **AI Model Strategy**: Each system uses different AI approaches:
   - Erwan: smolagents protocol with LLM abstraction
   - front: Custom server-side response logic with potential LLM integration
   - Base_LLM: Direct Anthropic Claude API calls

2. **Data Persistence**: 
   - Erwan: Pickle-based offer storage with dual-storage architecture
   - front: CSV-based conversation history
   - Base_LLM: Session-only data retention

3. **Communication Patterns**:
   - Erwan: Direct Python package usage
   - front: WebSocket client-server architecture
   - Base_LLM: Console-based interaction

### Key Architectural Decisions

1. **System Separation**: Each directory is self-contained with its own dependencies and CLAUDE.md documentation

2. **AI Integration Flexibility**: Multiple AI backends supported across systems (smolagents, WebSocket server logic, Anthropic API)

3. **Data Isolation**: Each system manages its own data persistence without cross-system dependencies

## Development Workflow

### Working with Multiple Systems
- Each subdirectory has its own CLAUDE.md with system-specific guidance
- Dependencies are isolated per system (separate requirements.txt files)
- Systems can be developed and deployed independently

### Adding Cross-System Features
- Offer data from Erwan can potentially be integrated into front/ chat responses
- WebSocket server in front/ could leverage Erwan's OfferFinder capabilities
- Base_LLM utilities might be adapted for other systems

## Important Implementation Notes

### System Independence
Each system in this repository is designed to work independently. When making changes:
- Check the specific system's CLAUDE.md for detailed guidance
- Dependencies are scoped to individual systems
- Configuration files are system-specific

### AI Model Evolution
The repository shows an evolution of AI integration approaches:
- Base_LLM: Original Anthropic integration (legacy)
- Erwan: Modern protocol-based LLM abstraction
- front: Custom server logic with potential for LLM enhancement