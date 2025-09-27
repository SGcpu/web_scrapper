"""Amazon-specific scraper implementation focused on product search pages."""

from typing import List, Dict, Any
import re
import os
import time
import random

from app.scrapers.base_scraper import BaseScraper


class EnhancedAmazonScraper(BaseScraper):
    """Enhanced Amazon scraper that focuses on extracting product details and reviews from search results."""
    
    def can_handle_url(self, url: str) -> bool:
        """Check if this scraper can handle the given URL."""
        return 'amazon' in url.lower()
        
    async def scrape_reviews(self, url: str, max_reviews: int = 100) -> List[Dict[str, Any]]:
        """Scrape reviews for a product by extracting the product ID and using search pages."""
        reviews = []
        
        try:
            print(f"\n{'='*50}")
            print(f"Starting enhanced Amazon review scraping for URL: {url}")
            print(f"{'='*50}\n")
            
            # Set up browser if not already done
            if not self.browser or not self.page:
                await self.setup_browser()
            
            # Extract product ID from URL
            product_id = self._extract_product_id(url)
            if not product_id:
                print("Could not extract product ID from URL")
                return []
                
            print(f"Extracted product ID: {product_id}")
                
            # First, get product name from the product page
            product_name = await self._get_product_name(url)
            if not product_name:
                print("Could not get product name, using product ID")
                product_name = product_id
                
            # Create debug directory
            os.makedirs("debug_screenshots", exist_ok=True)
                
            # Create search query using product name or ID
            search_query = product_name if product_name else product_id
            search_query = search_query.replace(" ", "+")
            
            # Get domain from original URL
            domain = url.split("/")[2]  # e.g., amazon.com
            
            # Approach 1: Search for product reviews directly
            search_url = f"https://{domain}/s?k={search_query}+reviews"
            print(f"Searching for reviews with URL: {search_url}")
            
            if await self.navigate_to_url(search_url):
                # Save screenshot of search results
                await self.page.screenshot(path="debug_screenshots/search_results.png")
                
                # Try to extract reviews from search results page
                reviews_from_search = await self._extract_reviews_from_search()
                if reviews_from_search:
                    print(f"Found {len(reviews_from_search)} reviews from search results")
                    reviews.extend(reviews_from_search)
            
            # If we still need more reviews, try customer discussions
            if len(reviews) < max_reviews:
                discussions_url = f"https://{domain}/ask/questions/asin/{product_id}"
                print(f"Checking customer discussions: {discussions_url}")
                
                if await self.navigate_to_url(discussions_url):
                    await self.page.screenshot(path="debug_screenshots/discussions_page.png")
                    
                    # Extract useful content from discussions
                    discussions = await self._extract_discussions()
                    if discussions:
                        print(f"Found {len(discussions)} discussions that may contain reviews")
                        reviews.extend(discussions)
            
            # As a last resort, try the original product page
            if len(reviews) < max_reviews:
                print("Trying to extract reviews directly from product page")
                if await self.navigate_to_url(url):
                    # Scroll down to load all content
                    for position in [1000, 2000, 3000, 4000]:
                        await self.page.evaluate(f'window.scrollTo(0, {position})')
                        await self.random_delay(1, 2)
                    
                    # Save screenshot
                    await self.page.screenshot(path="debug_screenshots/product_page_final.png")
                    
                    # Try to find review sections
                    product_reviews = await self._extract_reviews_from_product_page()
                    if product_reviews:
                        print(f"Found {len(product_reviews)} reviews from product page")
                        reviews.extend(product_reviews)
            
            # Return unique reviews up to max_reviews
            unique_reviews = []
            seen_texts = set()
            
            for review in reviews:
                # Use first 100 chars as a unique identifier
                text_id = review.get('text', '')[:100] if review.get('text') else ''
                if text_id and text_id not in seen_texts and len(text_id) > 20:
                    seen_texts.add(text_id)
                    unique_reviews.append(review)
            
            result = unique_reviews[:max_reviews]
            print(f"\nFinished scraping. Found {len(result)} unique reviews.")
            return result
            
        except Exception as e:
            print(f"Error in enhanced Amazon scraper: {e}")
            return reviews
        finally:
            await self.cleanup_browser()
    
    def _extract_product_id(self, url: str) -> str:
        """Extract Amazon product ID from URL."""
        # Try various URL patterns
        patterns = [
            r'/dp/([A-Z0-9]{10})/?',
            r'/gp/product/([A-Z0-9]{10})/?',
            r'/product/([A-Z0-9]{10})/?',
            r'asin=([A-Z0-9]{10})/?',
            r'asin/([A-Z0-9]{10})/?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
        
    async def _get_product_name(self, url: str) -> str:
        """Get product name from the product page."""
        try:
            if await self.navigate_to_url(url):
                # Look for product title
                title_element = await self.page.query_selector('#productTitle')
                if title_element:
                    title = await title_element.inner_text()
                    return title.strip()
                
                # Alternative title selectors
                alt_selectors = ['.product-title', '.product-name', 'h1']
                for selector in alt_selectors:
                    element = await self.page.query_selector(selector)
                    if element:
                        text = await element.inner_text()
                        return text.strip()
        except Exception as e:
            print(f"Error getting product name: {e}")
            
        return None
        
    async def _extract_reviews_from_search(self) -> List[Dict[str, Any]]:
        """Extract reviews from search results page."""
        reviews = []
        
        try:
            # Look for review snippets in search results
            review_selectors = [
                '.a-row .a-size-base',
                '.a-expander-content',
                '.a-section .a-spacing-small',
                '.a-text-normal',
            ]
            
            for selector in review_selectors:
                elements = await self.page.query_selector_all(selector)
                print(f"Found {len(elements)} potential review elements with selector {selector}")
                
                for element in elements:
                    try:
                        text = await element.inner_text()
                        
                        # Check if this looks like a review (mentions stars or verified purchase)
                        if ('star' in text.lower() or 'review' in text.lower() or 'verified' in text.lower()) and len(text) > 50:
                            # Try to extract rating
                            rating = None
                            match = re.search(r'(\d+(\.\d+)?)\s*(?:out of 5 stars|stars)', text.lower())
                            if match:
                                try:
                                    rating = float(match.group(1))
                                except:
                                    pass
                                    
                            reviews.append({
                                'text': self.clean_text(text),
                                'rating': rating,
                                'verified_purchase': 'verified purchase' in text.lower()
                            })
                    except Exception as e:
                        print(f"Error processing search result element: {e}")
                        
        except Exception as e:
            print(f"Error extracting reviews from search: {e}")
            
        return reviews
        
    async def _extract_discussions(self) -> List[Dict[str, Any]]:
        """Extract useful content from customer discussions and questions."""
        reviews = []
        
        try:
            # Look for questions and answers
            qa_selectors = [
                '.askTeaserQuestions .a-spacing-base',
                '.a-section .a-spacing-small',
                '.askAnswerText',
                '.askAnswersAndComments',
                '.a-expander-content'
            ]
            
            for selector in qa_selectors:
                elements = await self.page.query_selector_all(selector)
                print(f"Found {len(elements)} potential Q&A elements with selector {selector}")
                
                for element in elements:
                    try:
                        text = await element.inner_text()
                        
                        # Only include substantial text that might be a review or useful opinion
                        if len(text) > 70:
                            reviews.append({
                                'text': self.clean_text(text),
                                'rating': None,  # Can't determine rating from Q&A
                                'source_type': 'customer_discussion'
                            })
                    except Exception as e:
                        print(f"Error processing discussion element: {e}")
                        
        except Exception as e:
            print(f"Error extracting discussions: {e}")
            
        return reviews
        
    async def _extract_reviews_from_product_page(self) -> List[Dict[str, Any]]:
        """Extract reviews directly from the product page."""
        reviews = []
        
        try:
            # First check if there's review content on the page
            page_text = await self.page.inner_text('body')
            has_reviews = any(term in page_text.lower() for term in 
                             ['customer reviews', 'star rating', 'verified purchase', 'top reviews'])
            
            if not has_reviews:
                print("No review content detected on product page")
                return []
                
            print("Found review-related content on product page, extracting reviews...")
                
            # Look for review sections
            review_sections = [
                '#customerReviews',
                '#customer-reviews-content',
                '#reviews-medley-footer',
                '.reviews-section',
                '.reviews-content'
            ]
            
            for section in review_sections:
                section_elem = await self.page.query_selector(section)
                if section_elem:
                    print(f"Found review section: {section}")
                    
                    # Look for review elements within this section
                    review_elements = await section_elem.query_selector_all('.a-section.review, [data-hook="review"], .review-card, .a-row')
                    print(f"Found {len(review_elements)} review elements in section")
                    
                    for element in review_elements:
                        try:
                            text = await element.inner_text()
                            
                            # Only include if it looks like a review
                            if len(text) > 50 and ('star' in text.lower() or 'verified' in text.lower()):
                                # Try to extract rating
                                rating = None
                                rating_elem = await element.query_selector('.a-icon-star')
                                
                                if rating_elem:
                                    rating_text = await rating_elem.inner_text()
                                    match = re.search(r'(\d+(\.\d+)?)', rating_text)
                                    if match:
                                        try:
                                            rating = float(match.group(1))
                                        except:
                                            pass
                                            
                                reviews.append({
                                    'text': self.clean_text(text),
                                    'rating': rating,
                                    'verified_purchase': 'verified purchase' in text.lower()
                                })
                        except Exception as e:
                            print(f"Error processing review element: {e}")
                    
                    # If we found reviews in this section, we can stop
                    if reviews:
                        break
                        
            # If we still haven't found reviews, look for any text that might contain review content
            if not reviews:
                print("Looking for reviews in general page text...")
                
                # Look for common review text patterns
                lines = page_text.split('\n')
                for i, line in enumerate(lines):
                    if ('out of 5 stars' in line.lower() or 'verified purchase' in line.lower()) and len(line) > 20:
                        # Get surrounding context (3 lines before and after)
                        start = max(0, i - 3)
                        end = min(len(lines), i + 4)
                        context = '\n'.join(lines[start:end])
                        
                        if len(context) > 50:
                            # Extract rating if possible
                            rating = None
                            match = re.search(r'(\d+(\.\d+)?)\s*out of 5 stars', context.lower())
                            if match:
                                try:
                                    rating = float(match.group(1))
                                except:
                                    pass
                                    
                            reviews.append({
                                'text': self.clean_text(context),
                                'rating': rating,
                                'verified_purchase': 'verified purchase' in context.lower()
                            })
            
        except Exception as e:
            print(f"Error extracting reviews from product page: {e}")
            
        return reviews