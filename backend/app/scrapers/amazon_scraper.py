"""Amazon-specific scraper implementation."""

from typing import List, Dict, Any
import re
import os
from urllib.parse import urlparse

from app.scrapers.base_scraper import BaseScraper


class AmazonScraper(BaseScraper):
    """Amazon product review scraper."""
    
    def can_handle_url(self, url: str) -> bool:
        """Check if this scraper can handle Amazon URLs."""
        parsed = urlparse(url)
        return 'amazon.' in parsed.netloc.lower()
    
    async def scrape_reviews(self, url: str, max_reviews: int = 100) -> List[Dict[str, Any]]:
        """Scrape reviews from Amazon product page."""
        reviews = []
        
        try:
            print(f"\n{'='*50}")
            print(f"Starting Amazon review scraping for URL: {url}")
            print(f"{'='*50}\n")
            
            # Set up browser if not already done
            if not self.browser or not self.page:
                await self.setup_browser()
                
            # Navigate to the product page
            if not await self.navigate_to_url(url):
                print("Failed to navigate to product page")
                return reviews
            
            # Save screenshot of initial product page for debugging
            os.makedirs("debug_screenshots", exist_ok=True)
            await self.page.screenshot(path="debug_screenshots/amazon_product_page.png")
            
            # Try multiple approaches to extract reviews
            
            # Approach 1: Try to get featured reviews directly from product page
            print("Approach 1: Attempting to scrape featured reviews from product page...")
            for scroll_position in [1000, 2000, 3000, 4000]:
                await self.page.evaluate(f"window.scrollTo(0, {scroll_position})")
                await self.random_delay(1, 2)
            await self.page.screenshot(path="debug_screenshots/product_page_scrolled.png")
            
            featured_reviews = await self._scrape_featured_reviews()
            if featured_reviews:
                print(f"Found {len(featured_reviews)} featured reviews on product page")
                reviews.extend(featured_reviews)
            
            # If we have enough reviews from the product page, return them
            if len(reviews) >= max_reviews:
                return reviews[:max_reviews]
                
            # Approach 2: Try to navigate to all reviews page
            # Only if we didn't get enough reviews from the product page
            print("\nApproach 2: Trying to navigate to dedicated reviews page...")
            
            # First go back to product page (in case we're not there)
            if not await self.navigate_to_url(url):
                print("Failed to navigate back to product page")
                # Return whatever reviews we have so far
                return reviews[:max_reviews] if reviews else []
                
            # Try to navigate to reviews page
            await self._navigate_to_reviews_page()
            await self.page.screenshot(path="debug_screenshots/after_reviews_navigation.png")
            
            # Check if we got redirected to sign-in page
            page_content = await self.page.content()
            page_url = self.page.url
            
            if 'signin' in page_url or 'sign-in' in page_url or 'ap/signin' in page_url or 'sign-in' in page_content.lower():
                print("Redirected to sign-in page. Cannot access reviews page without login.")
                # Return reviews we found from product page
                return reviews[:max_reviews] if reviews else []
            
            # If we successfully reached the reviews page, scrape reviews from multiple pages
            print("Successfully reached reviews page, scraping reviews...")
            page_count = 0
            max_pages = (max_reviews - len(reviews)) // 10 + 1
            
            while len(reviews) < max_reviews and page_count < max_pages:
                print(f"Scraping reviews page {page_count + 1}")
                page_reviews = await self._scrape_reviews_from_current_page()
                
                if not page_reviews:
                    print(f"No reviews found on page {page_count + 1}")
                    break
                    
                reviews.extend(page_reviews)
                print(f"Found {len(page_reviews)} reviews. Total now: {len(reviews)}")
                page_count += 1
                
                if len(reviews) < max_reviews and not await self._go_to_next_page():
                    print("No more review pages available")
                    break
                    
                await self.random_delay(2, 4)
            
            # If we still don't have reviews, try Approach 3: Use search for reviews directly
            if not reviews:
                print("\nApproach 3: Using direct search for reviews...")
                
                # Go back to product page
                if not await self.navigate_to_url(url):
                    return []
                
                # Try to extract product ID for search
                product_id = None
                if '/dp/' in url:
                    product_id = url.split('/dp/')[1].split('/')[0].split('?')[0]
                elif '/product/' in url:
                    product_id = url.split('/product/')[1].split('/')[0].split('?')[0]
                
                if product_id:
                    domain = url.split('/')[2]  # e.g. amazon.com
                    search_url = f"https://{domain}/s?k={product_id}+reviews"
                    print(f"Searching for reviews with URL: {search_url}")
                    
                    if await self.navigate_to_url(search_url):
                        await self.page.screenshot(path="debug_screenshots/review_search.png")
                        search_reviews = await self._scrape_reviews_from_current_page()
                        if search_reviews:
                            reviews.extend(search_reviews)
            
            reviews_to_return = reviews[:max_reviews]
            print(f"Finished scraping. Found {len(reviews_to_return)} total reviews.")
            return reviews_to_return
            
        except Exception as e:
            print(f"Error scraping Amazon reviews: {e}")
            return reviews
        finally:
            # Clean up resources
            await self.cleanup_browser()
            
    async def _scrape_featured_reviews(self) -> List[Dict[str, Any]]:
        """Scrape featured reviews from the product page."""
        reviews = []
        print("Scraping featured reviews from product page...")
        
        # Scroll down to make sure reviews are loaded
        await self.page.evaluate('window.scrollBy(0, 1000)')
        await self.random_delay(1, 2)
        
        # Scroll down more to load review section
        await self.page.evaluate('window.scrollBy(0, 1000)')
        await self.random_delay(1, 2)
        
        # Take screenshot after scrolling
        await self.page.screenshot(path="debug_screenshots/after_product_page_scroll.png")
        
        # Selectors specific to featured reviews on product pages
        featured_review_selectors = [
            # Top customer reviews section
            '#acrCustomerReviewText',
            '.a-section.a-spacing-none.review-views',
            '#customerReviews .review',
            '.review-data',
            '[data-hook="review"]',
            '.a-section.review',
            '.a-row.a-spacing-small.review-data',
            '#cm-cr-dp-review-list .a-section',
            '#customer-reviews-content .a-section',
            '#reviews-medley-footer .a-row',
            '.reviews-content .review',
            '.review-text-content'
        ]
        
        for selector in featured_review_selectors:
            print(f"Looking for featured reviews with selector: {selector}")
            try:
                review_elements = await self.page.query_selector_all(selector)
                print(f"Found {len(review_elements)} elements with {selector}")
                
                if len(review_elements) > 0:
                    for element in review_elements:
                        try:
                            review_data = await self._extract_review_data(element)
                            if review_data and review_data.get('text') and len(review_data.get('text', '')) > 10:
                                reviews.append(review_data)
                                print(f"Added featured review: {review_data.get('text', '')[:50]}...")
                        except Exception as e:
                            print(f"Error extracting featured review: {e}")
                
                # If we found some reviews, we can stop
                if reviews:
                    break
            except Exception as e:
                print(f"Error with featured review selector {selector}: {e}")
        
        print(f"Total featured reviews found: {len(reviews)}")
        return reviews
    
    async def _navigate_to_reviews_page(self):
        """Navigate to the reviews section."""
        print(f"Current URL: {self.page.url}")
        print("Looking for reviews link...")
        
        # Check if we're already on a reviews page
        if 'reviews' in self.page.url.lower() or 'dp/product-reviews' in self.page.url.lower():
            print("Already on reviews page")
            return
        
        # Try different approaches to get to the reviews page
        
        # 1. Try direct URL construction first (most reliable method)
        try:
            url = self.page.url
            domain = url.split('/')[2]  # Extract domain (amazon.com, amazon.in, etc.)
            
            # Extract product ID from URL
            product_id = None
            
            # Pattern 1: /dp/PRODUCTID
            if '/dp/' in url:
                product_id = url.split('/dp/')[1].split('/')[0].split('?')[0]
            # Pattern 2: /gp/product/PRODUCTID
            elif '/gp/product/' in url:
                product_id = url.split('/gp/product/')[1].split('/')[0].split('?')[0]
            # Pattern 3: /product/PRODUCTID
            elif '/product/' in url:
                product_id = url.split('/product/')[1].split('/')[0].split('?')[0]
                
            if product_id:
                # Construct reviews URL using the same domain as original URL
                reviews_url = f"https://{domain}/product-reviews/{product_id}/"
                print(f"Navigating directly to reviews URL: {reviews_url}")
                
                # Take screenshot before navigation
                await self.page.screenshot(path="debug_screenshots/before_reviews_navigation.png")
                
                await self.navigate_to_url(reviews_url)
                
                # Take screenshot after navigation
                await self.page.screenshot(path="debug_screenshots/after_reviews_navigation.png")
                
                # Log HTML content for debugging
                content = await self.page.content()
                with open("debug_screenshots/reviews_page_content.html", "w", encoding="utf-8") as f:
                    f.write(content[:10000])  # First 10K chars to avoid huge files
                    
                return
        except Exception as e:
            print(f"Failed to construct reviews URL: {e}")
        
        # 2. Try finding and clicking on review links
        selectors = [
            'a[data-hook="see-all-reviews-link-foot"]',
            'a[data-hook="see-all-reviews-link"]',
            'a:has-text("See all reviews")',
            'a:has-text("customer reviews")', 
            'a:has-text("ratings")',
            'a[href*="customerReviews"]',
            'a[href*="product-reviews"]',
            'a[href*="#reviews"]',
            'a[href*="review"]',
            '#reviews-medley-footer a',
            '.a-link-emphasis'  # Often used for review links
        ]
        
        for selector in selectors:
            try:
                print(f"Trying selector: {selector}")
                elements = await self.page.query_selector_all(selector)
                print(f"Found {len(elements)} elements for selector {selector}")
                
                for element in elements:
                    # Check if link text contains review-related keywords
                    text = await element.inner_text()
                    href = await element.get_attribute('href') or ''
                    print(f"Link text: '{text}', href: '{href}'")
                    
                    if ('review' in text.lower() or 
                        'rating' in text.lower() or 
                        'review' in href.lower() or 
                        'customerReviews' in href):
                        print(f"Found review link with text: '{text}'")
                        
                        # Take screenshot before clicking
                        await self.page.screenshot(path=f"debug_screenshots/before_click_{selector.replace('[', '_').replace(']', '_').replace(':', '_').replace('*', '_')}.png")
                        
                        # Click the link
                        await element.click()
                        await self.random_delay(2, 4)
                        
                        print(f"After clicking, URL is: {self.page.url}")
                        
                        # Take screenshot after clicking
                        await self.page.screenshot(path=f"debug_screenshots/after_click_{selector.replace('[', '_').replace(']', '_').replace(':', '_').replace('*', '_')}.png")
                        
                        return
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
                
        print("WARNING: Could not navigate to reviews page using any method")
    
    async def _scrape_reviews_from_current_page(self) -> List[Dict[str, Any]]:
        """Scrape reviews from the current page."""
        reviews = []
        print(f"Scraping reviews from URL: {self.page.url}")
        
        # Take a screenshot for debugging
        await self.page.screenshot(path="debug_screenshots/before_review_extraction.png")
        
        # Save HTML for debugging
        content = await self.page.content()
        with open("debug_screenshots/review_page_content.html", "w", encoding="utf-8") as f:
            f.write(content[:20000])  # First 20K chars to avoid huge files
        
        # Add scroll to make sure all reviews are loaded
        print("Scrolling to load all reviews...")
        await self.scroll_to_load_content(max_scrolls=5)
        
        # Take another screenshot after scrolling
        await self.page.screenshot(path="debug_screenshots/after_scrolling.png")
        
        # Updated selectors for 2023 Amazon review structure
        review_selectors = [
            # Generic review containers
            '[data-hook="review"]',
            '.review',
            '.review-card',
            '.a-section.review',
            '.a-section.celwidget',
            '.a-section.review-views',
            '.review-container',
            
            # Specific to review pages
            '#cm_cr-review_list .a-section.celwidget',
            '.review-views .a-section',
            'div.a-section.review',
            'div[data-hook="review"]',
            
            # Other potential selectors
            '.reviews-content .a-row',
            '.reviews-list .a-section',
            '.customer-review',
            '.reviews-container div'
        ]
        
        # Log all visible text for debugging
        try:
            text = await self.page.evaluate('() => document.body.innerText')
            print("\nPage text sample:")
            print(text[:1000])  # Print first 1000 chars
            
            # Check if keywords like "review", "rating", etc. are on the page
            review_keywords = ["review", "rating", "star", "customer", "verified", "purchase"]
            for keyword in review_keywords:
                if keyword in text.lower():
                    print(f"Keyword '{keyword}' found on page")
                else:
                    print(f"Keyword '{keyword}' NOT found on page")
        except Exception as e:
            print(f"Error getting page text: {e}")
        
        # Try each selector to find reviews
        for selector in review_selectors:
            print(f"\nTrying to find reviews with selector: {selector}")
            
            try:
                # Wait for reviews to load with increased timeout
                has_reviews = await self.wait_for_element(selector, timeout=10000)
                if not has_reviews:
                    print(f"No reviews found with selector: {selector}")
                    continue
                
                # Get all review elements
                review_elements = await self.page.query_selector_all(selector)
                print(f"Found {len(review_elements)} potential reviews with selector: {selector}")
                
                if len(review_elements) > 0:
                    # Debug first element content
                    if len(review_elements) > 0:
                        first_element = review_elements[0]
                        html = await self.page.evaluate('(element) => element.outerHTML', first_element)
                        print(f"Sample review element HTML (first 500 chars):\n{html[:500]}...\n")
                    
                    # Process each review
                    for element in review_elements:
                        try:
                            review_data = await self._extract_review_data(element)
                            
                            # Check if we got meaningful review data
                            if review_data and review_data.get('text') and len(review_data.get('text', '')) > 5:
                                print(f"Successfully extracted review: {review_data.get('text')[:30]}...")
                                reviews.append(review_data)
                            else:
                                print(f"Review data incomplete or too short: {review_data}")
                        except Exception as e:
                            print(f"Error extracting review data: {e}")
                            continue
                    
                    # If we found reviews with this selector, break the loop
                    if reviews:
                        break
                    
            except Exception as e:
                print(f"Error processing selector {selector}: {e}")
                continue
        
        print(f"Total reviews extracted: {len(reviews)}")
        return reviews
    
    async def _extract_review_data(self, element) -> Dict[str, Any]:
        """Extract review data from a review element."""
        review_data = {}
        
        try:
            # Get the HTML content for debugging
            try:
                html = await self.page.evaluate('(element) => element.outerHTML', element)
                short_html = html[:300] + '...' if len(html) > 300 else html
                print(f"Processing review element:\n{short_html}\n")
            except Exception as e:
                print(f"Could not get element HTML: {e}")
            
            # Review text - try multiple selectors for review body
            text_selectors = [
                '[data-hook="review-body"] span',
                '[data-hook="review-body"]',
                '.review-text',
                '.review-text-content span',
                '.a-expander-content',
                'span[data-hook="review-body"]',
                '.review-data',
                'span.a-size-base.review-text',
                '.a-row.a-spacing-small.review-data',
                'div[data-hook="review-collapsed"]',
                '.review-text-content',  # Common in 2023 Amazon
                'div.a-expander-content',  # Expanded review content
                'span[dir="auto"]',  # Often contains review text
                '.a-spacing-small[dir="auto"]' # Another common review container
            ]
            
            # Try to get review text
            review_text_found = False
            
            for selector in text_selectors:
                try:
                    text_element = await element.query_selector(selector)
                    if text_element:
                        text = await text_element.inner_text()
                        cleaned_text = self.clean_text(text)
                        if cleaned_text and len(cleaned_text) > 5:  # Ensure it's a meaningful review
                            review_data['text'] = cleaned_text
                            print(f"Found review text with selector '{selector}': {cleaned_text[:50]}...")
                            review_text_found = True
                            break
                except Exception as e:
                    print(f"Error with text selector {selector}: {e}")
            
            # If we still haven't found text, try getting all text from the element
            if not review_text_found:
                try:
                    text = await element.inner_text()
                    # Remove common noise like "Helpful" and "Report" buttons
                    text = re.sub(r'(Report|Helpful|See more)\b', '', text)
                    cleaned_text = self.clean_text(text)
                    
                    if cleaned_text and len(cleaned_text) > 10:  # Longer minimum length for full element text
                        review_data['text'] = cleaned_text
                        print(f"Using full element text: {cleaned_text[:50]}...")
                        review_text_found = True
                except Exception as e:
                    print(f"Error getting full element text: {e}")
            
            # Rating - try multiple selectors
            rating_selectors = [
                '[data-hook="review-star-rating"]',
                '[data-hook="review-star-rating"] span',
                '.a-icon-star',
                '.a-link-normal span.a-icon-alt',
                'i.a-icon.a-icon-star',
                'span.a-icon-alt'
            ]
            
            for selector in rating_selectors:
                rating_element = await element.query_selector(selector)
                if rating_element:
                    # Try different methods to extract rating
                    # Method 1: From class name (a-star-4 format)
                    rating_class = await rating_element.get_attribute('class') or ''
                    match = re.search(r'a-star-(\d+)', rating_class)
                    if match:
                        review_data['rating'] = float(match.group(1))
                        print(f"Found rating from class: {review_data['rating']}")
                        break
                        
                    # Method 2: From inner text (e.g. "4.0 out of 5 stars")
                    rating_text = await rating_element.inner_text()
                    match = re.search(r'(\d+(\.\d+)?)\s*out of\s*\d+', rating_text)
                    if match:
                        review_data['rating'] = float(match.group(1))
                        print(f"Found rating from text: {review_data['rating']}")
                        break
                        
                    # Method 3: From aria-label
                    aria_label = await rating_element.get_attribute('aria-label') or ''
                    match = re.search(r'(\d+(\.\d+)?)\s*out of\s*\d+', aria_label)
                    if match:
                        review_data['rating'] = float(match.group(1))
                        print(f"Found rating from aria-label: {review_data['rating']}")
                        break
            
            # Reviewer name - try multiple selectors
            name_selectors = [
                '[data-hook="review-author"]',
                '[data-hook="review-author"] span',
                '.a-profile-name',
                '.review-byline .a-link-normal',
                'span.a-profile-name',
                'a.a-profile'
            ]
            
            for selector in name_selectors:
                name_element = await element.query_selector(selector)
                if name_element:
                    name = await name_element.inner_text()
                    cleaned_name = self.clean_text(name)
                    if cleaned_name:
                        review_data['reviewer_name'] = cleaned_name
                        print(f"Found reviewer name: {cleaned_name}")
                        break
            
            # Review date - try multiple selectors
            date_selectors = [
                '[data-hook="review-date"]',
                '.review-date',
                'span.review-date',
                '.a-size-base.a-color-secondary'
            ]
            
            for selector in date_selectors:
                date_element = await element.query_selector(selector)
                if date_element:
                    date_text = await date_element.inner_text()
                    if 'on' in date_text.lower() or 'reviewed' in date_text.lower():
                        review_data['review_date'] = self.parse_date(date_text)
                        print(f"Found review date: {date_text}")
                        break
            
            # Verified purchase
            verified_selectors = [
                '[data-hook="avp-badge"]',
                '.a-size-mini:has-text("Verified Purchase")',
                'span:has-text("Verified Purchase")'
            ]
            
            review_data['verified_purchase'] = False
            for selector in verified_selectors:
                verified_element = await element.query_selector(selector)
                if verified_element:
                    review_data['verified_purchase'] = True
                    print("Found verified purchase badge")
                    break
            
            # Helpful votes
            helpful_selectors = [
                '[data-hook="helpful-vote-statement"]',
                '.cr-vote-text',
                'span:has-text("people found this helpful")',
                '.a-size-base:has-text("helpful")'
            ]
            
            review_data['helpful_votes'] = 0
            for selector in helpful_selectors:
                helpful_element = await element.query_selector(selector)
                if helpful_element:
                    helpful_text = await helpful_element.inner_text()
                    match = re.search(r'(\d+)', helpful_text)
                    if match:
                        review_data['helpful_votes'] = int(match.group(1))
                        print(f"Found helpful votes: {review_data['helpful_votes']}")
                        break
            
            review_data['total_votes'] = review_data['helpful_votes']  # Amazon doesn't show total votes
            
            # Review ID (if available)
            review_id = await element.get_attribute('id') or await element.get_attribute('data-hook')
            if review_id:
                review_data['review_id'] = review_id
                print(f"Found review ID: {review_id}")
            
        except Exception as e:
            print(f"Error extracting review data: {e}")
        
        # Check if we have the minimum required fields
        if not review_data.get('text'):
            print("WARNING: Could not extract review text, skipping this review")
            
        return review_data
    
    async def _go_to_next_page(self) -> bool:
        """Navigate to the next page of reviews."""
        try:
            print("Looking for next page link...")
            
            # Take screenshot for debugging
            await self.page.screenshot(path="debug_screenshots/before_next_page.png")
            
            # Look for next page link with improved selectors
            next_selectors = [
                'li.a-last a',
                'a:has-text("Next")',
                'a:has-text("Next page")',
                '.a-pagination .a-last a',
                '.a-pagination a[href*="pageNumber="]',
                '.a-pagination a:not(.a-disabled):has-text("→")',
                'a.a-link-normal[href*="page="]',
                'a[href*="pageNumber="]'
            ]
            
            # Try each selector
            for selector in next_selectors:
                print(f"Trying next page selector: {selector}")
                next_link = await self.page.query_selector(selector)
                
                if next_link:
                    # Check if the link is not disabled
                    classes = await next_link.get_attribute('class') or ''
                    if 'a-disabled' not in classes:
                        # Get link text and href for logging
                        link_text = await next_link.inner_text()
                        link_href = await next_link.get_attribute('href') or 'unknown'
                        print(f"Found next page link: '{link_text}' with href: {link_href}")
                        
                        # Click the link
                        await next_link.click()
                        await self.random_delay(3, 5)
                        
                        # Take screenshot after navigation
                        await self.page.screenshot(path="debug_screenshots/after_next_page.png")
                        
                        # Verify we actually changed pages
                        new_url = self.page.url
                        print(f"After clicking next page, URL is: {new_url}")
                        
                        # Wait for the page to stabilize
                        await self.random_delay(1, 2)
                        
                        return True
            
            # Alternative method: Try to modify URL directly if pattern is recognized
            current_url = self.page.url
            
            # Check for pageNumber parameter
            if 'pageNumber=' in current_url:
                match = re.search(r'pageNumber=(\d+)', current_url)
                if match:
                    current_page = int(match.group(1))
                    next_page = current_page + 1
                    next_url = current_url.replace(f'pageNumber={current_page}', f'pageNumber={next_page}')
                    print(f"Navigating to next page via URL modification: {next_url}")
                    await self.navigate_to_url(next_url)
                    return True
            
            # Check for page= parameter
            elif 'page=' in current_url:
                match = re.search(r'page=(\d+)', current_url)
                if match:
                    current_page = int(match.group(1))
                    next_page = current_page + 1
                    next_url = current_url.replace(f'page={current_page}', f'page={next_page}')
                    print(f"Navigating to next page via URL modification: {next_url}")
                    await self.navigate_to_url(next_url)
                    return True
            
            print("No next page found")
            return False
            
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            return False