"""
VerificationAgent - AI-powered verification system for job offers
"""

import logging
import re
import requests
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlparse
from .standard_offer import StandardOffer

# Import smolagents for LLM functionality
try:
    from smolagents import CodeAgent, InferenceClientModel
    SMOLAGENTS_AVAILABLE = True
except ImportError:
    SMOLAGENTS_AVAILABLE = False


class VerificationAgent:
    """
    AI-powered verification system that validates job offers and enhances missing information.
    
    This agent performs two key functions:
    1. Employer vs Freelancer Detection - Ensures offers are from legitimate employers
    2. Missing Information Extraction - Scrapes source URLs to fill in missing data
    """
    
    # Prompt template for employer vs freelancer detection
    EMPLOYER_DETECTION_PROMPT = """
You are an expert at analyzing job postings to determine if they are legitimate job offers from employers hiring freelancers, or if they are freelancers offering their own services.

OFFER DETAILS TO ANALYZE:
- Client Name: {client_name}
- Company: {client_company}
- Job Description: {job_description}
- Payment Terms: {payment_terms}
- Requirements: {requirements}
- Source URL: {source_url}

ANALYSIS CRITERIA:
Look for these EMPLOYER indicators (positive signs):
- Company names rather than individual names
- Language like "We are hiring", "We need", "Our company requires"
- Job descriptions describing work to be done
- HR/corporate language
- Company email domains
- Specific project requirements
- Budget/rate offerings from client perspective

Look for these FREELANCER indicators (negative signs):
- Individual names offering services
- Language like "I offer", "My services include", "I am available"
- Service descriptions (what they can do for you)
- Portfolio mentions
- Personal email addresses
- Marketing language about their skills
- "Contact me for" language

ANALYSIS TASK:
1. Determine if this is a legitimate job offer FROM an employer TO hire a freelancer
2. Provide a confidence score (0.0 to 1.0)
3. Explain your reasoning

Respond in JSON format:
{{
    "is_legitimate_employer": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation of your analysis",
    "employer_indicators": ["list of positive signs found"],
    "freelancer_indicators": ["list of negative signs found"]
}}
"""

    # Prompt template for missing information extraction
    INFORMATION_EXTRACTION_PROMPT = """
You are an expert at extracting job posting information from web page content.

ORIGINAL OFFER DATA:
- Client Name: {client_name}
- Company: {client_company}
- Job Description: {job_description}
- Payment Terms: {payment_terms}
- Requirements: {requirements}
- Duration: {duration}
- Contact: {client_contact}
- Location: {location}

WEB PAGE CONTENT:
{page_content}

EXTRACTION TASK:
Analyze the web page content to find missing or incomplete information for the job offer.
Look for:
- Complete company name (if missing or incomplete)
- Full job description (if truncated)
- Salary/rate information (if missing)
- Complete requirements/qualifications
- Contact information (email, phone)
- Employment type (full-time, part-time, contract)
- Application deadline
- Additional job details

IMPORTANT RULES:
- Mark fields as "NOT_FOUND" if not available on the page
- Preserve original data if the page version is not more complete

Respond in JSON format:
{{
    "enhanced_data": {{
        "client_company": "complete company name or NOT_FOUND",
        "job_description": "complete description or NOT_FOUND",
        "payment_terms": "salary/rate info or NOT_FOUND",
        "requirements": "complete requirements or NOT_FOUND",
        "client_contact": "contact info or NOT_FOUND",
        "duration": "employment type/duration or NOT_FOUND",
        "location": "complete location or NOT_FOUND"
    }},
    "additional_info": {{
        "application_deadline": "deadline or NOT_FOUND",
        "employment_type": "full-time/part-time/contract or NOT_FOUND",
        "benefits": "benefits mentioned or NOT_FOUND"
    }},
    "extraction_notes": "Summary of what was found/enhanced"
}}
"""

    def __init__(self, llm_instance=None):
        """
        Initialize VerificationAgent with an LLM instance.
        
        Args:
            llm_instance: smolagents CodeAgent or compatible LLM interface
        """
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        if llm_instance is None and SMOLAGENTS_AVAILABLE:
            try:
                # Create default smolagents instance for verification
                model = InferenceClientModel("microsoft/DialoGPT-medium")
                self.llm = CodeAgent(tools=[], model=model)
                self.is_smolagents = True
                self.logger.info("Created default smolagents instance for verification")
            except Exception as e:
                self.logger.warning(f"Failed to create default smolagents instance: {e}")
                self.llm = None
                self.is_smolagents = False
        elif SMOLAGENTS_AVAILABLE and hasattr(llm_instance, 'run'):
            self.llm = llm_instance
            self.is_smolagents = True
        else:
            self.llm = llm_instance
            self.is_smolagents = False
        
        # Configuration
        self.request_timeout = 10
        self.max_page_content_length = 10000
        self.enable_url_scraping = True
    
    def _setup_logging(self):
        """Configure logging for verification activities."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def verify_offer(self, offer: StandardOffer) -> StandardOffer:
        """
        Perform complete verification of a job offer.
        
        Args:
            offer: StandardOffer instance to verify
            
        Returns:
            Enhanced StandardOffer with verification results
        """
        self.logger.info(f"Starting verification for offer: {offer.client_name}")
        
        try:
            # Step 1: Employer vs Freelancer Detection
            is_legitimate, confidence, reasoning = self._detect_employer_vs_freelancer(offer)
            
            # Step 2: Missing Information Extraction (only if legitimate)
            enhanced_data = {}
            if is_legitimate and offer.source_url and self.enable_url_scraping:
                enhanced_data = self._extract_missing_information(offer)
            
            # Step 3: Apply verification results
            missing_fields = self._identify_missing_fields(offer)
            
            verification_notes = reasoning
            if enhanced_data:
                verification_notes += f" Enhanced with additional data from source."
            
            offer.set_verification_result(
                is_legitimate=is_legitimate,
                confidence=confidence,
                notes=verification_notes,
                missing_fields=missing_fields
            )
            
            # Step 4: Enhance offer with additional data
            if enhanced_data and is_legitimate:
                offer.enhance_with_verification_data(enhanced_data)
            
            self.logger.info(f"Verification completed: legitimate={is_legitimate}, confidence={confidence:.2f}")
            return offer
            
        except Exception as e:
            self.logger.error(f"Error during verification: {e}")
            # Set failed verification result
            offer.set_verification_result(
                is_legitimate=False,
                confidence=0.0,
                notes=f"Verification failed: {str(e)}"
            )
            return offer
    
    def _detect_employer_vs_freelancer(self, offer: StandardOffer) -> Tuple[bool, float, str]:
        """
        Detect if offer is from employer or freelancer using AI analysis.
        
        Args:
            offer: StandardOffer to analyze
            
        Returns:
            Tuple of (is_legitimate_employer, confidence_score, reasoning)
        """
        if self.llm is None:
            self.logger.warning("No LLM available for employer detection")
            return False, 0.0, "No LLM available for verification"
        
        try:
            # Prepare prompt with offer details
            prompt = self.EMPLOYER_DETECTION_PROMPT.format(
                client_name=offer.client_name or "NOT_AVAILABLE",
                client_company=offer.client_company or "NOT_AVAILABLE",
                job_description=offer.job_description or "NOT_AVAILABLE",
                payment_terms=offer.payment_terms or "NOT_AVAILABLE",
                requirements=offer.requirements or "NOT_AVAILABLE",
                source_url=offer.source_url or "NOT_AVAILABLE"
            )
            
            # Get LLM response
            response = self._generate_llm_response(prompt)
            
            # Parse response
            return self._parse_employer_detection_response(response)
            
        except Exception as e:
            self.logger.error(f"Error in employer detection: {e}")
            return False, 0.0, f"Detection failed: {str(e)}"
    
    def _extract_missing_information(self, offer: StandardOffer) -> Dict[str, Any]:
        """
        Extract missing information by scraping the source URL.
        
        Args:
            offer: StandardOffer with source_url to scrape
            
        Returns:
            Dictionary with enhanced data
        """
        if not offer.source_url:
            return {}
        
        try:
            # Scrape page content
            page_content = self._scrape_url_content(offer.source_url)
            if not page_content:
                return {}
            
            if self.llm is None:
                self.logger.warning("No LLM available for information extraction")
                return {}
            
            # Prepare prompt with page content
            prompt = self.INFORMATION_EXTRACTION_PROMPT.format(
                client_name=offer.client_name or "NOT_AVAILABLE",
                client_company=offer.client_company or "NOT_AVAILABLE", 
                job_description=offer.job_description or "NOT_AVAILABLE",
                payment_terms=offer.payment_terms or "NOT_AVAILABLE",
                requirements=offer.requirements or "NOT_AVAILABLE",
                duration=offer.duration or "NOT_AVAILABLE",
                client_contact=offer.client_contact or "NOT_AVAILABLE",
                location=offer.location or "NOT_AVAILABLE",
                page_content=page_content[:self.max_page_content_length]
            )
            
            # Get LLM response
            response = self._generate_llm_response(prompt)
            
            # Parse and return enhanced data
            return self._parse_extraction_response(response)
            
        except Exception as e:
            self.logger.error(f"Error extracting missing information: {e}")
            return {}
    
    def _scrape_url_content(self, url: str) -> Optional[str]:
        """
        Scrape text content from a URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Text content or None if failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.request_timeout)
            response.raise_for_status()
            
            # Basic text extraction (would be enhanced with BeautifulSoup in production)
            content = response.text
            
            # Remove HTML tags (simple approach)
            text_content = re.sub(r'<[^>]+>', ' ', content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            self.logger.info(f"Successfully scraped {len(text_content)} characters from {url}")
            return text_content
            
        except requests.RequestException as e:
            self.logger.warning(f"Failed to scrape URL {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error scraping URL {url}: {e}")
            return None
    
    def _generate_llm_response(self, prompt: str) -> str:
        """Generate response from LLM."""
        try:
            if self.is_smolagents:
                response = self.llm.run(prompt)
                if hasattr(response, 'content'):
                    return response.content
                elif isinstance(response, str):
                    return response
                else:
                    return str(response)
            else:
                return self.llm.generate_response(prompt)
        except Exception as e:
            self.logger.error(f"Error generating LLM response: {e}")
            return ""
    
    def _parse_employer_detection_response(self, response: str) -> Tuple[bool, float, str]:
        """Parse employer detection response."""
        try:
            import json
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return False, 0.0, "Could not parse verification response"
            
            data = json.loads(json_match.group())
            
            is_legitimate = data.get('is_legitimate_employer', False)
            confidence = float(data.get('confidence', 0.0))
            reasoning = data.get('reasoning', 'No reasoning provided')
            
            return is_legitimate, confidence, reasoning
            
        except Exception as e:
            self.logger.error(f"Error parsing employer detection response: {e}")
            return False, 0.0, f"Failed to parse response: {str(e)}"
    
    def _parse_extraction_response(self, response: str) -> Dict[str, Any]:
        """Parse information extraction response."""
        try:
            import json
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return {}
            
            data = json.loads(json_match.group())
            enhanced_data = data.get('enhanced_data', {})
            
            # Filter out NOT_FOUND values
            filtered_data = {}
            for key, value in enhanced_data.items():
                if value and value != "NOT_FOUND" and value.strip():
                    filtered_data[key] = value
            
            return filtered_data
            
        except Exception as e:
            self.logger.error(f"Error parsing extraction response: {e}")
            return {}
    
    def _identify_missing_fields(self, offer: StandardOffer) -> Dict[str, bool]:
        """Identify which fields are missing in the original offer."""
        missing = {}
        
        missing['client_contact'] = not bool(offer.client_contact)
        missing['client_company'] = not bool(offer.client_company)
        missing['payment_terms'] = not bool(offer.payment_terms)
        missing['requirements'] = not bool(offer.requirements)
        missing['duration'] = not bool(offer.duration)
        
        return missing
    
    def verify_batch(self, offers: List[StandardOffer]) -> List[StandardOffer]:
        """
        Verify multiple offers in batch.
        
        Args:
            offers: List of StandardOffer instances to verify
            
        Returns:
            List of verified StandardOffer instances
        """
        self.logger.info(f"Starting batch verification of {len(offers)} offers")
        
        verified_offers = []
        for i, offer in enumerate(offers, 1):
            self.logger.info(f"Verifying offer {i}/{len(offers)}: {offer.client_name}")
            verified_offer = self.verify_offer(offer)
            verified_offers.append(verified_offer)
        
        legitimate_count = sum(1 for offer in verified_offers if offer.is_legitimate())
        self.logger.info(f"Batch verification completed: {legitimate_count}/{len(offers)} offers verified as legitimate")
        
        return verified_offers
    
    def get_verification_stats(self, offers: List[StandardOffer]) -> Dict[str, Any]:
        """Get verification statistics for a list of offers."""
        total = len(offers)
        if total == 0:
            return {"total": 0, "verified": 0, "legitimate": 0, "enhanced": 0}
        
        verified = sum(1 for offer in offers if offer.is_verified())
        legitimate = sum(1 for offer in offers if offer.is_legitimate())
        enhanced = sum(1 for offer in offers if offer.enhanced_by_verification)
        
        avg_confidence = 0.0
        confidence_scores = [offer.verification_confidence for offer in offers if offer.verification_confidence is not None]
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        return {
            "total": total,
            "verified": verified,
            "legitimate": legitimate,
            "enhanced": enhanced,
            "verification_rate": verified / total,
            "legitimacy_rate": legitimate / verified if verified > 0 else 0,
            "enhancement_rate": enhanced / total,
            "average_confidence": avg_confidence
        }