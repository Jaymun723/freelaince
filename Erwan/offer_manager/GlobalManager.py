# global_manager.py

from typing import Dict, Any, List, Optional, Union
from offer_manager import OfferManager
from offer_finder import OfferFinder, LLMInterface
from standard_offer import StandardOffer
from verification_agent import VerificationAgent

# If smolagents is available
try:
    from smolagents import CodeAgent
except ImportError:
    CodeAgent = None  # Allows type checking even when smolagents isn't installed


class GlobalManager:
    """
    Global manager for coordinating offer discovery and management.
    """

    def __init__(self, llm_instance: Optional[Union["CodeAgent", LLMInterface]] = None):
        self.offer_manager = OfferManager()
        self.offer_finder = OfferFinder(llm_instance)
        self.verificator = VerificationAgent(llm_instance)

    def find_offers(self, criteria: Dict[str, Any], personalized: bool = False, user_context: str = "") -> List[StandardOffer]:
        """
        Finds new offers and adds them to the OfferManager.

        Args:
            criteria: Search criteria for finding offers.
            personalized: Whether to use personalized search.
            user_context: Context for personalized search.

        Returns:
            List of newly added offers.
        """
        known_offers = list(self.offer_manager._full_offers.values())

        new_offers = self.offer_finder.free_search(criteria, known_offers)

        for offer in new_offers:
            offer = self.verificator.verify_offer(offer)
            self.offer_manager.add_offer(offer)

        return new_offers

    def delete_offer(self, offer_id: str) -> bool:
        """
        Deletes an offer by ID.

        Args:
            offer_id: ID of the offer to delete.

        Returns:
            True if successfully deleted, False otherwise.
        """
        return self.offer_manager.remove_offer(offer_id)

    def get_offers(self) -> List[Dict[str, Any]]:
        """
        Returns a list of current offers.

        Returns:
            A list of offer summaries.
        """
        return self.offer_manager.list_offers(format_output=False)