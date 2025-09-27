"""Main API router."""

from fastapi import APIRouter
from app.api.endpoints import scraping, analysis, products, dashboard

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    scraping.router,
    prefix="/scrape",
    tags=["scraping"]
)

api_router.include_router(
    analysis.router,
    prefix="/analyze",
    tags=["analysis"]
)

api_router.include_router(
    products.router,
    prefix="/products",
    tags=["products"]
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["dashboard"]
)