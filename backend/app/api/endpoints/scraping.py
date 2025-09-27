"""Scraping endpoints for web scraping operations."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from app.database.database import get_db
from app.api.schemas import ScrapeRequest, ScrapeResponse, ScrapeStatus
from app.models.product import Product
from app.models.scraping_session import ScrapingSession
from app.scrapers.scraper_factory import ScraperFactory
from app.core.config import settings

router = APIRouter()

# In-memory storage for tracking scraping sessions (in production, use Redis or database)
scraping_sessions = {}


async def run_scraping_task(session_id: str, product_id: int, url: str, max_reviews: int, db: Session):
    """Background task to run scraping operation."""
    session = db.query(ScrapingSession).filter(ScrapingSession.session_id == session_id).first()
    if not session:
        return
    
    try:
        # Update session status
        session.status = "running"
        session.started_at = datetime.utcnow()
        db.commit()
        
        # Get appropriate scraper
        scraper = ScraperFactory.get_scraper(url)
        
        # Run scraping
        reviews_data = await scraper.scrape_reviews(url, max_reviews=max_reviews)
        
        # Process and save reviews
        from app.models.review import Review
        reviews_created = 0
        reviews_failed = 0
        
        for review_data in reviews_data:
            try:
                review = Review(
                    product_id=product_id,
                    text=review_data.get('text', ''),
                    rating=review_data.get('rating'),
                    reviewer_name=review_data.get('reviewer_name'),
                    review_date=review_data.get('review_date'),
                    verified_purchase=review_data.get('verified_purchase', False),
                    helpful_votes=review_data.get('helpful_votes', 0),
                    total_votes=review_data.get('total_votes', 0),
                    source_url=url,
                    review_id_on_site=review_data.get('review_id')
                )
                db.add(review)
                reviews_created += 1
            except Exception as e:
                reviews_failed += 1
                print(f"Failed to save review: {e}")
        
        db.commit()
        
        # Update session with results
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.total_reviews_found = len(reviews_data)
        session.reviews_scraped = reviews_created
        session.reviews_failed = reviews_failed
        db.commit()
        
        # Update scraping_sessions cache
        scraping_sessions[session_id] = {
            "status": "completed",
            "total_reviews_found": len(reviews_data),
            "reviews_scraped": reviews_created,
            "reviews_failed": reviews_failed,
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Update session with error
        session.status = "failed"
        session.completed_at = datetime.utcnow()
        session.error_message = str(e)
        db.commit()
        
        # Update scraping_sessions cache
        scraping_sessions[session_id] = {
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.utcnow().isoformat()
        }


@router.post("/", response_model=ScrapeResponse)
async def start_scraping(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start scraping reviews from a product URL."""
    try:
        # Check if product already exists
        product = db.query(Product).filter(Product.url == str(request.url)).first()
        
        if not product:
            # Create new product
            # Extract basic product info (this would be enhanced with actual scraping)
            product = Product(
                name="Product Name",  # To be extracted during scraping
                url=str(request.url),
                platform=request.platform or "generic",
                category=None
            )
            db.add(product)
            db.commit()
            db.refresh(product)
        
        # Create scraping session
        session_id = str(uuid.uuid4())
        scraping_session = ScrapingSession(
            product_id=product.id,
            session_id=session_id,
            status="pending",
            scraper_config={
                "max_reviews": request.max_reviews,
                "platform": request.platform
            },
            user_agent=settings.USER_AGENT
        )
        
        db.add(scraping_session)
        db.commit()
        
        # Initialize session in cache
        scraping_sessions[session_id] = {
            "status": "pending",
            "product_id": product.id,
            "started_at": datetime.utcnow().isoformat()
        }
        
        # Start background scraping task
        background_tasks.add_task(
            run_scraping_task,
            session_id,
            product.id,
            str(request.url),
            request.max_reviews,
            db
        )
        
        return ScrapeResponse(
            session_id=session_id,
            product_id=product.id,
            status="started",
            message="Scraping started successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scraping: {str(e)}")


@router.get("/status/{session_id}", response_model=ScrapeStatus)
async def get_scraping_status(session_id: str, db: Session = Depends(get_db)):
    """Get the status of a scraping session."""
    # First check cache
    if session_id in scraping_sessions:
        cache_data = scraping_sessions[session_id]
        
        # Also get from database for accurate data
        session = db.query(ScrapingSession).filter(ScrapingSession.session_id == session_id).first()
        
        if session:
            return ScrapeStatus(
                session_id=session_id,
                status=session.status,
                progress=cache_data,
                total_reviews_found=session.total_reviews_found or 0,
                reviews_scraped=session.reviews_scraped or 0,
                reviews_failed=session.reviews_failed or 0,
                error_message=session.error_message
            )
    
    # Check database only
    session = db.query(ScrapingSession).filter(ScrapingSession.session_id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Scraping session not found")
    
    return ScrapeStatus(
        session_id=session_id,
        status=session.status,
        progress={},
        total_reviews_found=session.total_reviews_found or 0,
        reviews_scraped=session.reviews_scraped or 0,
        reviews_failed=session.reviews_failed or 0,
        error_message=session.error_message
    )


@router.get("/sessions", response_model=List[ScrapeStatus])
async def get_all_sessions(db: Session = Depends(get_db)):
    """Get all scraping sessions."""
    sessions = db.query(ScrapingSession).order_by(ScrapingSession.created_at.desc()).all()
    
    result = []
    for session in sessions:
        result.append(ScrapeStatus(
            session_id=session.session_id,
            status=session.status,
            progress=scraping_sessions.get(session.session_id, {}),
            total_reviews_found=session.total_reviews_found or 0,
            reviews_scraped=session.reviews_scraped or 0,
            reviews_failed=session.reviews_failed or 0,
            error_message=session.error_message
        ))
    
    return result