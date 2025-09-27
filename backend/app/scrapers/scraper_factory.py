"""Scraper factory for creating appropriate scrapers based on URL."""

from typing import Type
from urllib.parse import urlparse

from app.scrapers.base_scraper import BaseScraper
from app.scrapers.amazon_scraper import AmazonScraper
from app.scrapers.generic_scraper import GenericScraper


class ScraperFactory:
    """Factory class for creating appropriate scrapers."""
    
    # Registry of available scrapers
    _scrapers = [
        AmazonScraper,
        GenericScraper,  # Keep generic as last fallback
    ]
    
    @classmethod
    def get_scraper(cls, url: str) -> BaseScraper:
        """Get appropriate scraper for the given URL."""
        for scraper_class in cls._scrapers:
            scraper = scraper_class()
            if scraper.can_handle_url(url):
                return scraper
        
        # Should never reach here since GenericScraper handles all URLs
        return GenericScraper()
    
    @classmethod
    def get_platform_name(cls, url: str) -> str:
        """Get platform name from URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if 'amazon.' in domain:
            return 'amazon'
        elif 'ebay.' in domain:
            return 'ebay'
        elif 'walmart.' in domain:
            return 'walmart'
        elif 'target.' in domain:
            return 'target'
        elif 'bestbuy.' in domain:
            return 'bestbuy'
        elif 'etsy.' in domain:
            return 'etsy'
        elif 'shopify' in domain:
            return 'shopify'
        else:
            return 'generic'
    
    @classmethod
    def register_scraper(cls, scraper_class: Type[BaseScraper]):
        """Register a new scraper class."""
        if scraper_class not in cls._scrapers:
            # Insert before generic scraper (keep generic as last)
            cls._scrapers.insert(-1, scraper_class)
    
    @classmethod
    def get_supported_platforms(cls) -> list:
        """Get list of supported platforms."""
        platforms = []
        for scraper_class in cls._scrapers:
            if hasattr(scraper_class, 'PLATFORM_NAME'):
                platforms.append(scraper_class.PLATFORM_NAME)
        return platforms