import asyncio
import os
import json
import re
from app.scrapers.amazon_scraper import AmazonScraper

async def extract_review_text(element):
    """Extract review text from an element."""
    # Try various selectors for review text
    text_selectors = [
        '.review-text-content span',
        '.review-text',
        '[data-hook="review-body"] span',
        '[data-hook="review-body"]',
        '.a-expander-content',
        '.review-data',
    ]
    
    for selector in text_selectors:
        try:
            text_element = await element.query_selector(selector)
            if text_element:
                text = await text_element.inner_text()
                if text and len(text.strip()) > 5:
                    return text.strip()
        except Exception as e:
            print(f"Error extracting review text with selector {selector}: {e}")
    
    # If we couldn't find text with specific selectors, try getting all text
    try:
        text = await element.inner_text()
        return text.strip()
    except:
        return None

async def extract_rating(element):
    """Extract rating from an element."""
    # Try various selectors for ratings
    rating_selectors = [
        '[data-hook="review-star-rating"]',
        'i.a-icon-star',
        '.a-icon-star',
    ]
    
    for selector in rating_selectors:
        try:
            rating_element = await element.query_selector(selector)
            if rating_element:
                # Try to get rating from text like "4.0 out of 5 stars"
                rating_text = await rating_element.inner_text()
                if rating_text:
                    match = re.search(r'(\d+(\.\d+)?)', rating_text)
                    if match:
                        return float(match.group(1))
                
                # Try to get rating from class (e.g., a-star-4)
                class_attr = await rating_element.get_attribute('class')
                if class_attr:
                    match = re.search(r'a-star-(\d+)', class_attr)
                    if match:
                        return float(match.group(1))
        except Exception as e:
            print(f"Error extracting rating with selector {selector}: {e}")
    
    return None

async def test_amazon_scraper():
    print("Testing enhanced Amazon scraper with direct methods...")
    
    # Create a scraper instance
    scraper = AmazonScraper()
    reviews_found = []
    
    try:
        # Make sure debug folder exists
        os.makedirs("debug_screenshots", exist_ok=True)
        
        # Setup the browser with anti-detection measures
        await scraper.setup_browser()
        
        # Use an Amazon India URL as an alternative
        test_urls = [
            "https://www.amazon.com/Apple-AirPods-Charging-Latest-Model/dp/B07PXGQC1Q",
            "https://www.amazon.in/Apple-MWP22HN-A-AirPods-Pro/dp/B07ZRXF7M8/",
            "https://www.amazon.com/Apple-MLWK3AM-A-AirPods-3rd-Generation/dp/B09JQMJHXY/"
        ]
        
        for test_url in test_urls:
            print(f"\n\n{'='*50}")
            print(f"Testing URL: {test_url}")
            print(f"{'='*50}")
            
            # Navigate to product page
            if not await scraper.navigate_to_url(test_url):
                print(f"Failed to navigate to {test_url}, trying next URL")
                continue
            
            # Take screenshot of product page
            await scraper.page.screenshot(path=f"debug_screenshots/product_page_{test_url.split('/')[-2]}.png")
            
            print("\nExtracting data from product page...")
            
            # First, extract product info
            try:
                product_title = await scraper.page.query_selector('#productTitle')
                if product_title:
                    title_text = await product_title.inner_text()
                    print(f"Product: {title_text.strip()}")
            except Exception as e:
                print(f"Error getting product title: {e}")
            
            # Progressive scrolling to ensure reviews are loaded
            print("Scrolling down the page to find reviews...")
            scroll_positions = [1000, 2000, 3000, 4000, 5000]
            
            for position in scroll_positions:
                print(f"Scrolling to position {position}...")
                await scraper.page.evaluate(f'window.scrollTo(0, {position})')
                await asyncio.sleep(2)
                
                # Take a screenshot at each scroll position
                await scraper.page.screenshot(path=f"debug_screenshots/scroll_to_{position}.png")
            
            # Now try to find reviews
            print("\nLooking for review elements on product page...")
            
            # Review container selectors (from most specific to most generic)
            review_containers = [
                '#customerReviews .a-section.review',
                '#customerReviews [data-hook="review"]',
                '#cm_cr-review_list .a-section',
                '.reviews-content .a-section',
                '[data-hook="review"]',
                '.review',
                '.a-section.review',
                '.a-section.celwidget',
                '#reviews-medley-footer .a-row',
                '.reviews-section',
                '.customer-reviews',
            ]
            
            reviews_found_on_page = False
            
            for container_selector in review_containers:
                review_elements = await scraper.page.query_selector_all(container_selector)
                print(f"Selector: {container_selector} - Found: {len(review_elements)} elements")
                
                if len(review_elements) > 0:
                    reviews_found_on_page = True
                    print(f"Found {len(review_elements)} potential reviews with selector: {container_selector}")
                    
                    for i, review_element in enumerate(review_elements):
                        if i >= 5:  # Limit to 5 reviews for testing
                            break
                            
                        try:
                            # Extract review text
                            review_text = await extract_review_text(review_element)
                            
                            # Extract rating
                            rating = await extract_rating(review_element)
                            
                            # Only add if we found meaningful text
                            if review_text and len(review_text.strip()) > 10:
                                print(f"\nReview #{i+1}:")
                                print(f"  Text: {review_text[:100]}...")
                                if rating:
                                    print(f"  Rating: {rating}")
                                
                                reviews_found.append({
                                    "text": review_text,
                                    "rating": rating,
                                    "source_url": test_url
                                })
                        except Exception as e:
                            print(f"Error processing review element #{i}: {e}")
                    
                    # If we found reviews with this selector, break
                    if reviews_found:
                        break
            
            if not reviews_found_on_page:
                print("No reviews found with container selectors, trying direct text search...")
                
                # Look for review sections by text content
                review_related_texts = [
                    'Top reviews from',
                    'Customer reviews',
                    'out of 5 stars',
                    'Verified Purchase',
                    'Top positive review',
                    'Top critical review'
                ]
                
                # Get all text from page
                page_text = await scraper.page.inner_text('body')
                
                for text in review_related_texts:
                    if text.lower() in page_text.lower():
                        print(f"Found text on page: '{text}'")
                        
                        # Get surrounding context
                        index = page_text.lower().find(text.lower())
                        start = max(0, index - 100)
                        end = min(len(page_text), index + len(text) + 400)
                        context = page_text[start:end]
                        print(f"Context: '...{context}...'")
                
                # Look for review snippets
                try:
                    # Try to find full text using content near the review text 
                    elements = await scraper.page.query_selector_all('.a-row')
                    for element in elements:
                        text = await element.inner_text()
                        if 'review' in text.lower() or 'stars' in text.lower() or 'verified purchase' in text.lower():
                            print(f"Potential review content: {text[:100]}...")
                            
                            # If text looks like a review (has substantial content and rating-related text)
                            if len(text) > 50 and ('star' in text.lower() or 'review' in text.lower()):
                                reviews_found.append({
                                    "text": text,
                                    "rating": None,  # We don't have a reliable rating
                                    "source_url": test_url
                                })
                except Exception as e:
                    print(f"Error searching for review snippets: {e}")
        
        # Save all found reviews to a file
        print(f"\nTotal reviews found across all URLs: {len(reviews_found)}")
        if reviews_found:
            with open("debug_screenshots/extracted_reviews.json", "w", encoding="utf-8") as f:
                json.dump(reviews_found, f, indent=2)
            print(f"Reviews saved to debug_screenshots/extracted_reviews.json")
        
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        # Clean up
        await scraper.cleanup_browser()

if __name__ == "__main__":
    asyncio.run(test_amazon_scraper())