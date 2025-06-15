"""
OfferManager - Main class for managing freelance job offers
"""

from datetime import datetime, date
from typing import Dict, List, Any, Optional, Union
import json
import pickle
import uuid
from .standard_offer import StandardOffer


class OfferManager:
    """
    Manages a collection of job offers with quick overview and detailed access.
    
    Stores essential information for quick browsing while maintaining references
    to full StandardOffer objects for detailed access.
    """
    
    VALID_STATUSES = ["pending", "accepted", "declined", "completed"]
    
    def __init__(self):
        """Initialize an empty OfferManager."""
        self._offers: Dict[str, Dict[str, Any]] = {}
        self._full_offers: Dict[str, StandardOffer] = {}
    
    def add_offer(self, standard_offer: StandardOffer) -> str:
        """
        Add a new offer to the manager.
        
        Args:
            standard_offer: A StandardOffer instance to add
            
        Returns:
            str: The generated offer ID
            
        Raises:
            TypeError: If standard_offer is not a StandardOffer instance
        """
        if not isinstance(standard_offer, StandardOffer):
            raise TypeError("Offer must be an instance of StandardOffer")
        
        # Generate unique offer ID
        offer_id = str(uuid.uuid4())
        
        # Store essential information for quick overview
        essential_info = {
            "offer_id": offer_id,
            "job_title": standard_offer.get_offer_type(),
            "client_name": standard_offer.client_name,
            "date_time": standard_offer.date_time,
            "location": standard_offer.location,
            "status": "pending",
            "description": standard_offer.job_description[:200] + "..." 
                          if len(standard_offer.job_description) > 200 
                          else standard_offer.job_description,
            "source_url": standard_offer.source_url,
            "created_at": datetime.now()
        }
        
        # Store both essential info and full offer
        self._offers[offer_id] = essential_info
        self._full_offers[offer_id] = standard_offer
        
        return offer_id
    
    def list_offers(self, format_output: bool = True) -> Union[List[Dict[str, Any]], str]:
        """
        Display summary of all offers.
        
        Args:
            format_output: If True, return formatted string; if False, return raw data
            
        Returns:
            Formatted string or list of offer summaries
        """
        if not self._offers:
            return "No offers found." if format_output else []
        
        if not format_output:
            return list(self._offers.values())
        
        # Format output for display
        output_lines = ["=" * 100]
        output_lines.append(f"{'OFFER SUMMARY':^100}")
        output_lines.append("=" * 100)
        output_lines.append(f"{'ID':<8} {'Type':<12} {'Client':<18} {'Date':<12} {'Status':<10} {'Location':<15} {'Source':<25}")
        output_lines.append("-" * 100)
        
        # Sort by date (most recent first)
        sorted_offers = sorted(
            self._offers.values(), 
            key=lambda x: x['date_time'], 
            reverse=True
        )
        
        for offer in sorted_offers:
            source_display = offer['source_url'][:25] if offer['source_url'] else "N/A"
            output_lines.append(
                f"{offer['offer_id'][:8]:<8} "
                f"{offer['job_title']:<12} "
                f"{offer['client_name'][:18]:<18} "
                f"{offer['date_time'].strftime('%Y-%m-%d'):<12} "
                f"{offer['status'].title():<10} "
                f"{offer['location'][:15]:<15} "
                f"{source_display:<25}"
            )
        
        output_lines.append("=" * 100)
        output_lines.append(f"Total offers: {len(self._offers)}")
        
        return "\n".join(output_lines)
    
    def get_offer_by_id(self, offer_id: str) -> Optional[StandardOffer]:
        """
        Retrieve full offer details by ID.
        
        Args:
            offer_id: The offer ID to retrieve
            
        Returns:
            StandardOffer instance or None if not found
        """
        return self._full_offers.get(offer_id)
    
    def update_status(self, offer_id: str, status: str) -> bool:
        """
        Update offer status.
        
        Args:
            offer_id: The offer ID to update
            status: New status (must be valid)
            
        Returns:
            bool: True if updated successfully, False otherwise
            
        Raises:
            ValueError: If status is not valid
        """
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(self.VALID_STATUSES)}")
        
        if offer_id not in self._offers:
            return False
        
        self._offers[offer_id]["status"] = status
        return True
    
    def filter_offers(self, **criteria) -> List[Dict[str, Any]]:
        """
        Filter offers by various criteria.
        
        Args:
            **criteria: Filtering criteria (status, client_name, date_from, date_to, job_title)
            
        Returns:
            List of matching offers
        """
        filtered_offers = []
        
        for offer in self._offers.values():
            match = True
            
            # Filter by status
            if 'status' in criteria:
                if offer['status'] != criteria['status']:
                    match = False
                    continue
            
            # Filter by client name (case-insensitive partial match)
            if 'client_name' in criteria:
                if criteria['client_name'].lower() not in offer['client_name'].lower():
                    match = False
                    continue
            
            # Filter by job title (case-insensitive partial match)
            if 'job_title' in criteria:
                if criteria['job_title'].lower() not in offer['job_title'].lower():
                    match = False
                    continue
            
            # Filter by date range
            if 'date_from' in criteria:
                date_from = criteria['date_from']
                if isinstance(date_from, str):
                    date_from = datetime.fromisoformat(date_from)
                if offer['date_time'].date() < date_from.date():
                    match = False
                    continue
            
            if 'date_to' in criteria:
                date_to = criteria['date_to']
                if isinstance(date_to, str):
                    date_to = datetime.fromisoformat(date_to)
                if offer['date_time'].date() > date_to.date():
                    match = False
                    continue
            
            # Filter by location (case-insensitive partial match)
            if 'location' in criteria:
                if criteria['location'].lower() not in offer['location'].lower():
                    match = False
                    continue
            
            # Filter by source URL (case-insensitive partial match)
            if 'source_url' in criteria:
                offer_url = offer.get('source_url', '') or ''
                if criteria['source_url'].lower() not in offer_url.lower():
                    match = False
                    continue
            
            if match:
                filtered_offers.append(offer)
        
        return filtered_offers
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about offers.
        
        Returns:
            Dictionary with offer statistics
        """
        if not self._offers:
            return {"total": 0, "by_status": {}, "by_type": {}}
        
        stats = {
            "total": len(self._offers),
            "by_status": {},
            "by_type": {}
        }
        
        for offer in self._offers.values():
            # Count by status
            status = offer['status']
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Count by type
            job_type = offer['job_title']
            stats['by_type'][job_type] = stats['by_type'].get(job_type, 0) + 1
        
        return stats
    
    def remove_offer(self, offer_id: str) -> bool:
        """
        Remove an offer from the manager.
        
        Args:
            offer_id: The offer ID to remove
            
        Returns:
            bool: True if removed successfully, False if not found
        """
        if offer_id in self._offers:
            del self._offers[offer_id]
            del self._full_offers[offer_id]
            return True
        return False
    
    def save_to_file(self, filename: str, format_type: str = "json") -> bool:
        """
        Save offers to file.
        
        Args:
            filename: File path to save to
            format_type: Format to save in ("json" or "pickle")
            
        Returns:
            bool: True if saved successfully
            
        Raises:
            ValueError: If format_type is not supported
        """
        if format_type not in ["json", "pickle"]:
            raise ValueError("Format must be 'json' or 'pickle'")
        
        try:
            if format_type == "json":
                # Convert offers to JSON-serializable format
                json_data = {
                    "offers": {},
                    "full_offers": {}
                }
                
                for offer_id, offer in self._offers.items():
                    json_offer = offer.copy()
                    json_offer['date_time'] = offer['date_time'].isoformat()
                    json_offer['created_at'] = offer['created_at'].isoformat()
                    json_data["offers"][offer_id] = json_offer
                    
                    # Save full offer details
                    json_data["full_offers"][offer_id] = self._full_offers[offer_id].get_full_details()
                
                with open(filename, 'w') as f:
                    json.dump(json_data, f, indent=2)
            
            else:  # pickle
                data = {
                    "offers": self._offers,
                    "full_offers": self._full_offers
                }
                with open(filename, 'wb') as f:
                    pickle.dump(data, f)
            
            return True
            
        except Exception as e:
            print(f"Error saving to file: {e}")
            return False
    
    def load_from_file(self, filename: str, format_type: str = "json") -> bool:
        """
        Load offers from file.
        
        Args:
            filename: File path to load from
            format_type: Format to load from ("json" or "pickle")
            
        Returns:
            bool: True if loaded successfully
            
        Raises:
            ValueError: If format_type is not supported
        """
        if format_type not in ["json", "pickle"]:
            raise ValueError("Format must be 'json' or 'pickle'")
        
        try:
            if format_type == "pickle":
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                self._offers = data["offers"]
                self._full_offers = data["full_offers"]
            
            else:  # json
                # Note: JSON loading for full offers would require reconstructing
                # the StandardOffer objects, which is complex. For now, we'll
                # just load the basic offer data.
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                self._offers = {}
                for offer_id, offer in data["offers"].items():
                    offer['date_time'] = datetime.fromisoformat(offer['date_time'])
                    offer['created_at'] = datetime.fromisoformat(offer['created_at'])
                    self._offers[offer_id] = offer
                
                # Full offers would need to be reconstructed based on type
                # This is a limitation of JSON serialization with complex objects
                self._full_offers = {}
            
            return True
            
        except Exception as e:
            print(f"Error loading from file: {e}")
            return False
    
    def __len__(self) -> int:
        """Return number of offers."""
        return len(self._offers)
    
    def __str__(self) -> str:
        """String representation of the manager."""
        return f"OfferManager with {len(self._offers)} offers"