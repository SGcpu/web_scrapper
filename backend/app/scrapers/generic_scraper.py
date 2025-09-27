"""Generic scraper for various e-commerce platforms."""

from typing import List, Dict, Any
import re
from urllib.parse import urlparse

from app.scrapers.base_scraper import BaseScraper


class GenericScraper(BaseScraper):
    """Generic scraper for various e-commerce platforms."""
    
    def can_handle_url(self, url: str) -> bool:
        """This scraper can handle any URL as a fallback."""
        return True
    
    async def scrape_reviews(self, url: str, max_reviews: int = 100) -> List[Dict[str, Any]]:
        """Scrape reviews using generic selectors."""
        reviews = []
        
        try:
            if not await self.navigate_to_url(url):
                return reviews
            
            # Scroll to load more content
            await self.scroll_to_load_content(max_scrolls=5)
            
            # Try multiple common review selectors
            review_selectors = [
                '.review',
                '.review-item',
                '.review-container',
                '[class*="review"]',
                '.comment',
                '.feedback',
                '.testimonial'
            ]
            
            for selector in review_selectors:
                elements = await self.page.query_selector_all(selector)
                if elements and len(elements) > 2:  # Found substantial reviews
                    for element in elements[:max_reviews]:
                        try:
                            review_data = await self._extract_generic_review_data(element)
                            if review_data and review_data.get('text'):
                                reviews.append(review_data)
                        except Exception as e:
                            print(f"Error extracting review: {e}")
                            continue
                    break
            
            return reviews[:max_reviews]
            
        except Exception as e:
            print(f"Error scraping generic reviews: {e}")
            return reviews
    
    async def _extract_generic_review_data(self, element) -> Dict[str, Any]:
        """Extract review data using generic selectors."""
        review_data = {}
        
        try:
            # Try to find review text using common selectors
            text_selectors = [
                '.review-text',
                '.review-content',
                '.review-body',
                '.comment-text',
                '.feedback-text',
                'p',
                '.text',
                '[class*="text"]',
                '[class*="content"]',
                '[class*="body"]'
            ]
            
            for selector in text_selectors:
                text_element = await element.query_selector(selector)
                if text_element:
                    text = await text_element.inner_text()
                    text = self.clean_text(text)
                    if len(text) > 20:  # Ensure it's substantial text
                        review_data['text'] = text
                        break
            
            # Try to find rating
            rating_selectors = [
                '.rating',
                '.stars',
                '.score',
                '[class*="rating"]',
                '[class*="star"]',
                '[class*="score"]'
            ]
            
            for selector in rating_selectors:
                rating_element = await element.query_selector(selector)
                if rating_element:
                    # Try different ways to extract rating
                    rating_text = await rating_element.inner_text()
                    rating = self.parse_rating(rating_text)
                    if rating:
                        review_data['rating'] = rating
                        break
                    
                    # Try data attributes
                    for attr in ['data-rating', 'data-score', 'data-stars']:
                        rating_attr = await rating_element.get_attribute(attr)
                        if rating_attr:
                            try:
                                review_data['rating'] = float(rating_attr)
                                break
                            except ValueError:
                                continue
                    
                    if 'rating' in review_data:
                        break
            
            # Try to find reviewer name
            name_selectors = [
                '.reviewer',
                '.author',
                '.user',
                '.name',
                '[class*="reviewer"]',
                '[class*="author"]',
                '[class*="user"]',
                '[class*="name"]'
            ]
            
            for selector in name_selectors:
                name_element = await element.query_selector(selector)
                if name_element:
                    name = await name_element.inner_text()
                    name = self.clean_text(name)
                    if name and len(name) < 100:  # Reasonable name length
                        review_data['reviewer_name'] = name
                        break
            
            # Try to find date
            date_selectors = [
                '.date',
                '.time',
                '.timestamp',
                '[class*="date"]',
                '[class*="time"]'
            ]
            
            for selector in date_selectors:
                date_element = await element.query_selector(selector)
                if date_element:
                    date_text = await date_element.inner_text()
                    date = self.parse_date(date_text)
                    if date:
                        review_data['review_date'] = date
                        break
            
            # Set defaults
            review_data.setdefault('verified_purchase', False)
            review_data.setdefault('helpful_votes', 0)
            review_data.setdefault('total_votes', 0)
            
        except Exception as e:
            print(f"Error extracting generic review data: {e}")
        
        return review_data