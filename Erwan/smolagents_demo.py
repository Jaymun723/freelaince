#!/usr/bin/env python3
"""
Demo script for the OfferFinder class using smolagents

This script demonstrates how to use the OfferFinder class with smolagents
for AI-powered freelance opportunity discovery.
"""

import logging
from datetime import datetime
from offer_manager import OfferManager, OfferFinder

# Import smolagents components
try:
    from smolagents import CodeAgent, HfApiModel, LiteLLMModel
    SMOLAGENTS_AVAILABLE = True
except ImportError:
    SMOLAGENTS_AVAILABLE = False
    print("Warning: smolagents not available. Please install with: pip install smolagents")


class SmolagentsLLMAdapter:
    """
    Adapter to make smolagents compatible with the original LLMInterface.
    
    This wrapper allows using smolagents with the existing OfferFinder interface
    while providing a fallback if smolagents is not available.
    """
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """
        Initialize the smolagents adapter.
        
        Args:
            model_name: Name of the HuggingFace model to use
        """
        if not SMOLAGENTS_AVAILABLE:
            raise ImportError("smolagents package not available")
        
        try:
            # Try to create a LiteLLM model first (supports more providers)
            self.model = LiteLLMModel(model_id="gpt-3.5-turbo")
            self.agent = CodeAgent(tools=[], model=self.model)
        except Exception:
            # Fallback to HuggingFace API model
            try:
                self.model = HfApiModel(model_name)
                self.agent = CodeAgent(tools=[], model=self.model)
            except Exception as e:
                print(f"Failed to initialize smolagents model: {e}")
                raise
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using smolagents.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            The model's response as a string
        """
        try:
            response = self.agent.run(prompt)
            
            # Extract the text response from smolagents result
            if hasattr(response, 'content'):
                return response.content
            elif isinstance(response, str):
                return response
            else:
                return str(response)
                
        except Exception as e:
            print(f"Error generating response with smolagents: {e}")
            return ""


class MockSmolagentsLLM:
    """
    Mock implementation when smolagents is not available.
    
    This provides the same interface as SmolagentsLLMAdapter but returns
    mock responses for demonstration purposes.
    """
    
    def generate_response(self, prompt: str) -> str:
        """Generate a mock response for demonstration."""
        print(f"\\n[MOCK SMOLAGENTS] Received prompt (first 100 chars): {prompt[:100]}...")
        
        # Return a mock JSON response
        if "personalized" in prompt.lower():
            return self._get_personalized_mock_response()
        else:
            return self._get_free_search_mock_response()
    
    def _get_free_search_mock_response(self) -> str:
        """Return a mock response for free search."""
        return '''
        {
            "offers": [
                {
                    "client_name": "Sarah Williams",
                    "client_contact": "sarah@creativestudio.com",
                    "client_company": "Creative Studio NYC",
                    "job_description": "Product photography for e-commerce website. Need high-quality photos of jewelry and accessories with white background and lifestyle shots.",
                    "date_time": "2024-09-20T10:00:00",
                    "duration": "5 hours",
                    "location": "Creative Studio, SoHo NYC",
                    "payment_terms": "$1200 flat rate - payment on completion",
                    "requirements": "Professional product photography experience, own lighting equipment, macro lens capability",
                    "source_url": "https://fiverr.com/product-photography-nyc-jewelry",
                    "offer_type": "photography",
                    "photography_details": {
                        "event_type": "product",
                        "photos_expected": "80",
                        "equipment_requirements": ["macro lens", "studio lighting", "white backdrop"],
                        "post_processing_requirements": "Color correction, background removal, retouching",
                        "delivery_format": "digital_download",
                        "delivery_timeline": "5 business days",
                        "additional_services": ["image editing", "file optimization"]
                    }
                },
                {
                    "client_name": "Michael Chen",
                    "client_contact": "mike.chen@techevents.com",
                    "client_company": "TechEvents Conference",
                    "job_description": "Corporate event photography for tech conference. Need speaker headshots, audience shots, networking sessions, and keynote presentations.",
                    "date_time": "2024-08-30T08:00:00",
                    "duration": "8 hours",
                    "location": "Javits Center, NYC",
                    "payment_terms": "$2000 - 50% upfront, 50% after delivery",
                    "requirements": "Event photography experience, professional equipment, ability to work in low light",
                    "source_url": "https://eventbrite.com/tech-conference-photographer-needed",
                    "offer_type": "photography",
                    "photography_details": {
                        "event_type": "corporate",
                        "photos_expected": "300",
                        "equipment_requirements": ["full-frame camera", "24-70mm lens", "70-200mm lens", "flash"],
                        "post_processing_requirements": "Professional editing, color grading",
                        "delivery_format": "cloud_storage",
                        "delivery_timeline": "48 hours",
                        "additional_services": ["same-day highlights", "social media ready images"]
                    }
                }
            ]
        }
        '''
    
    def _get_personalized_mock_response(self) -> str:
        """Return a mock response for personalized search."""
        return '''
        {
            "offers": [
                {
                    "client_name": "Lisa Park",
                    "client_contact": "lisa.park.photography@gmail.com",
                    "client_company": "Park Family",
                    "job_description": "Outdoor maternity photoshoot in Central Park. Golden hour session with natural poses and candid moments. Expecting mother and partner.",
                    "date_time": "2024-09-05T17:30:00",
                    "duration": "2 hours",
                    "location": "Central Park Bethesda Fountain",
                    "payment_terms": "$650 - payment via Venmo after session",
                    "requirements": "Maternity photography experience, natural light expertise",
                    "source_url": "https://instagram.com/direct-message-maternity-photographer",
                    "offer_type": "photography",
                    "photography_details": {
                        "event_type": "maternity",
                        "photos_expected": "40",
                        "equipment_requirements": ["85mm lens", "reflector"],
                        "post_processing_requirements": "Soft, natural editing style",
                        "delivery_format": "digital_download",
                        "delivery_timeline": "2 weeks",
                        "additional_services": ["online gallery", "print release"]
                    }
                }
            ]
        }
        '''


def demonstrate_smolagents_finder():
    """Demonstrate the OfferFinder with smolagents integration."""
    print("=" * 80)
    print("OFFER FINDER WITH SMOLAGENTS DEMONSTRATION")
    print("=" * 80)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create manager
    manager = OfferManager()
    
    print("\\n1. Initializing OfferFinder with smolagents")
    print("-" * 60)
    
    # Try to create smolagents LLM adapter
    if SMOLAGENTS_AVAILABLE:
        print("✓ smolagents package available")
        try:
            # Try to create real smolagents adapter
            smolagents_llm = SmolagentsLLMAdapter()
            print("✓ Successfully created smolagents LLM adapter")
            finder = OfferFinder(smolagents_llm)
        except Exception as e:
            print(f"⚠ Failed to create real smolagents adapter: {e}")
            print("→ Using mock smolagents for demonstration")
            mock_llm = MockSmolagentsLLM()
            finder = OfferFinder(mock_llm)
    else:
        print("⚠ smolagents package not available")
        print("→ Using mock smolagents for demonstration")
        mock_llm = MockSmolagentsLLM()
        finder = OfferFinder(mock_llm)
    
    # Alternative: Let OfferFinder try to create its own smolagents instance
    print("\\n   Alternative: Let OfferFinder auto-initialize smolagents")
    try:
        auto_finder = OfferFinder()  # No parameters - should auto-create smolagents
        print("✓ OfferFinder successfully auto-created smolagents instance")
        finder = auto_finder  # Use the auto-created one if successful
    except Exception as e:
        print(f"⚠ Auto-initialization failed: {e}")
        print("→ Continuing with manually created instance")
    
    print("\\n2. Free Search with smolagents - Photography Jobs in NYC")
    print("-" * 60)
    
    # Define search criteria
    search_criteria = {
        'job_type': 'photography',
        'location': 'New York City',
        'additional_filters': {
            'event_types': ['product', 'corporate', 'events'],
            'min_budget': 800,
            'date_range': 'next 2 months',
            'equipment_available': True
        }
    }
    
    print(f"Search criteria: {search_criteria}")
    
    # Perform free search
    found_offers = finder.free_search(search_criteria, [])
    
    print(f"\\n✓ Found {len(found_offers)} offers using smolagents:")
    for i, offer in enumerate(found_offers, 1):
        print(f"  {i}. {offer}")
        print(f"     📍 Location: {offer.location}")
        print(f"     💰 Payment: {offer.payment_terms}")
        print(f"     🔗 Source: {offer.source_url}")
        if hasattr(offer, 'event_type'):
            print(f"     📸 Type: {offer.event_type}")
    
    # Add found offers to manager
    print("\\n3. Adding smolagents-found offers to manager")
    print("-" * 60)
    
    for offer in found_offers:
        offer_id = manager.add_offer(offer)
        print(f"   ✓ Added offer {offer_id[:8]} - {offer.client_name}")
    
    print("\\n4. Personalized Search with smolagents")
    print("-" * 60)
    
    # Define user context for personalized search
    user_context = '''
    Photographer Profile:
    - Specializes in natural light photography and outdoor settings
    - 3+ years experience in portraits, maternity, and lifestyle photography
    - Based in Manhattan, prefers Brooklyn and Central Park locations
    - Enjoys working with families, couples, and expecting mothers
    - Has professional portrait equipment (85mm, 50mm lenses, reflectors)
    - Prefers creative projects with artistic freedom
    - Available evenings and weekends
    - Target rate: $500-1500 per session
    - Instagram portfolio with 5K+ followers
    '''
    
    personalized_criteria = {
        'job_type': 'photography',
        'location': 'NYC (Manhattan, Brooklyn)',
        'preferences': {
            'specialties': ['portrait', 'maternity', 'lifestyle'],
            'style': 'natural light, outdoor',
            'budget_range': '500-1500',
            'schedule': 'evenings, weekends'
        }
    }
    
    print(f"User profile context: {user_context[:150]}...")
    print(f"Personalized criteria: {personalized_criteria}")
    
    # Get current offers to avoid duplicates
    current_offers = [manager.get_offer_by_id(offer_id) for offer_id in manager._offers.keys()]
    current_offers = [offer for offer in current_offers if offer is not None]
    
    # Perform personalized search
    personalized_offers = finder.personalized_search(
        personalized_criteria, 
        current_offers,
        user_context
    )
    
    print(f"\\n✓ Found {len(personalized_offers)} personalized offers:")
    for i, offer in enumerate(personalized_offers, 1):
        print(f"  {i}. {offer}")
        print(f"     🎯 AI Match: Based on natural light & portrait expertise")
        print(f"     📍 Location: {offer.location}")
        print(f"     💰 Payment: {offer.payment_terms}")
        print(f"     🔗 Source: {offer.source_url}")
    
    # Add personalized offers
    for offer in personalized_offers:
        offer_id = manager.add_offer(offer)
        print(f"   ✓ Added personalized offer {offer_id[:8]} - {offer.client_name}")
    
    print("\\n5. Final Results - All smolagents-discovered offers")
    print("-" * 60)
    print(manager.list_offers())
    
    # Show statistics
    stats = manager.get_stats()
    print(f"\\n📊 Summary Statistics:")
    print(f"   • Total offers managed: {stats['total']}")
    print(f"   • By status: {stats['by_status']}")
    print(f"   • By type: {stats['by_type']}")
    
    print("\\n6. smolagents Integration Benefits")
    print("-" * 60)
    print("✓ Advanced language understanding for job description parsing")
    print("✓ Better context awareness for personalized matching")
    print("✓ Support for multiple model providers (HuggingFace, OpenAI, etc.)")
    print("✓ Built-in tool integration capabilities")
    print("✓ Improved handling of ambiguous or incomplete job postings")
    
    print("\\n7. Data Quality Check")
    print("-" * 60)
    
    all_offers = found_offers + personalized_offers
    for offer in all_offers:
        print(f"\\nOffer: {offer.client_name}")
        print(f"  ✓ Source URL: {offer.source_url or 'Missing - would be flagged'}")
        print(f"  ✓ Contact: {offer.client_contact or 'NOT_AVAILABLE'}")
        print(f"  ✓ Description length: {len(offer.job_description or '')} chars")
        if hasattr(offer, 'photos_expected'):
            print(f"  ✓ Photos expected: {offer.photos_expected}")
        if hasattr(offer, 'equipment_requirements'):
            print(f"  ✓ Equipment items: {len(offer.equipment_requirements)}")
    
    print("\\n" + "=" * 80)
    print("SMOLAGENTS INTEGRATION DEMO COMPLETED")
    print("=" * 80)
    
    print("\\n🚀 Next Steps for Production:")
    print("1. Configure smolagents with your preferred model provider")
    print("2. Add API keys for OpenAI, Anthropic, or other services")
    print("3. Implement web scraping tools for smolagents to use")
    print("4. Add caching and rate limiting for API efficiency")
    print("5. Create custom tools for specific job board parsing")


if __name__ == "__main__":
    demonstrate_smolagents_finder()