"""
Freelance Offer Manager System

A Python package for managing freelance job offers with flexible offer types
and comprehensive management capabilities.
"""

from .offer_manager import OfferManager
from .standard_offer import StandardOffer
from .photography_offer import PhotographyOffer

__version__ = "1.0.0"
__all__ = ["OfferManager", "StandardOffer", "PhotographyOffer"]