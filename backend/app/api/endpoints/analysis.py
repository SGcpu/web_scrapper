"""Analysis endpoints for ML processing operations."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
from datetime import datetime
import time

from app.database.database import get_db
from app.api.schemas import AnalysisRequest, AnalysisResponse, AnalysisResult
from app.models.product import Product
from app.models.review import Review
from app.models.analysis import AnalysisResult as AnalysisResultModel
from app.ml.sentiment_analyzer import get_sentiment_analyzer

router = APIRouter()

# In-memory storage for tracking analysis sessions
analysis_sessions = {}


async def run_analysis_task(session_id: str, product_id: int, db: Session):
    """Background task to run sentiment analysis."""
    try:
        # Update session status
        analysis_sessions[session_id]["status"] = "running"
        analysis_sessions[session_id]["started_at"] = datetime.utcnow().isoformat()
        
        # Get product and reviews
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise Exception("Product not found")
        
        reviews = db.query(Review).filter(
            Review.product_id == product_id,
            Review.is_processed == False
        ).all()
        
        if not reviews:
            raise Exception("No unprocessed reviews found for analysis")
        
        # Initialize sentiment analyzer
        analyzer = get_sentiment_analyzer()
        
        # Prepare review texts
        review_texts = [review.text for review in reviews]
        
        # Run sentiment analysis
        start_time = time.time()
        sentiment_results = analyzer.analyze_batch(review_texts)
        processing_time = time.time() - start_time
        
        # Save analysis results
        analysis_results = []
        for review, sentiment in zip(reviews, sentiment_results):
            analysis_result = AnalysisResultModel(
                review_id=review.id,
                sentiment_label=sentiment["label"],
                sentiment_score=sentiment["score"],
                model_version="distilbert-base-uncased-finetuned-sst-2-english",
                processing_time=processing_time / len(reviews)  # Average per review
            )
            db.add(analysis_result)
            analysis_results.append(analysis_result)
            
            # Mark review as processed
            review.is_processed = True
        
        db.commit()
        
        # Calculate aggregated results
        sentiment_distribution = analyzer.get_sentiment_distribution(sentiment_results)
        avg_sentiment_score = analyzer.get_average_sentiment_score(sentiment_results)
        
        # Prepare final result
        final_result = AnalysisResult(
            product_id=product_id,
            total_reviews=len(reviews),
            sentiment={
                "label": "POSITIVE" if avg_sentiment_score > 0.6 else "NEGATIVE" if avg_sentiment_score < 0.4 else "NEUTRAL",
                "score": avg_sentiment_score,
                "distribution": sentiment_distribution
            },
            aspects=[],  # TODO: Implement aspect analysis
            topics=[],   # TODO: Implement topic modeling
            keywords=[], # TODO: Implement keyword extraction
            trust_score=0.8,  # TODO: Implement trust scoring
            processing_time=processing_time
        )
        
        # Update session with results
        analysis_sessions[session_id].update({
            "status": "completed",
            "result": final_result.dict(),
            "completed_at": datetime.utcnow().isoformat(),
            "processing_time": processing_time
        })
        
    except Exception as e:
        # Update session with error
        analysis_sessions[session_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.utcnow().isoformat()
        })


@router.post("/", response_model=AnalysisResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start sentiment analysis for a product or custom reviews."""
    try:
        session_id = str(uuid.uuid4())
        
        if request.product_id:
            # Analyze existing product reviews
            product = db.query(Product).filter(Product.id == request.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Check if there are unprocessed reviews
            unprocessed_count = db.query(Review).filter(
                Review.product_id == request.product_id,
                Review.is_processed == False
            ).count()
            
            if unprocessed_count == 0:
                raise HTTPException(status_code=400, detail="No unprocessed reviews found for analysis")
            
            # Initialize session
            analysis_sessions[session_id] = {
                "status": "pending",
                "product_id": request.product_id,
                "total_reviews": unprocessed_count,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Start background analysis
            background_tasks.add_task(run_analysis_task, session_id, request.product_id, db)
            
            return AnalysisResponse(
                session_id=session_id,
                status="started",
                message=f"Analysis started for {unprocessed_count} reviews"
            )
            
        elif request.reviews:
            # TODO: Implement analysis for custom review texts
            raise HTTPException(status_code=501, detail="Custom review analysis not yet implemented")
        
        elif request.url:
            # TODO: Implement scraping + analysis workflow
            raise HTTPException(status_code=501, detail="URL-based analysis not yet implemented")
        
        else:
            raise HTTPException(status_code=400, detail="Must provide product_id, url, or reviews")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")


@router.get("/status/{session_id}", response_model=AnalysisResponse)
async def get_analysis_status(session_id: str):
    """Get the status of an analysis session."""
    if session_id not in analysis_sessions:
        raise HTTPException(status_code=404, detail="Analysis session not found")
    
    session_data = analysis_sessions[session_id]
    
    return AnalysisResponse(
        session_id=session_id,
        status=session_data["status"],
        result=session_data.get("result"),
        message=f"Analysis {session_data['status']}"
    )


@router.get("/results/{product_id}", response_model=AnalysisResult)
async def get_analysis_results(product_id: int, db: Session = Depends(get_db)):
    """Get the latest analysis results for a product."""
    # Get product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get all analysis results for this product
    analysis_results = db.query(AnalysisResultModel).join(Review).filter(
        Review.product_id == product_id
    ).all()
    
    if not analysis_results:
        raise HTTPException(status_code=404, detail="No analysis results found for this product")
    
    # Calculate aggregated results
    analyzer = get_sentiment_analyzer()
    sentiment_data = [
        {"label": result.sentiment_label, "score": result.sentiment_score}
        for result in analysis_results
    ]
    
    sentiment_distribution = analyzer.get_sentiment_distribution(sentiment_data)
    avg_sentiment_score = analyzer.get_average_sentiment_score(sentiment_data)
    
    # Get total processing time
    total_processing_time = sum(result.processing_time or 0 for result in analysis_results)
    
    return AnalysisResult(
        product_id=product_id,
        total_reviews=len(analysis_results),
        sentiment={
            "label": "POSITIVE" if avg_sentiment_score > 0.6 else "NEGATIVE" if avg_sentiment_score < 0.4 else "NEUTRAL",
            "score": avg_sentiment_score,
            "distribution": sentiment_distribution
        },
        aspects=[],  # TODO: Implement aspect analysis
        topics=[],   # TODO: Implement topic modeling
        keywords=[], # TODO: Implement keyword extraction
        trust_score=0.8,  # TODO: Implement trust scoring
        processing_time=total_processing_time
    )


@router.get("/sessions")
async def get_all_analysis_sessions():
    """Get all analysis sessions."""
    return {
        "sessions": list(analysis_sessions.values()),
        "total": len(analysis_sessions)
    }