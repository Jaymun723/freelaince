"""
PhotographyOffer - Specialized offer class for photography jobs with verification support
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from .standard_offer import StandardOffer


class PhotographyOffer(StandardOffer):
    """
    Photography-specific offer class with specialized fields and validation.
    
    Extends StandardOffer with photography-specific attributes like event type,
    equipment requirements, and post-processing specifications.
    """
    
    VALID_EVENT_TYPES = [
        "wedding", "corporate", "portrait", "event", "product", "real_estate",
        "family", "maternity", "newborn", "graduation", "sports", "concert",
        "fashion", "headshots", "other"
    ]
    
    VALID_DELIVERY_FORMATS = [
        "digital_download", "usb_drive", "cloud_storage", "prints", "album", "mixed"
    ]
    
    def __init__(
        self,
        client_name: str,
        client_contact: str,
        client_company: str,
        job_description: str,
        date_time: datetime,
        duration: str,
        location: str,
        payment_terms: str,
        requirements: str,
        event_type: str,
        photos_expected: int,
        equipment_requirements: List[str],
        post_processing_requirements: str,
        delivery_format: str,
        delivery_timeline: str,
        additional_services: Optional[List[str]] = None,
        source_url: Optional[str] = None
    ):
        """
        Initialize a PhotographyOffer.
        
        Args:
            event_type: Type of photography event
            photos_expected: Expected number of final photos
            equipment_requirements: List of required equipment
            post_processing_requirements: Post-processing specifications
            delivery_format: Format for photo delivery
            delivery_timeline: Timeline for photo delivery
            additional_services: Optional additional services
            source_url: URL where this offer was found (optional)
        """
        super().__init__(
            client_name, client_contact, client_company, job_description,
            date_time, duration, location, payment_terms, requirements, source_url
        )
        
        self.event_type = event_type
        self.photos_expected = photos_expected
        self.equipment_requirements = equipment_requirements or []
        self.post_processing_requirements = post_processing_requirements
        self.delivery_format = delivery_format
        self.delivery_timeline = delivery_timeline
        self.additional_services = additional_services or []
    
    def _validate_event_type(self, event_type: str) -> str:
        """Validate event type is from accepted list."""
        if event_type.lower() not in self.VALID_EVENT_TYPES:
            raise ValueError(f"Event type must be one of: {', '.join(self.VALID_EVENT_TYPES)}")
        return event_type.lower()
    
    def _validate_photos_expected(self, count: int) -> int:
        """Validate expected photo count is reasonable."""
        if count < 1:
            raise ValueError("Photos expected must be at least 1")
        if count > 10000:
            raise ValueError("Photos expected seems unreasonably high (>10,000)")
        return count
    
    def _validate_delivery_format(self, format_type: str) -> str:
        """Validate delivery format is from accepted list."""
        if format_type.lower() not in self.VALID_DELIVERY_FORMATS:
            raise ValueError(f"Delivery format must be one of: {', '.join(self.VALID_DELIVERY_FORMATS)}")
        return format_type.lower()
    
    def get_offer_type(self) -> str:
        """Return the offer type."""
        return "Photography"
    
    def get_specific_details(self) -> Dict[str, Any]:
        """Return photography-specific details."""
        return {
            "event_type": self.event_type.title(),
            "photos_expected": self.photos_expected,
            "equipment_requirements": self.equipment_requirements,
            "post_processing_requirements": self.post_processing_requirements,
            "delivery_format": self.delivery_format.replace('_', ' ').title(),
            "delivery_timeline": self.delivery_timeline,
            "additional_services": self.additional_services
        }
    
    def add_equipment_requirement(self, equipment: str) -> None:
        """Add an equipment requirement."""
        if equipment not in self.equipment_requirements:
            self.equipment_requirements.append(equipment)
    
    def remove_equipment_requirement(self, equipment: str) -> None:
        """Remove an equipment requirement."""
        if equipment in self.equipment_requirements:
            self.equipment_requirements.remove(equipment)
    
    def add_additional_service(self, service: str) -> None:
        """Add an additional service."""
        if service not in self.additional_services:
            self.additional_services.append(service)
    
    def remove_additional_service(self, service: str) -> None:
        """Remove an additional service."""
        if service in self.additional_services:
            self.additional_services.remove(service)
    
    def get_equipment_summary(self) -> str:
        """Get a formatted summary of equipment requirements."""
        if not self.equipment_requirements:
            return "No special equipment requirements"
        return ", ".join(self.equipment_requirements)
    
    def get_services_summary(self) -> str:
        """Get a formatted summary of additional services."""
        if not self.additional_services:
            return "No additional services"
        return ", ".join(self.additional_services)
    
    def estimate_shooting_time(self) -> str:
        """Provide rough time estimate based on event type and photo count."""
        base_time = {
            "wedding": 8,
            "corporate": 4,
            "portrait": 2,
            "event": 6,
            "product": 4,
            "real_estate": 3,
            "family": 2,
            "maternity": 2,
            "newborn": 3,
            "graduation": 4,
            "sports": 6,
            "concert": 4,
            "fashion": 6,
            "headshots": 1,
            "other": 4
        }
        
        estimated_hours = base_time.get(self.event_type, 4)
        
        # Adjust based on photo count
        if self.photos_expected > 500:
            estimated_hours += 2
        elif self.photos_expected > 200:
            estimated_hours += 1
        
        return f"Approximately {estimated_hours} hours"
    
    def enhance_with_verification_data(self, enhanced_data: Dict[str, Any]):
        """
        Enhance the photography offer with additional data found during verification.
        
        Args:
            enhanced_data: Dictionary with enhanced field values
        """
        # Call parent method for standard fields
        super().enhance_with_verification_data(enhanced_data)
        
        # Handle photography-specific enhancements
        fields_updated = []
        
        if not self.post_processing_requirements and enhanced_data.get('post_processing_requirements'):
            self.post_processing_requirements = enhanced_data['post_processing_requirements']
            fields_updated.append('post_processing_requirements')
        
        if not self.delivery_timeline and enhanced_data.get('delivery_timeline'):
            self.delivery_timeline = enhanced_data['delivery_timeline']
            fields_updated.append('delivery_timeline')
        
        # Add any photography-specific services found
        additional_services = enhanced_data.get('additional_services', [])
        if additional_services and isinstance(additional_services, list):
            for service in additional_services:
                if service not in self.additional_services:
                    self.additional_services.append(service)
                    fields_updated.append(f'additional_service: {service}')
        
        if fields_updated:
            self.enhanced_by_verification = True
            if self.verification_notes:
                self.verification_notes += f" Photography enhancements: {', '.join(fields_updated)}"
            else:
                self.verification_notes = f"Photography enhancements: {', '.join(fields_updated)}"
    
    def __str__(self) -> str:
        """String representation of the photography offer."""
        verification_indicator = ""
        if self.is_verified():
            verification_indicator = " ✓" if self.is_legitimate() else " ✗"
        return f"Photography Offer ({self.event_type.title()}) - {self.client_name} ({self.date_time.strftime('%Y-%m-%d')}){verification_indicator}"