"""Create sample data for testing the Review Radar application."""

import asyncio
from datetime import datetime, timedelta
import random

from app.database.database import get_db
from app.models.product import Product
from app.models.review import Review
from app.models.analysis import AnalysisResult
from app.models.scraping_session import ScrapingSession
from sqlalchemy.orm import Session


async def create_sample_data():
    """Create sample data for testing."""
    print("Creating sample data...")
    
    # Get database session
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Sample products
        products_data = [
            {
                "name": "Wireless Bluetooth Headphones",
                "url": "https://www.amazon.com/dp/B08N5WRWNW",
                "category": "Electronics",
                "platform": "amazon",
                "image_url": "https://example.com/headphones.jpg",
                "price": "$49.99",
                "rating": "4.3",
                "total_reviews": 1250,
                "is_active": True
            },
            {
                "name": "Organic Cotton T-Shirt",
                "url": "https://www.amazon.com/dp/B09XYZ123",
                "category": "Clothing",
                "platform": "amazon",
                "price": "$19.99",
                "rating": "4.1",
                "total_reviews": 890,
                "is_active": True
            },
            {
                "name": "Stainless Steel Coffee Mug",
                "url": "https://shopify.example.com/coffee-mug",
                "category": "Home",
                "platform": "shopify",
                "price": "$24.99",
                "rating": "4.7",
                "total_reviews": 456,
                "is_active": True
            },
            {
                "name": "Gaming Mouse Pad",
                "url": "https://www.ebay.com/itm/123456789",
                "category": "Electronics",
                "platform": "ebay",
                "price": "$12.99",
                "rating": "3.9",
                "total_reviews": 234,
                "is_active": True
            },
        ]
        
        created_products = []
        for product_data in products_data:
            product = Product(**product_data)
            db.add(product)
            created_products.append(product)
        
        db.commit()
        print(f"Created {len(created_products)} products")
        
        # Sample reviews for each product
        sentiment_labels = ["POSITIVE", "NEGATIVE", "NEUTRAL"]
        review_texts = [
            "Great product! Really satisfied with the quality.",
            "Excellent value for money. Highly recommend!",
            "Good quality but shipping was slow.",
            "Not what I expected. Poor build quality.",
            "Amazing! Exactly as described.",
            "Okay product, nothing special.",
            "Terrible quality. Don't buy this.",
            "Perfect! Will buy again.",
            "Good but overpriced.",
            "Love it! Great purchase decision."
        ]
        
        for product in created_products:
            # Refresh to get the ID
            db.refresh(product)
            
            # Create random reviews
            num_reviews = min(product.total_reviews, 50)  # Limit for demo
            for i in range(num_reviews):
                review = Review(
                    product_id=product.id,
                    text=random.choice(review_texts),
                    rating=random.randint(1, 5),
                    reviewer_name=f"User{i+1}",
                    review_date=datetime.now() - timedelta(days=random.randint(1, 365)),
                    verified_purchase=random.choice([True, False]),
                    helpful_votes=random.randint(0, 20),
                    total_votes=random.randint(0, 30),
                    is_processed=random.choice([True, False])
                )
                db.add(review)
        
        db.commit()
        print(f"Created sample reviews for products")
        
        # Sample analysis results
        for product in created_products:
            analysis = AnalysisResult(
                product_id=product.id,
                total_reviews=product.total_reviews,
                overall_sentiment=random.choice(sentiment_labels),
                sentiment_score=random.uniform(0.3, 0.9),
                positive_percentage=random.uniform(40, 80),
                negative_percentage=random.uniform(10, 30),
                neutral_percentage=random.uniform(10, 40),
                trust_score=random.uniform(0.6, 0.95),
                aspects_data={"quality": 0.8, "price": 0.6, "shipping": 0.7},
                topics_data={"quality": 0.85, "value": 0.78},
                keywords=["quality", "value", "good", "recommend"],
                processing_time=random.uniform(10, 60)
            )
            db.add(analysis)
        
        db.commit()
        print(f"Created analysis results for products")
        
        # Sample scraping sessions
        session_statuses = ["completed", "running", "failed", "pending"]
        for i in range(5):
            session = ScrapingSession(
                session_id=f"session_{i+1}_{random.randint(1000, 9999)}",
                url=f"https://example.com/product/{i+1}",
                status=random.choice(session_statuses),
                total_reviews_found=random.randint(100, 2000),
                reviews_scraped=random.randint(50, 1000),
                reviews_failed=random.randint(0, 50),
                platform="amazon",
                max_reviews=1000
            )
            db.add(session)
        
        db.commit()
        print(f"Created sample scraping sessions")
        
        print("✅ Sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(create_sample_data())