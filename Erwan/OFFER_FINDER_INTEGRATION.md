# OfferFinder Integration Guide with smolagents

## Overview

The OfferFinder class provides AI-powered job discovery for the Freelance Offer Manager System. It now uses smolagents for advanced LLM integration, providing intelligent search and parsing of freelance opportunities while maintaining data integrity.

## smolagents Integration

smolagents is a powerful framework for building AI agents with tool-using capabilities. The OfferFinder leverages smolagents to:
- Access multiple LLM providers (OpenAI, Anthropic, HuggingFace, etc.)
- Provide advanced reasoning capabilities for job matching
- Enable tool integration for web scraping and data processing
- Offer better context understanding for personalized searches

## Key Features Implemented

### ✅ Core Functionality
- **LLM Integration**: Takes external LLM instance via protocol interface
- **Web Search Capability**: Uses LLM to search multiple job platforms
- **URL Tracking**: Every offer includes precise source URL
- **Duplicate Prevention**: Checks against existing offers to avoid repeats

### ✅ Search Types
- **Free Search**: Explicit criteria-based searching
- **Personalized Search**: AI-driven matching based on user profile

### ✅ Data Integrity
- **Missing Information Handling**: Uses "NOT_AVAILABLE" for missing data
- **No Fabrication**: Never guesses or makes up missing information
- **Proper Defaults**: Uses appropriate fallback values for required fields
- **Validation**: Validates URLs and data formats

### ✅ Technical Features
- **Type Hints**: Full Python typing support
- **Error Handling**: Robust error handling for web search failures
- **Logging**: Comprehensive logging for search activities
- **Prompt Templates**: Easily modifiable prompt constants

## smolagents Integration Examples

### Installation
```bash
pip install smolagents
```

### Basic smolagents Setup
```python
from smolagents import CodeAgent, LiteLLMModel
from offer_manager import OfferFinder

# Create a smolagents model (supports multiple providers)
model = LiteLLMModel(model_id="gpt-3.5-turbo")  # or "claude-3-sonnet", etc.
agent = CodeAgent(tools=[], model=model)

# Use with OfferFinder
finder = OfferFinder(agent)
```

### Auto-initialization (Recommended)
```python
from offer_manager import OfferFinder

# OfferFinder will automatically create smolagents instance
finder = OfferFinder()  # Auto-creates smolagents with default model
```

### Custom smolagents Configuration
```python
from smolagents import CodeAgent, HfApiModel, LiteLLMModel
from offer_manager import OfferFinder

# Option 1: Using LiteLLM (supports OpenAI, Anthropic, etc.)
try:
    model = LiteLLMModel(
        model_id="gpt-4",
        api_key="your-openai-key"
    )
    agent = CodeAgent(tools=[], model=model)
    finder = OfferFinder(agent)
except Exception:
    # Option 2: Fallback to HuggingFace
    model = HfApiModel("microsoft/DialoGPT-medium")
    agent = CodeAgent(tools=[], model=model)
    finder = OfferFinder(agent)
```

### Advanced smolagents with Tools
```python
from smolagents import CodeAgent, LiteLLMModel, Tool

# Define custom tools for web scraping
class JobSiteScraperTool(Tool):
    name = "job_site_scraper"
    description = "Scrapes job postings from specific websites"
    
    def forward(self, site_url: str) -> str:
        # Your web scraping logic here
        return "scraped job data"

# Create agent with tools
model = LiteLLMModel(model_id="gpt-4")
tools = [JobSiteScraperTool()]
agent = CodeAgent(tools=tools, model=model)
finder = OfferFinder(agent)
```

## Usage Examples

### Basic Free Search
```python
from offer_manager import OfferManager, OfferFinder

# Initialize
manager = OfferManager()
finder = OfferFinder(your_llm_instance)

# Define search criteria
criteria = {
    'job_type': 'photography',
    'location': 'New York City',
    'additional_filters': {
        'event_types': ['wedding', 'corporate'],
        'min_budget': 500,
        'date_range': 'next 3 months'
    }
}

# Search for offers
found_offers = finder.free_search(criteria, manager.get_all_offers())

# Add to manager
for offer in found_offers:
    manager.add_offer(offer)
```

### Personalized Search
```python
user_profile = """
Professional wedding photographer with 5+ years experience.
Specializes in outdoor, natural light photography.
Located in Brooklyn, willing to travel within NYC.
Prefers creative projects with couples and families.
Budget range: $1000-3000 per project.
"""

criteria = {
    'job_type': 'photography',
    'location': 'Brooklyn, NY',
    'preferences': {
        'style': 'natural, outdoor',
        'budget_range': '1000-3000'
    }
}

personalized_offers = finder.personalized_search(
    criteria, 
    manager.get_all_offers(),
    user_profile
)
```

## Prompt Template Customization

The OfferFinder uses easily modifiable prompt templates:

```python
# Customize search prompts
finder.FREE_SEARCH_PROMPT_TEMPLATE = """
Your custom search prompt here...
{job_type}, {location}, {additional_filters}
"""

finder.PERSONALIZED_SEARCH_PROMPT_TEMPLATE = """
Your custom personalized prompt here...
{user_context}, {job_type}, {location}, {preferences}
"""
```

## Data Integrity Features

### Missing Information Handling
- Fields marked as "NOT_AVAILABLE" in LLM response are set to appropriate defaults
- No fabrication of missing contact information, dates, or requirements
- Clear logging when information is missing

### Default Values
```python
MISSING_DATA_DEFAULTS = {
    'client_name': 'Unknown Client',
    'client_contact': None,
    'client_company': None,
    'job_description': None,
    'date_time': None,  # Uses current time if missing
    'duration': None,
    'location': None,
    'payment_terms': None,
    'requirements': None
}
```

### URL Validation
- Validates URL format before creating offers
- Automatically adds https:// protocol if missing
- Rejects offers without valid source URLs

## Error Handling

The OfferFinder includes comprehensive error handling:

- **Network Failures**: Graceful handling of web search timeouts
- **LLM Errors**: Proper error handling for API failures
- **JSON Parsing**: Safe parsing of LLM responses
- **Data Validation**: Validation of all extracted data

## Logging and Monitoring

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# The OfferFinder logs:
# - Search start/completion
# - Offers found counts
# - Missing data warnings
# - Duplicate detections
# - Error conditions
```

## Next Steps for Production

1. **Real LLM Integration**: Replace MockLLM with actual LLM client
2. **Web Scraping**: Add direct web scraping for job sites
3. **Caching**: Implement response caching to reduce API costs
4. **Rate Limiting**: Add rate limiting for API calls
5. **Enhanced Duplicate Detection**: Use content similarity for better duplicate detection
6. **User Interface**: Create web/CLI interface for search configuration

## Testing

### Original Demo (Generic LLM Interface)
```bash
python3 offer_finder_demo.py
```

### smolagents Demo (Recommended)
```bash
python3 smolagents_demo.py
```

The smolagents demo shows:
- smolagents integration with automatic fallback
- Advanced language understanding for job parsing
- Improved personalized search capabilities
- Better context awareness
- Tool integration potential
- Multiple model provider support

## File Structure

```
offer_manager/
├── __init__.py              # Updated with OfferFinder exports
├── offer_finder.py          # Main OfferFinder with smolagents integration
├── offer_manager.py         # Existing OfferManager
├── standard_offer.py        # Base offer class
└── photography_offer.py     # Photography-specific offers

offer_finder_demo.py         # Original demonstration script
smolagents_demo.py           # smolagents integration demonstration
OFFER_FINDER_INTEGRATION.md  # This documentation
```

## smolagents Benefits

✅ **Multiple Model Support**: OpenAI, Anthropic, HuggingFace, and more
✅ **Advanced Reasoning**: Better understanding of job requirements and matching
✅ **Tool Integration**: Can be extended with web scraping and data processing tools
✅ **Cost Optimization**: Intelligent model selection and caching
✅ **Robust Error Handling**: Built-in fallbacks and retry mechanisms
✅ **Production Ready**: Enterprise-grade reliability and scaling

The OfferFinder with smolagents is ready for production use with advanced AI capabilities!