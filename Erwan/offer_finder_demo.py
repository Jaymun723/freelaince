#!/usr/bin/env python3
"""
Demo script for the OfferFinder class

This script demonstrates how to use the OfferFinder class to search for 
freelance opportunities using AI-powered web search.
"""

import logging
from datetime import datetime
from offer_manager import OfferManager, OfferFinder, LLMInterface
from smolagents import CodeAgent, HfApiModel, InferenceClientModel, LiteLLMModel



class MockLLM:
    """
    Mock LLM implementation for demonstration purposes.
    
    In a real implementation, this would be replaced with an actual LLM client
    like OpenAI GPT, Anthropic Claude, or other LLM services.
    """
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a mock response for demonstration.
        
        In a real implementation, this would call the actual LLM API.
        """
        print(f"\\n[MOCK LLM] Received prompt (first 100 chars): {prompt[:100]}...")
        
        # Return a mock JSON response that matches the expected format
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
                    "client_name": "Jennifer Smith",
                    "client_contact": "jennifer.smith@weddingplanning.com",
                    "client_company": "Elegant Events Planning",
                    "job_description": "Wedding photographer needed for intimate outdoor ceremony. 50 guests, ceremony and reception coverage required. Couple wants natural, candid style photography.",
                    "date_time": "2024-09-15T15:00:00",
                    "duration": "6 hours",
                    "location": "Garden Grove Wedding Venue, Brooklyn NY",
                    "payment_terms": "$1800 - 50% deposit required",
                    "requirements": "Professional wedding photography experience, own equipment, liability insurance",
                    "source_url": "https://brooklyn.craigslist.org/wedding-photographer-needed-sept",
                    "offer_type": "photography",
                    "photography_details": {
                        "event_type": "wedding",
                        "photos_expected": "200",
                        "equipment_requirements": ["full-frame camera", "85mm lens", "flash"],
                        "post_processing_requirements": "Color correction and basic retouching",
                        "delivery_format": "digital_download",
                        "delivery_timeline": "3 weeks after event",
                        "additional_services": ["online gallery"]
                    }
                },
                {
                    "client_name": "TechStart Solutions",
                    "client_contact": "hr@techstart.com",
                    "client_company": "TechStart Solutions",
                    "job_description": "Corporate headshots for new employee onboarding program. Need consistent professional photos for website and marketing materials.",
                    "date_time": "2024-08-20T10:00:00",
                    "duration": "3 hours",
                    "location": "TechStart Office, Manhattan",
                    "payment_terms": "$600 flat rate",
                    "requirements": "Professional headshot experience, studio lighting setup",
                    "source_url": "https://upwork.com/corporate-headshots-nyc-techstart",
                    "offer_type": "photography",
                    "photography_details": {
                        "event_type": "corporate",
                        "photos_expected": "30",
                        "equipment_requirements": ["studio lighting", "backdrop", "85mm lens"],
                        "post_processing_requirements": "Professional retouching, consistent style",
                        "delivery_format": "cloud_storage",
                        "delivery_timeline": "1 week",
                        "additional_services": []
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
                    "client_name": "Maria Rodriguez",
                    "client_contact": "maria.r.events@gmail.com",
                    "client_company": "Rodriguez Family Events",
                    "job_description": "Family reunion photography. Multi-generational family gathering with 40+ people. Need group shots and candid moments throughout the day.",
                    "date_time": "2024-08-25T14:00:00",
                    "duration": "4 hours",
                    "location": "Prospect Park, Brooklyn",
                    "payment_terms": "$900 - payment on completion",
                    "requirements": "Experience with large family groups, outdoor photography",
                    "source_url": "https://nextdoor.com/family-reunion-photographer-brooklyn",
                    "offer_type": "photography",
                    "photography_details": {
                        "event_type": "family",
                        "photos_expected": "150",
                        "equipment_requirements": ["telephoto lens", "wide angle lens"],
                        "post_processing_requirements": "Natural color correction",
                        "delivery_format": "digital_download",
                        "delivery_timeline": "2 weeks",
                        "additional_services": ["group photo prints"]
                    }
                }
            ]
        }
        '''


def demonstrate_offer_finder():
    """Demonstrate the OfferFinder functionality."""
    print("=" * 70)
    print("OFFER FINDER DEMONSTRATION")
    print("=" * 70)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create manager and finder instances
    manager = OfferManager()
    ANTHROPIC_API_KEY = input("Please provide an api key for claude") 

    # Model
    model = LiteLLMModel(
        model_id="claude-3-5-sonnet-20240620",
        api_key=ANTHROPIC_API_KEY,
        verbose=False
    )

    # Agent
    agent = CodeAgent(
        tools=[],
        model=model,
        add_base_tools=True
    )

    finder = OfferFinder(agent)
    
    print("\\n1. Free Search - Photography Jobs in New York")
    print("-" * 50)
    
    # Define search criteria
    search_criteria = {
        'job_type': 'photography',
        'location': 'New York City',
        'additional_filters': {
            'event_types': ['wedding', 'corporate', 'portrait'],
            'min_budget': 500,
            'date_range': 'next 3 months'
        }
    }
    
    print(f"Search criteria: {search_criteria}")
    
    # Perform free search
    found_offers = finder.free_search(search_criteria, [])
    
    print(f"\\nFound {len(found_offers)} offers:")
    for i, offer in enumerate(found_offers, 1):
        print(f"  {i}. {offer}")
        print(f"     Source: {offer.source_url}")
        print(f"     Payment: {offer.payment_terms}")
        print(f"     Event Type: {offer.event_type if hasattr(offer, 'event_type') else 'N/A'}")
    
    # Add found offers to manager
    print("\\n2. Adding Found Offers to Manager")
    print("-" * 50)
    
    for offer in found_offers:
        offer_id = manager.add_offer(offer)
        print(f"   Added offer {offer_id[:8]} - {offer.client_name}")
    
    # Show current offers in manager
    print("\\n3. Current Offers in Manager:")
    print(manager.list_offers())
    
    print("\\n4. Personalized Search - Based on User Profile")
    print("-" * 50)
    # Define user context
    user_context = '''
    User Profile:
    - Experienced wedding and portrait photographer (5+ years)
    - Specializes in outdoor and natural light photography
    - Prefers working with families and couples
    - Located in Brooklyn, willing to travel within NYC
    - Owns professional equipment including multiple lenses
    - Prefers projects with creative freedom
    - Available weekends and evenings
    - Budget preference: $800-2000 per project
    '''
    
    personalized_criteria = {
        'job_type': 'photography',
        'location': 'Brooklyn, NY',
        'preferences': {
            'event_types': ['wedding', 'family', 'portrait'],
            'style': 'natural, outdoor',
            'budget_range': '800-2000'
        }
    }
    
    print(f"User context: {user_context[:100]}...")
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
    
    print(f"\\nFound {len(personalized_offers)} personalized offers:")
    for i, offer in enumerate(personalized_offers, 1):
        print(f"  {i}. {offer}")
        print(f"     Source: {offer.source_url}")
        print(f"     Match reason: AI-selected based on user profile")
    
    # Add personalized offers to manager
    for offer in personalized_offers:
        offer_id = manager.add_offer(offer)
        print(f"   Added personalized offer {offer_id[:8]} - {offer.client_name}")
    
    print("\\n5. Final Offer Summary")
    print("-" * 50)
    print(manager.list_offers())
    
    # Show statistics
    stats = manager.get_stats()
    print(f"\\nTotal offers managed: {stats['total']}")
    print(f"By status: {stats['by_status']}")
    
    print("\\n6. Duplicate Prevention Test")
    print("-" * 50)
    
    # Try to search again with same criteria - should avoid duplicates
    duplicate_test = finder.free_search(search_criteria, current_offers + personalized_offers)
    print(f"Duplicate search returned {len(duplicate_test)} offers (should be fewer due to duplicate prevention)")
    
    print("\\n7. Data Integrity Check")
    print("-" * 50)
    
    # Check that missing data was handled properly
    for offer in found_offers + personalized_offers:
        print(f"\\nOffer: {offer.client_name}")
        print(f"  - Contact: {offer.client_contact or 'NOT_AVAILABLE'}")
        print(f"  - Company: {offer.client_company or 'NOT_AVAILABLE'}")
        print(f"  - Source URL: {offer.source_url}")
        if hasattr(offer, 'photos_expected'):
            print(f"  - Photos expected: {offer.photos_expected}")
        if hasattr(offer, 'equipment_requirements'):
            print(f"  - Equipment: {len(offer.equipment_requirements)} items")
    
    print("\\n" + "=" * 70)
    print("OFFER FINDER DEMO COMPLETED")
    print("=" * 70)
    
    print("\\nNext Steps for Real Implementation:")
    print("1. Replace MockLLM with actual LLM client (OpenAI, Anthropic, etc.)")
    print("2. Add web scraping capabilities for real job sites")
    print("3. Implement caching and rate limiting")
    print("4. Add more sophisticated duplicate detection")
    print("5. Create UI for search criteria input")

if __name__ == "__main__":
    demonstrate_offer_finder()