# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Freelance Offer Manager System - a Python package for managing freelance job offers with AI-powered discovery capabilities. The system consists of three main components that work together:

1. **Offer Management Layer**: Core data models and management functionality
2. **AI Discovery Layer**: LLM-powered job opportunity finder with web search capabilities  
3. **Demo Applications**: Example usage and testing scripts

## Development Commands

### Running Demonstrations
```bash
# Core system demo (basic offer management)
python3 main.py

# Original OfferFinder demo (with mock LLM)
python3 offer_finder_demo.py

# smolagents integration demo (requires smolagents package)
python3 smolagents_demo.py
```

### Testing Module Imports
```bash
# Verify all modules can be imported
python3 -c "from offer_manager import OfferManager, StandardOffer, PhotographyOffer, OfferFinder; print('✓ All modules import successfully')"

# Check syntax of all Python files
find . -name "*.py" -exec python3 -m py_compile {} \;
```

### Package Usage
```python
# Basic usage pattern
from offer_manager import OfferManager, PhotographyOffer, OfferFinder

# Create and manage offers
manager = OfferManager()
offer = PhotographyOffer(...)  # with all required fields
offer_id = manager.add_offer(offer)

# AI-powered offer discovery
finder = OfferFinder()  # Auto-creates smolagents instance if available
found_offers = finder.free_search(criteria, known_offers)
```

## Architecture Overview

### Core Design Pattern
The system uses a **dual-storage architecture** in OfferManager:
- `_offers`: Lightweight essential info for quick browsing (dict of summaries)
- `_full_offers`: Complete StandardOffer objects for detailed access
- This separation enables fast listing while preserving full data access

### Inheritance Hierarchy
```
StandardOffer (ABC)
├── PhotographyOffer (concrete implementation)
└── [Future offer types extend here]
```

StandardOffer defines the common interface with abstract methods `get_offer_type()` and `get_specific_details()` that concrete implementations must provide.

### AI Integration Layer
OfferFinder uses a **flexible LLM interface** approach:
- Protocol-based interface allows any LLM implementation
- smolagents integration with automatic fallback
- Dual prompt templates: `FREE_SEARCH_PROMPT_TEMPLATE` and `PERSONALIZED_SEARCH_PROMPT_TEMPLATE`
- Built-in data integrity with explicit "NOT_AVAILABLE" handling

### Data Integrity Principles
The system enforces strict data integrity rules:
- **No fabrication**: Missing data is explicitly marked as "NOT_AVAILABLE" or None
- **URL tracking**: Every found offer must include precise source URL
- **Duplicate prevention**: URL-based deduplication against known offers
- **Validation**: Contact info, URLs, and data formats are validated on input

### Key Architectural Decisions

1. **Abstract Base Classes**: StandardOffer is abstract to enforce consistent interface across offer types while allowing specialization

2. **Essential vs Full Data**: OfferManager stores both lightweight summaries and complete objects to optimize for different access patterns

3. **LLM Abstraction**: OfferFinder works with any LLM through protocol interface, with smolagents as preferred implementation

4. **Missing Data Handling**: System explicitly handles incomplete information rather than guessing, maintaining data credibility

## Key Integration Points

### Adding New Offer Types
1. Extend StandardOffer abstract base class
2. Implement required abstract methods: `get_offer_type()`, `get_specific_details()`
3. Add to `__init__.py` exports
4. Update OfferFinder prompt templates if needed

### LLM Integration
- OfferFinder auto-detects smolagents availability
- Falls back to standard LLMInterface protocol if smolagents unavailable
- Prompt templates are easily modifiable class constants
- Response parsing expects JSON format with specific schema

### Data Validation
- Client contact validation (email/phone patterns)
- URL validation with auto-protocol correction
- Date/time parsing with fallbacks
- Equipment and service list normalization

## Important Implementation Notes

### Source URL Tracking
Every offer MUST have a source URL. OfferFinder rejects offers without valid URLs as this is critical for lead source tracking and duplicate prevention.

### Status Management
OfferManager enforces valid status transitions: `["pending", "accepted", "declined", "completed"]`

### Search Deduplication
OfferFinder compares source URLs against known offers to prevent duplicates. This happens at the URL level before offer creation.

### Prompt Template Modification
Both search prompt templates are class constants that can be easily modified for different domains or languages. They include specific instructions for handling missing data.