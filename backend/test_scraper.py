import asyncio
from app.scrapers.scraper_factory import ScraperFactory

async def test_scraper():
    print("Testing Amazon scraper...")
    scraper = ScraperFactory.get_scraper('https://www.amazon.com/dp/B07PXGQC1Q')
    reviews = await scraper.scrape_reviews('https://www.amazon.com/dp/B07PXGQC1Q', max_reviews=5)
    print(f'Found {len(reviews)} reviews')
    for i, review in enumerate(reviews):
        print(f"Review {i+1}:")
        print(f"  Text: {review.get('text', '')[:100]}...")
        print(f"  Rating: {review.get('rating')}")
        print(f"  Reviewer: {review.get('reviewer_name')}")
        print(f"  Date: {review.get('review_date')}")
        print(f"  Verified: {review.get('verified_purchase')}")
        print("")

if __name__ == "__main__":
    asyncio.run(test_scraper())