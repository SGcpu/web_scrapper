import asyncio
import os
import json
from app.scrapers.amazon_scraper import AmazonScraper

async def test_simple_scraper():
    """Test a simplified version of Amazon scraping focused on product page only."""
    print("\n=== Testing Amazon Scraper with Simplified Approach ===\n")
    
    # Create scraper instance
    scraper = AmazonScraper()
    
    # URLs to try
    urls = [
        "https://www.amazon.in/Apple-MWP22HN-A-AirPods-Pro/dp/B07ZRXF7M8/",  # Amazon India might have fewer restrictions
        "https://www.amazon.com/Apple-AirPods-Charging-Latest-Model/dp/B07PXGQC1Q"  # Amazon US as fallback
    ]
    
    reviews_found = []
    
    try:
        # Make debug directory
        os.makedirs("debug_screenshots", exist_ok=True)
        
        # Try each URL
        for url in urls:
            print(f"\nTrying URL: {url}")
            
            # Set up browser and navigate to page
            await scraper.setup_browser()
            
            # Navigate to URL
            print(f"Navigating to {url}")
            success = await scraper.navigate_to_url(url)
            if not success:
                print(f"Failed to navigate to {url}")
                await scraper.cleanup_browser()
                continue
            
            # Save screenshot
            await scraper.page.screenshot(path=f"debug_screenshots/product_page.png")
            
            # Scroll down to potentially reveal reviews
            print("Scrolling down page...")
            for position in [1000, 2000, 3000, 4000, 5000]:
                await scraper.page.evaluate(f'window.scrollTo(0, {position})')
                await asyncio.sleep(1)
            
            # Save screenshot after scrolling
            await scraper.page.screenshot(path=f"debug_screenshots/scrolled_page.png")
            
            # Check for review content
            print("\nChecking for review content...")
            page_text = await scraper.page.inner_text('body')
            
            # Look for review-related terms
            review_terms = ["customer reviews", "star rating", "verified purchase", 
                           "reviews", "top reviews", "review this product"]
            
            found_terms = []
            for term in review_terms:
                if term.lower() in page_text.lower():
                    found_terms.append(term)
            
            if found_terms:
                print(f"Found review-related terms: {', '.join(found_terms)}")
            else:
                print("No review-related terms found on page")
            
            # Try to extract reviews directly from page
            print("\nTrying to extract reviews from page...")
            page_reviews = await scraper._scrape_featured_reviews()
            
            if page_reviews:
                print(f"Success! Found {len(page_reviews)} reviews on product page")
                reviews_found.extend(page_reviews)
                
                # Print sample of first review
                if len(page_reviews) > 0:
                    print("\nSample review:")
                    review = page_reviews[0]
                    print(f"Text: {review.get('text', '')[:150]}...")
                    print(f"Rating: {review.get('rating')}")
                    print(f"Verified: {review.get('verified_purchase', False)}")
            else:
                print("No reviews found on product page")
            
            # Clean up browser
            await scraper.cleanup_browser()
        
        # Save any found reviews
        if reviews_found:
            print(f"\nTotal reviews found across all URLs: {len(reviews_found)}")
            with open("debug_screenshots/simple_reviews.json", "w", encoding="utf-8") as f:
                json.dump(reviews_found, f, indent=2)
            print("Reviews saved to debug_screenshots/simple_reviews.json")
        else:
            print("\nNo reviews found on any URL")
        
    except Exception as e:
        print(f"Error during test: {e}")
        await scraper.cleanup_browser()

if __name__ == "__main__":
    asyncio.run(test_simple_scraper())