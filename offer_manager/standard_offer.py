"""
StandardOffer - Base class for all freelance job offers
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
import re
import json


class StandardOffer(ABC):
    """
    Abstract base class for freelance job offers.
    
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
        self.client_contact = self._validate_contact(client_contact)
        self.client_company = client_company
        self.job_description = job_description
        self.date_time = date_time
        self.duration = duration
        self.location = location
        self.payment_terms = payment_terms
        self.requirements = requirements
        self.source_url = self._validate_url(source_url) if source_url else None
        self.created_at = datetime.now()
    
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
        return {
            "offer_type": self.get_offer_type(),
            "client_name": self.client_name,
            "job_description": self.job_description[:100] + "..." if len(self.job_description) > 100 else self.job_description,
            "date_time": self.date_time.strftime("%Y-%m-%d %H:%M"),
            "location": self.location,
            "payment_terms": self.payment_terms,
            "source_url": self.source_url
        }
    
    def get_full_details(self) -> Dict[str, Any]:
        """
        Get complete offer details.
        
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
            "created_at": self.created_at.isoformat()
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
        return f"{self.get_offer_type()} Offer - {self.client_name} ({self.date_time.strftime('%Y-%m-%d')})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the offer."""
        return f"{self.__class__.__name__}(client='{self.client_name}', date='{self.date_time.strftime('%Y-%m-%d %H:%M')}')"