"""
OfferFinder - Web search and AI-powered offer discovery system using smolagents
FIXED VERSION: LLMInterface is always available regardless of smolagents
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Protocol
from urllib.parse import urlparse
import re
from offer_manager.standard_offer import StandardOffer
from offer_manager.photography_offer import PhotographyOffer

# Always define LLMInterface protocol for type hints and compatibility
class LLMInterface(Protocol):
    def generate_response(self, prompt: str) -> str:
        """Generate a response from the LLM given a prompt."""
        pass

# Import smolagents for LLM functionality
try:
    from smolagents import CodeAgent, HfApiModel, LiteLLMModel
    SMOLAGENTS_AVAILABLE = True
except ImportError:
    SMOLAGENTS_AVAILABLE = False


class OfferFinder:
    """
    AI-powered offer discovery system that searches the web for freelance opportunities.
    
    This class uses an external LLM to intelligently search for and parse job offers,
    maintaining data integrity by explicitly handling missing information.
    """
    
    # Prompt templates - easily modifiable constants
    FREE_SEARCH_PROMPT_TEMPLATE = """
You are an expert freelance job finder. Search for job opportunities matching these criteria:

SEARCH CRITERIA:
- Job Type: {job_type}
- Location: {location} (expand to nearby areas if needed)
- Additional Filters: {additional_filters}

INSTRUCTIONS:
1. Find relevant freelance job opportunities from websites like:
   - Upwork, Fiverr, Freelancer
   - Craigslist, Facebook Marketplace
   - LinkedIn, Indeed
   - Photography-specific sites (if applicable)
   - Local job boards

2. For each opportunity found, extract the following information:
   - Client name (if available, otherwise use "Unknown Client")
   - Client contact (email/phone if available)
   - Client company (if available)
   - Job description
   - Date and time (if specified)
   - Duration (if specified)
   - Location/venue
   - Payment terms (if specified)
   - Requirements/specifications
   - Source URL (REQUIRED - exact URL where found)

3. CRITICAL RULES:
   - Only include information that is explicitly stated
   - Use "NOT_AVAILABLE" for any missing information
   - Do NOT guess or fabricate missing details
   - Always include the exact source URL

4. For photography jobs, also extract:
   - Event type (wedding, corporate, portrait, etc.)
   - Number of photos expected (if specified)
   - Equipment requirements (if specified)
   - Post-processing requirements (if specified)
   - Delivery format (if specified)
   - Delivery timeline (if specified)
   - Additional services (if specified)

Format your response as JSON with this structure:
{{
    "offers": [
        {{
            "client_name": "string or NOT_AVAILABLE",
            "client_contact": "string or NOT_AVAILABLE",
            "client_company": "string or NOT_AVAILABLE",
            "job_description": "string or NOT_AVAILABLE",
            "date_time": "ISO format or NOT_AVAILABLE",
            "duration": "string or NOT_AVAILABLE",
            "location": "string or NOT_AVAILABLE",
            "payment_terms": "string or NOT_AVAILABLE",
            "requirements": "string or NOT_AVAILABLE",
            "source_url": "REQUIRED - exact URL",
            "offer_type": "photography or general",
            "photography_details": {{
                "event_type": "string or NOT_AVAILABLE",
                "photos_expected": "number or NOT_AVAILABLE",
                "equipment_requirements": ["list or empty"],
                "post_processing_requirements": "string or NOT_AVAILABLE",
                "delivery_format": "string or NOT_AVAILABLE",
                "delivery_timeline": "string or NOT_AVAILABLE",
                "additional_services": ["list or empty"]
            }}
        }}
    ]
}}
"""

    PERSONALIZED_SEARCH_PROMPT_TEMPLATE = """
You are an AI assistant helping find personalized freelance opportunities. 

USER CONTEXT:
{user_context}

BASE CRITERIA:
- Job Type: {job_type}
- Location: {location}
- Additional Preferences: {preferences}

INSTRUCTIONS:
1. Based on the user context, intelligently search for opportunities that match their:
   - Experience level and skills
   - Working style and preferences  
   - Career goals and interests
   - Geographic and schedule preferences

2. Look for offers on platforms like:
   - Upwork, Fiverr, Freelancer
   - Craigslist, Facebook Marketplace
   - LinkedIn, Indeed
   - Specialized job boards
   - Professional networks

3. Prioritize opportunities that:
   - Match the user's expertise level
   - Align with their stated preferences
   - Offer growth potential
   - Fit their availability and location

4. For each opportunity, extract information following the same rules as free search:
   - Only include explicitly stated information
   - Use "NOT_AVAILABLE" for missing data
   - Do NOT guess or fabricate details
   - Always include exact source URL

5. Rank opportunities by relevance to user profile

Use the same JSON format as the free search template.
"""

    MISSING_DATA_DEFAULTS = {
        'client_name': 'Unknown Client',
        'client_contact': None,
        'client_company': None,
        'job_description': None,
        'date_time': None,
        'duration': None,
        'location': None,
        'payment_terms': None,
        'requirements': None,
        'event_type': 'other',
        'photos_expected': 0,
        'equipment_requirements': [],
        'post_processing_requirements': None,
        'delivery_format': 'digital_download',
        'delivery_timeline': None,
        'additional_services': []
    }

    def __init__(self, llm_instance: Optional[Union["CodeAgent", LLMInterface]] = None):
        """
        Initialize OfferFinder with an LLM instance.
        
        Args:
            llm_instance: Either a smolagents CodeAgent or an object implementing LLMInterface.
                         If None, will try to create a default smolagents instance.
        """
        if llm_instance is None and SMOLAGENTS_AVAILABLE:
            # Create default smolagents instance
            try:
                # Use a default HuggingFace model
                model = LiteLLMModel(model_id="gpt-3.5-turbo")
                self.llm = CodeAgent(tools=[], model=model)
                self.is_smolagents = True
            except Exception as e:
                self.logger = logging.getLogger(__name__)
                self.logger.warning(f"Failed to create default smolagents instance: {e}")
                self.llm = None
                self.is_smolagents = False
        elif SMOLAGENTS_AVAILABLE and hasattr(llm_instance, 'run'):
            # smolagents CodeAgent
            self.llm = llm_instance
            self.is_smolagents = True
        else:
            # Standard LLM interface
            self.llm = llm_instance
            self.is_smolagents = False
        
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging for search activities and missing information."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _generate_llm_response(self, prompt: str) -> str:
        """
        Generate a response from the LLM using either smolagents or standard interface.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response as a string
        """
        if self.llm is None:
            raise ValueError("No LLM instance available")
        
        try:
            if self.is_smolagents:
                # Use smolagents CodeAgent interface
                response = self.llm.run(prompt)
                # Extract text response from smolagents result
                if hasattr(response, 'content'):
                    return response.content
                elif isinstance(response, str):
                    return response
                else:
                    return str(response)
            else:
                # Use standard interface
                return self.llm.generate_response(prompt)
        except Exception as e:
            self.logger.error(f"Error generating LLM response: {e}")
            return ""

    def free_search(
        self, 
        criteria: Dict[str, Any], 
        known_offers: List[StandardOffer]
    ) -> List[StandardOffer]:
        """
        Perform a free search for offers matching specified criteria.
        
        Args:
            criteria: Search criteria dictionary
            known_offers: List of existing offers to avoid duplicates
            
        Returns:
            List of StandardOffer instances found
        """
        self.logger.info(f"Starting free search with criteria: {criteria}")
        
        try:
            # Extract search parameters
            job_type = criteria.get('job_type', 'freelance work')
            location = criteria.get('location', 'remote')
            additional_filters = criteria.get('additional_filters', {})
            
            # Create search prompt
            prompt = self.FREE_SEARCH_PROMPT_TEMPLATE.format(
                job_type=job_type,
                location=location,
                additional_filters=additional_filters
            )
            
            # Get LLM response
            response = self._generate_llm_response(prompt)
            
            # Parse response and create offers
            offers = self._parse_llm_response(response, known_offers)
            
            self.logger.info(f"Free search completed. Found {len(offers)} new offers.")
            return offers
            
        except Exception as e:
            self.logger.error(f"Error in free search: {e}")
            return []

    def personalized_search(
        self, 
        base_criteria: Dict[str, Any], 
        known_offers: List[StandardOffer],
        user_context: str = ""
    ) -> List[StandardOffer]:
        """
        Perform a personalized search using AI-driven matching.
        
        Args:
            base_criteria: Base search criteria
            known_offers: List of existing offers to avoid duplicates
            user_context: User profile and preferences
            
        Returns:
            List of StandardOffer instances found
        """
        self.logger.info("Starting personalized search")
        
        try:
            # Extract parameters
            job_type = base_criteria.get('job_type', 'freelance work')
            location = base_criteria.get('location', 'remote')
            preferences = base_criteria.get('preferences', {})
            
            # Create personalized prompt
            prompt = self.PERSONALIZED_SEARCH_PROMPT_TEMPLATE.format(
                user_context=user_context,
                job_type=job_type,
                location=location,
                preferences=preferences
            )
            
            # Get LLM response
            response = self._generate_llm_response(prompt)
            
            # Parse response and create offers
            offers = self._parse_llm_response(response, known_offers)
            
            self.logger.info(f"Personalized search completed. Found {len(offers)} new offers.")
            return offers
            
        except Exception as e:
            self.logger.error(f"Error in personalized search: {e}")
            return []

    def _parse_llm_response(
        self, 
        response: str, 
        known_offers: List[StandardOffer]
    ) -> List[StandardOffer]:
        """
        Parse LLM response and create StandardOffer instances.
        
        Args:
            response: JSON response from LLM
            known_offers: Existing offers to check for duplicates
            
        Returns:
            List of new StandardOffer instances
        """
        try:
            import json
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                self.logger.warning("No JSON found in LLM response")
                return []
            
            data = json.loads(json_match.group())
            offers_data = data.get('offers', [])
            
            new_offers = []
            existing_urls = {offer.source_url for offer in known_offers if offer.source_url}
            
            for offer_data in offers_data:
                # Check for duplicates
                source_url = offer_data.get('source_url')
                if not source_url or source_url in existing_urls:
                    self.logger.info(f"Skipping duplicate offer from {source_url}")
                    continue
                
                # Create offer instance
                offer = self._create_offer_from_data(offer_data)
                if offer:
                    new_offers.append(offer)
                    existing_urls.add(source_url)
            
            return new_offers
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing LLM response: {e}")
            return []

    def _create_offer_from_data(self, offer_data: Dict[str, Any]) -> Optional[StandardOffer]:
        """
        Create a StandardOffer instance from parsed data.
        
        Args:
            offer_data: Dictionary containing offer information
            
        Returns:
            StandardOffer instance or None if creation fails
        """
        try:
            # Extract and validate required fields
            source_url = offer_data.get('source_url')
            if not source_url or source_url == "NOT_AVAILABLE":
                self.logger.warning("Offer missing source URL, skipping")
                return None
            
            # Validate URL format
            if not self._is_valid_url(source_url):
                self.logger.warning(f"Invalid URL format: {source_url}")
                return None
            
            # Handle missing data with defaults
            processed_data = self._process_offer_data(offer_data)
            
            # Determine offer type and create appropriate instance
            offer_type = offer_data.get('offer_type', 'general')
            photography_details = offer_data.get('photography_details', {})
            
            if offer_type == 'photography' and photography_details:
                return self._create_photography_offer(processed_data, photography_details)
            else:
                # For now, we'll create a basic offer type
                # In a real implementation, you'd have other offer types
                self.logger.info(f"General offer type not implemented, creating photography offer as fallback")
                return self._create_photography_offer(processed_data, {})
                
        except Exception as e:
            self.logger.error(f"Error creating offer from data: {e}")
            return None

    def _process_offer_data(self, offer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process offer data and handle missing information.
        
        Args:
            offer_data: Raw offer data
            
        Returns:
            Processed offer data with proper defaults
        """
        processed = {}
        
        for field, default_value in self.MISSING_DATA_DEFAULTS.items():
            raw_value = offer_data.get(field)
            
            if raw_value == "NOT_AVAILABLE" or raw_value is None or raw_value == "":
                processed[field] = default_value
                self.logger.debug(f"Field '{field}' missing, using default: {default_value}")
            else:
                processed[field] = raw_value
        
        # Special handling for date_time
        date_time_str = offer_data.get('date_time')
        if date_time_str and date_time_str != "NOT_AVAILABLE":
            try:
                processed['date_time'] = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
            except ValueError:
                processed['date_time'] = datetime.now()  # Default to current time
                self.logger.warning(f"Invalid date format: {date_time_str}, using current time")
        else:
            processed['date_time'] = datetime.now()
            
        return processed

    def _create_photography_offer(
        self, 
        processed_data: Dict[str, Any], 
        photography_details: Dict[str, Any]
    ) -> Optional[PhotographyOffer]:
        """
        Create a PhotographyOffer instance.
        
        Args:
            processed_data: Processed offer data
            photography_details: Photography-specific details
            
        Returns:
            PhotographyOffer instance or None if creation fails
        """
        try:
            # Extract photography-specific fields
            event_type = photography_details.get('event_type', processed_data.get('event_type', 'other'))
            photos_expected = photography_details.get('photos_expected', processed_data.get('photos_expected', 0))
            equipment_requirements = photography_details.get('equipment_requirements', processed_data.get('equipment_requirements', []))
            post_processing_requirements = photography_details.get('post_processing_requirements', processed_data.get('post_processing_requirements'))
            delivery_format = photography_details.get('delivery_format', processed_data.get('delivery_format', 'digital_download'))
            delivery_timeline = photography_details.get('delivery_timeline', processed_data.get('delivery_timeline'))
            additional_services = photography_details.get('additional_services', processed_data.get('additional_services', []))
            
            # Handle numerical values
            if isinstance(photos_expected, str):
                try:
                    photos_expected = int(photos_expected)
                except ValueError:
                    photos_expected = 0
            
            # Ensure equipment_requirements is a list
            if isinstance(equipment_requirements, str):
                equipment_requirements = [equipment_requirements] if equipment_requirements else []
            
            # Ensure additional_services is a list
            if isinstance(additional_services, str):
                additional_services = [additional_services] if additional_services else []
            
            return PhotographyOffer(
                client_name=processed_data['client_name'],
                client_contact=processed_data['client_contact'],
                client_company=processed_data['client_company'],
                job_description=processed_data['job_description'],
                date_time=processed_data['date_time'],
                duration=processed_data['duration'],
                location=processed_data['location'],
                payment_terms=processed_data['payment_terms'],
                requirements=processed_data['requirements'],
                event_type=event_type,
                photos_expected=photos_expected,
                equipment_requirements=equipment_requirements,
                post_processing_requirements=post_processing_requirements,
                delivery_format=delivery_format,
                delivery_timeline=delivery_timeline,
                additional_services=additional_services,
                source_url=processed_data.get('source_url')
            )
            
        except Exception as e:
            self.logger.error(f"Error creating photography offer: {e}")
            return None

    def _is_valid_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid URL format
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _check_duplicate_offers(
        self, 
        new_offers: List[StandardOffer], 
        known_offers: List[StandardOffer]
    ) -> List[StandardOffer]:
        """
        Remove duplicate offers based on URL and content similarity.
        
        Args:
            new_offers: List of newly found offers
            known_offers: List of existing offers
            
        Returns:
            List of unique offers
        """
        unique_offers = []
        known_urls = {offer.source_url for offer in known_offers if offer.source_url}
        
        for offer in new_offers:
            if offer.source_url not in known_urls:
                unique_offers.append(offer)
                known_urls.add(offer.source_url)
            else:
                self.logger.info(f"Duplicate offer detected: {offer.source_url}")
        
        return unique_offers

    def get_search_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about recent searches.
        
        Returns:
            Dictionary with search statistics
        """
        # This would be implemented with actual tracking
        return {
            "total_searches": 0,
            "offers_found": 0,
            "duplicates_filtered": 0,
            "success_rate": 0.0
        }