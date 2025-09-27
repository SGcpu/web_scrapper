"""Pydantic schemas for API request/response models."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


# Base schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    url: HttpUrl
    category: Optional[str] = Field(None, max_length=100)
    platform: str = Field(..., max_length=50)
    image_url: Optional[HttpUrl] = None
    price: Optional[str] = Field(None, max_length=50)
    rating: Optional[str] = Field(None, max_length=10)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    url: Optional[HttpUrl] = None
    category: Optional[str] = Field(None, max_length=100)
    platform: Optional[str] = Field(None, max_length=50)
    image_url: Optional[HttpUrl] = None
    price: Optional[str] = Field(None, max_length=50)
    rating: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: int
    total_reviews: int
    last_scraped: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Scraping schemas
class ScrapeRequest(BaseModel):
    url: HttpUrl
    max_reviews: Optional[int] = Field(500, ge=1, le=1000)
    platform: Optional[str] = None


class ScrapeResponse(BaseModel):
    session_id: str
    product_id: int
    status: str
    message: str


class ScrapeStatus(BaseModel):
    session_id: str
    status: str
    progress: Dict[str, Any]
    total_reviews_found: int
    reviews_scraped: int
    reviews_failed: int
    error_message: Optional[str] = None


# Analysis schemas
class AnalysisRequest(BaseModel):
    product_id: Optional[int] = None
    url: Optional[HttpUrl] = None
    reviews: Optional[List[str]] = None


class SentimentResult(BaseModel):
    label: str
    score: float
    distribution: Dict[str, float]


class AspectSentiment(BaseModel):
    aspect: str
    sentiment: str
    score: float
    mentions: int


class TopicResult(BaseModel):
    topic_id: int
    label: str
    keywords: List[str]
    probability: float
    review_count: int


class AnalysisResult(BaseModel):
    product_id: int
    total_reviews: int
    sentiment: SentimentResult
    aspects: List[AspectSentiment]
    topics: List[TopicResult]
    keywords: List[str]
    trust_score: float
    processing_time: float


class AnalysisResponse(BaseModel):
    session_id: str
    status: str
    result: Optional[AnalysisResult] = None
    message: str


# Review schemas
class ReviewBase(BaseModel):
    text: str = Field(..., min_length=1)
    rating: Optional[float] = Field(None, ge=1, le=5)
    reviewer_name: Optional[str] = Field(None, max_length=200)
    review_date: Optional[datetime] = None
    verified_purchase: bool = False
    helpful_votes: int = Field(0, ge=0)
    total_votes: int = Field(0, ge=0)


class ReviewCreate(ReviewBase):
    product_id: int


class Review(ReviewBase):
    id: int
    product_id: int
    source_url: Optional[str]
    review_id_on_site: Optional[str]
    is_processed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Dashboard schemas
class DashboardSummary(BaseModel):
    total_products: int
    total_reviews: int
    avg_sentiment: float
    recent_analyses: int


class ProductSummary(BaseModel):
    id: int
    name: str
    url: str
    platform: str
    total_reviews: int
    avg_rating: Optional[float]
    sentiment_score: Optional[float]
    last_analyzed: Optional[datetime]


# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Success schemas
class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None