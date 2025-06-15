#!/usr/bin/env python3
"""
Demo script for the Freelance Offer Manager System

This script demonstrates the key features of the offer management system:
- Creating photography offers
- Adding them to the manager
- Listing and filtering offers
- Updating offer status
- Retrieving full offer details
"""

from datetime import datetime, timedelta
from offer_manager import OfferManager, PhotographyOffer


def create_sample_offers():
    """Create sample photography offers for demonstration."""
    offers = []
    
    # Sample offer 1: Wedding photography
    wedding_offer = PhotographyOffer(
        client_name="Sarah Johnson",
        client_contact="sarah.johnson@email.com",
        client_company="Johnson Family",
        job_description="Wedding photography for outdoor ceremony and reception. Need full day coverage including getting ready, ceremony, cocktail hour, and reception.",
        date_time=datetime(2024, 8, 15, 14, 0),
        duration="8 hours",
        location="Sunset Gardens, Downtown",
        payment_terms="$2500 - 50% deposit, 50% on delivery",
        requirements="Professional wedding photography experience required",
        event_type="wedding",
        photos_expected=300,
        equipment_requirements=["Full-frame camera", "Backup camera", "85mm lens", "24-70mm lens", "Flash equipment"],
        post_processing_requirements="Color correction, exposure adjustment, basic retouching for all photos. Advanced retouching for 50 selected photos.",
        delivery_format="digital_download",
        delivery_timeline="4 weeks after event",
        additional_services=["Engagement session", "Wedding album design"],
        source_url="https://weddingwire.com/vendor/listing/sarah-johnson"
    )
    offers.append(wedding_offer)
    
    # Sample offer 2: Corporate headshots
    corporate_offer = PhotographyOffer(
        client_name="Mike Chen",
        client_contact="+1-555-0123",
        client_company="TechCorp Solutions",
        job_description="Corporate headshots for company website and LinkedIn profiles. Need consistent lighting and background for professional look.",
        date_time=datetime(2024, 7, 22, 9, 0),
        duration="4 hours",
        location="TechCorp Office, 123 Business Ave",
        payment_terms="$800 - Net 30",
        requirements="Professional headshot experience, studio lighting setup",
        event_type="corporate",
        photos_expected=50,
        equipment_requirements=["Studio lighting", "Gray backdrop", "85mm lens"],
        post_processing_requirements="Professional retouching, consistent color grading",
        delivery_format="cloud_storage",
        delivery_timeline="1 week after shoot",
        additional_services=["Individual photo consultation"],
        source_url="https://linkedin.com/jobs/corporate-photographer-techcorp"
    )
    offers.append(corporate_offer)
    
    # Sample offer 3: Family portrait session
    family_offer = PhotographyOffer(
        client_name="Emily Rodriguez",
        client_contact="emily.r.photos@gmail.com",
        client_company="Rodriguez Family",
        job_description="Annual family portraits in natural outdoor setting. Family of 5 including three young children.",
        date_time=datetime(2024, 9, 10, 16, 0),
        duration="2 hours",
        location="Central Park, North Meadow",
        payment_terms="$400 - Payment due at session",
        requirements="Experience with children's photography",
        event_type="family",
        photos_expected=25,
        equipment_requirements=["70-200mm lens", "Reflector"],
        post_processing_requirements="Natural color correction, skin smoothing",
        delivery_format="digital_download",
        delivery_timeline="2 weeks after session",
        additional_services=["Print ordering service"],
        source_url="https://craigslist.org/family-photographer-needed"
    )
    offers.append(family_offer)
    
    return offers


def demonstrate_offer_management():
    """Demonstrate the offer management system functionality."""
    print("=" * 60)
    print("FREELANCE OFFER MANAGER SYSTEM DEMO")
    print("=" * 60)
    
    # Create offer manager
    manager = OfferManager()
    
    print("\n1. Creating Sample Photography Offers...")
    offers = create_sample_offers()
    offer_ids = []
    
    # Add offers to manager
    for offer in offers:
        offer_id = manager.add_offer(offer)
        offer_ids.append(offer_id)
        print(f"   Added: {offer}")
    
    print(f"\n   Total offers created: {len(offer_ids)}")
    
    # List all offers
    print("\n2. Listing All Offers:")
    print(manager.list_offers())
    
    # Get statistics
    print("\n3. Offer Statistics:")
    stats = manager.get_stats()
    print(f"   Total offers: {stats['total']}")
    print(f"   By status: {stats['by_status']}")
    print(f"   By type: {stats['by_type']}")
    
    # Update offer status
    print("\n4. Updating Offer Status...")
    if offer_ids:
        first_offer_id = offer_ids[0]
        success = manager.update_status(first_offer_id, "accepted")
        if success:
            print(f"   Offer {first_offer_id[:8]} status updated to 'accepted'")
        
        if len(offer_ids) > 1:
            second_offer_id = offer_ids[1]
            manager.update_status(second_offer_id, "completed")
            print(f"   Offer {second_offer_id[:8]} status updated to 'completed'")
    
    # Show updated list
    print("\n5. Updated Offer List:")
    print(manager.list_offers())
    
    # Filter offers
    print("\n6. Filtering Offers...")
    
    # Filter by status
    pending_offers = manager.filter_offers(status="pending")
    print(f"   Pending offers: {len(pending_offers)}")
    for offer in pending_offers:
        print(f"     - {offer['client_name']} ({offer['job_title']})")
    
    # Filter by client name
    johnson_offers = manager.filter_offers(client_name="Johnson")
    print(f"   Offers containing 'Johnson': {len(johnson_offers)}")
    
    # Filter by date range
    future_date = datetime.now() + timedelta(days=30)
    upcoming_offers = manager.filter_offers(date_from=datetime.now(), date_to=future_date)
    print(f"   Offers in next 30 days: {len(upcoming_offers)}")
    
    # Filter by source URL
    craigslist_offers = manager.filter_offers(source_url="craigslist")
    print(f"   Offers from Craigslist: {len(craigslist_offers)}")
    for offer in craigslist_offers:
        print(f"     - {offer['client_name']} from {offer['source_url']}")
    
    # Get full offer details
    print("\n7. Full Offer Details:")
    if offer_ids:
        full_offer = manager.get_offer_by_id(offer_ids[0])
        if full_offer:
            print(f"   Retrieving details for: {full_offer}")
            print(f"   Event type: {full_offer.event_type.title()}")
            print(f"   Photos expected: {full_offer.photos_expected}")
            print(f"   Equipment needed: {full_offer.get_equipment_summary()}")
            print(f"   Additional services: {full_offer.get_services_summary()}")
            print(f"   Estimated shooting time: {full_offer.estimate_shooting_time()}")
            print(f"   Source URL: {full_offer.source_url or 'Not specified'}")
    
    # Demonstrate equipment management
    print("\n8. Managing Equipment Requirements...")
    if offer_ids:
        photo_offer = manager.get_offer_by_id(offer_ids[0])
        if isinstance(photo_offer, PhotographyOffer):
            print(f"   Original equipment: {photo_offer.get_equipment_summary()}")
            photo_offer.add_equipment_requirement("Drone")
            print(f"   After adding drone: {photo_offer.get_equipment_summary()}")
    
    # Save to file demonstration
    print("\n9. Save/Load Functionality...")
    try:
        success = manager.save_to_file("offers_backup.pickle", "pickle")
        if success:
            print("   Offers saved successfully to offers_backup.pickle")
        
        # Create new manager and load
        new_manager = OfferManager()
        success = new_manager.load_from_file("offers_backup.pickle", "pickle")
        if success:
            print(f"   Offers loaded successfully. New manager has {len(new_manager)} offers")
    except Exception as e:
        print(f"   Save/Load error: {e}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_offer_management()