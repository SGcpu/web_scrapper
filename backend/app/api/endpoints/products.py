"""Product endpoints for managing products and their data."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database.database import get_db
from app.api.schemas import Product, ProductCreate, ProductUpdate, ProductSummary
from app.models.product import Product as ProductModel
from app.models.review import Review
from app.models.analysis import AnalysisResult

router = APIRouter()


@router.get("/", response_model=List[ProductSummary])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    platform: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of products with summary information."""
    query = db.query(ProductModel)
    
    # Apply filters
    if platform:
        query = query.filter(ProductModel.platform == platform)
    if category:
        query = query.filter(ProductModel.category == category)
    
    products = query.offset(skip).limit(limit).all()
    
    # Build product summaries
    summaries = []
    for product in products:
        # Get review statistics
        review_count = db.query(Review).filter(Review.product_id == product.id).count()
        
        # Get average rating from reviews
        avg_rating_result = db.query(Review.rating).filter(
            Review.product_id == product.id,
            Review.rating.isnot(None)
        ).all()
        
        avg_rating = None
        if avg_rating_result:
            ratings = [r[0] for r in avg_rating_result if r[0] is not None]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
        
        # Get latest analysis sentiment score
        latest_analysis = db.query(AnalysisResult).join(Review).filter(
            Review.product_id == product.id
        ).order_by(AnalysisResult.created_at.desc()).first()
        
        sentiment_score = None
        last_analyzed = None
        if latest_analysis:
            sentiment_score = latest_analysis.sentiment_score
            last_analyzed = latest_analysis.created_at
        
        summaries.append(ProductSummary(
            id=product.id,
            name=product.name,
            url=product.url,
            platform=product.platform,
            total_reviews=review_count,
            avg_rating=avg_rating,
            sentiment_score=sentiment_score,
            last_analyzed=last_analyzed
        ))
    
    return summaries


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID."""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return Product.from_orm(product)


@router.post("/", response_model=Product)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    # Check if product with this URL already exists
    existing = db.query(ProductModel).filter(ProductModel.url == str(product.url)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product with this URL already exists")
    
    # Create new product
    db_product = ProductModel(
        name=product.name,
        url=str(product.url),
        category=product.category,
        platform=product.platform,
        image_url=str(product.image_url) if product.image_url else None,
        price=product.price,
        rating=product.rating
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return Product.from_orm(db_product)


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update a product."""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field in ["url", "image_url"] and value:
            value = str(value)
        setattr(product, field, value)
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    
    return Product.from_orm(product)


@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product and all associated data."""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete product (cascade will handle reviews and analysis results)
    db.delete(product)
    db.commit()
    
    return {"message": "Product deleted successfully"}


@router.get("/{product_id}/reviews")
async def get_product_reviews(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get reviews for a specific product."""
    # Check if product exists
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get reviews
    reviews = db.query(Review).filter(
        Review.product_id == product_id
    ).offset(skip).limit(limit).all()
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "reviews": [review.to_dict() for review in reviews],
        "total": db.query(Review).filter(Review.product_id == product_id).count()
    }


@router.get("/{product_id}/stats")
async def get_product_stats(product_id: int, db: Session = Depends(get_db)):
    """Get detailed statistics for a product."""
    # Check if product exists
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get review statistics
    total_reviews = db.query(Review).filter(Review.product_id == product_id).count()
    processed_reviews = db.query(Review).filter(
        Review.product_id == product_id,
        Review.is_processed == True
    ).count()
    
    # Get rating distribution
    ratings = db.query(Review.rating).filter(
        Review.product_id == product_id,
        Review.rating.isnot(None)
    ).all()
    
    rating_distribution = {}
    if ratings:
        for rating in [1, 2, 3, 4, 5]:
            count = sum(1 for r in ratings if r[0] and int(r[0]) == rating)
            rating_distribution[str(rating)] = count
    
    # Get sentiment distribution from analysis results
    sentiment_results = db.query(AnalysisResult.sentiment_label).join(Review).filter(
        Review.product_id == product_id
    ).all()
    
    sentiment_distribution = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
    for result in sentiment_results:
        sentiment_distribution[result[0]] = sentiment_distribution.get(result[0], 0) + 1
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "total_reviews": total_reviews,
        "processed_reviews": processed_reviews,
        "unprocessed_reviews": total_reviews - processed_reviews,
        "rating_distribution": rating_distribution,
        "sentiment_distribution": sentiment_distribution,
        "last_scraped": product.last_scraped.isoformat() if product.last_scraped else None,
        "created_at": product.created_at.isoformat() if product.created_at else None
    }