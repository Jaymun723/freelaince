"""
StandardOffer - Base class for all freelance job offers with verification support
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
import re
import json


class StandardOffer(ABC):
    """
    Abstract base class for freelance job offers with verification capabilities.
    
    This class defines the common structure and behavior for all types of
    freelance offers while allowing for specific implementations.
    """
    
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
        source_url: Optional[str] = None
    ):
        """
        Initialize a StandardOffer.
        
        Args:
            client_name: Name of the client
            client_contact: Contact information (email or phone)
            client_company: Client's company name
            job_description: Description of the job
            date_time: Date and time of the job
            duration: Expected duration of the job
            location: Job location or venue
            payment_terms: Payment terms and amount
            requirements: Job requirements and specifications
            source_url: URL where this offer was found (optional)
        """
        self.client_name = self._validate_name(client_name)
        self.client_contact = client_contact
        self.client_company = client_company
        self.job_description = job_description
        self.date_time = date_time
        self.duration = duration
        self.location = location
        self.payment_terms = payment_terms
        self.requirements = requirements
        self.source_url = self._validate_url(source_url) if source_url else None
        self.created_at = datetime.now()
        
        # Verification fields
        self.is_legitimate_job_offer: Optional[bool] = None
        self.verification_confidence: Optional[float] = None
        self.verification_notes: Optional[str] = None
        self.verified_at: Optional[datetime] = None
        self.original_missing_fields: Optional[Dict[str, bool]] = None
        self.enhanced_by_verification: bool = False
    
    def _validate_name(self, name: str) -> str:
        """Validate client name is not empty."""
        if not name or not name.strip():
            raise ValueError("Client name cannot be empty")
        return name.strip()
    
    def _validate_contact(self, contact: str) -> str:
        """Validate contact information format."""
        if not contact or not contact.strip():
            raise ValueError("Client contact cannot be empty")
        
        contact = contact.strip()
        
        # Check if it's an email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, contact):
            return contact
        
        # Check if it's a phone number (basic validation)
        phone_pattern = r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$'
        if re.match(phone_pattern, contact):
            return contact
        
        raise ValueError("Contact must be a valid email or phone number")
    
    def _validate_url(self, url: str) -> str:
        """Validate URL format."""
        if not url or not url.strip():
            return url
        
        url = url.strip()
        
        # Basic URL validation
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if re.match(url_pattern, url, re.IGNORECASE):
            return url
        
        # If it doesn't start with http/https, assume it's missing protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            if re.match(url_pattern, url, re.IGNORECASE):
                return url
        
        raise ValueError("Source URL must be a valid URL")
    
    def set_verification_result(
        self, 
        is_legitimate: bool, 
        confidence: float, 
        notes: str = None,
        missing_fields: Dict[str, bool] = None
    ):
        """
        Set verification results for this offer.
        
        Args:
            is_legitimate: Whether this is a legitimate job offer from an employer
            confidence: Confidence score (0.0 to 1.0)
            notes: Additional verification notes
            missing_fields: Dict indicating which fields were originally missing
        """
        self.is_legitimate_job_offer = is_legitimate
        self.verification_confidence = max(0.0, min(1.0, confidence))  # Clamp to [0,1]
        self.verification_notes = notes
        self.verified_at = datetime.now()
        self.original_missing_fields = missing_fields or {}
    
    def enhance_with_verification_data(self, enhanced_data: Dict[str, Any]):
        """
        Enhance the offer with additional data found during verification.
        
        Args:
            enhanced_data: Dictionary with enhanced field values
        """
        fields_updated = []
        
        # Only update fields that were originally missing or incomplete
        if not self.client_contact and enhanced_data.get('client_contact'):
            self.client_contact = enhanced_data['client_contact']
            fields_updated.append('client_contact')
        
        if not self.client_company and enhanced_data.get('client_company'):
            self.client_company = enhanced_data['client_company']
            fields_updated.append('client_company')
        
        if not self.payment_terms and enhanced_data.get('payment_terms'):
            self.payment_terms = enhanced_data['payment_terms']
            fields_updated.append('payment_terms')
        
        if not self.requirements and enhanced_data.get('requirements'):
            self.requirements = enhanced_data['requirements']
            fields_updated.append('requirements')
        
        if not self.duration and enhanced_data.get('duration'):
            self.duration = enhanced_data['duration']
            fields_updated.append('duration')
        
        if fields_updated:
            self.enhanced_by_verification = True
            if self.verification_notes:
                self.verification_notes += f" Enhanced fields: {', '.join(fields_updated)}"
            else:
                self.verification_notes = f"Enhanced fields: {', '.join(fields_updated)}"
    
    def is_verified(self) -> bool:
        """Check if this offer has been verified."""
        return self.is_legitimate_job_offer is not None
    
    def is_legitimate(self) -> bool:
        """Check if this offer is verified as legitimate."""
        return self.is_legitimate_job_offer is True
    
    def get_verification_status(self) -> str:
        """Get human-readable verification status."""
        if not self.is_verified():
            return "Not Verified"
        elif self.is_legitimate():
            confidence_pct = int(self.verification_confidence * 100) if self.verification_confidence else 0
            return f"Verified Legitimate ({confidence_pct}% confidence)"
        else:
            return "Verified Not Legitimate"
    
    @abstractmethod
    def get_offer_type(self) -> str:
        """Return the specific type of this offer."""
        pass
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of essential offer information for quick overview.
        
        Returns:
            Dictionary containing summary information
        """
        summary = {
            "offer_type": self.get_offer_type(),
            "client_name": self.client_name,
            "job_description": self.job_description[:100] + "..." if len(self.job_description) > 100 else self.job_description,
            "date_time": self.date_time.strftime("%Y-%m-%d %H:%M"),
            "location": self.location,
            "payment_terms": self.payment_terms,
            "source_url": self.source_url,
            "verification_status": self.get_verification_status()
        }
        return summary
    
    def get_full_details(self) -> Dict[str, Any]:
        """
        Get complete offer details including verification information.
        
        Returns:
            Dictionary containing all offer information
        """
        details = {
            "offer_type": self.get_offer_type(),
            "client_info": {
                "name": self.client_name,
                "contact": self.client_contact,
                "company": self.client_company
            },
            "job_details": {
                "description": self.job_description,
                "date_time": self.date_time.isoformat(),
                "duration": self.duration,
                "location": self.location,
                "requirements": self.requirements
            },
            "payment_terms": self.payment_terms,
            "source_url": self.source_url,
            "created_at": self.created_at.isoformat(),
            "verification": {
                "is_legitimate": self.is_legitimate_job_offer,
                "confidence": self.verification_confidence,
                "notes": self.verification_notes,
                "verified_at": self.verified_at.isoformat() if self.verified_at else None,
                "enhanced_by_verification": self.enhanced_by_verification,
                "original_missing_fields": self.original_missing_fields
            }
        }
        
        # Add specific details from subclasses
        specific_details = self.get_specific_details()
        if specific_details:
            details["specific_details"] = specific_details
        
        return details
    
    @abstractmethod
    def get_specific_details(self) -> Dict[str, Any]:
        """Return offer-type-specific details."""
        pass
    
    def to_json(self) -> str:
        """Convert offer to JSON string."""
        return json.dumps(self.get_full_details(), indent=2)
    
    def __str__(self) -> str:
        """String representation of the offer."""
        verification_indicator = ""
        if self.is_verified():
            verification_indicator = " ✓" if self.is_legitimate() else " ✗"
        return f"{self.get_offer_type()} Offer - {self.client_name} ({self.date_time.strftime('%Y-%m-%d')}){verification_indicator}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the offer."""
        return f"{self.__class__.__name__}(client='{self.client_name}', date='{self.date_time.strftime('%Y-%m-%d %H:%M')}', verified={self.is_verified()})"