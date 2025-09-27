"""Simple test to verify the backend setup."""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_basic_imports():
    """Test basic Python packages."""
    try:
        import fastapi
        print(f"✓ FastAPI installed: {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI not installed")
        return False

    try:
        import sqlalchemy
        print(f"✓ SQLAlchemy installed: {sqlalchemy.__version__}")
    except ImportError:
        print("❌ SQLAlchemy not installed")
        return False

    try:
        import pydantic
        print(f"✓ Pydantic installed: {pydantic.__version__}")
    except ImportError:
        print("❌ Pydantic not installed")
        return False

    return True

def test_app_imports():
    """Test that app modules can be imported."""
    try:
        from app.core.config import settings
        print("✓ Config imported successfully")
        print(f"  - App name: {settings.APP_NAME}")
        print(f"  - Debug mode: {settings.DEBUG}")
        
        from app.database.database import Base, engine
        print("✓ Database configuration imported successfully")
        
        # Test database creation
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        
        try:
            from app.api.schemas import ScrapeRequest
            print("✓ API schemas imported successfully")
        except ImportError as e:
            print(f"⚠️  API schemas import warning: {e}")
        
        from app.scrapers.scraper_factory import ScraperFactory
        print("✓ Scraper factory imported successfully")
        
        # Test scraper factory
        scraper = ScraperFactory.get_scraper("https://amazon.com/product/123")
        print(f"✓ Scraper created: {type(scraper).__name__}")
        
        platform = ScraperFactory.get_platform_name("https://amazon.com/product/123")
        print(f"✓ Platform detected: {platform}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("Review Radar Backend Setup Test")
    print("=" * 40)
    
    basic_success = test_basic_imports()
    if not basic_success:
        print("\n❌ Basic packages not installed correctly")
        exit(1)
    
    app_success = test_app_imports()
    
    if app_success:
        print("\n🎉 All core components imported successfully!")
        print("\n✅ Backend setup is working correctly!")
        print("\nNext steps:")
        print("1. Install remaining ML packages: pip install keybert bertopic hdbscan umap-learn")
        print("2. Run the FastAPI server: uvicorn main:app --reload")
        print("3. Visit http://localhost:8000/docs for API documentation")
    else:
        print("\n❌ Backend setup needs attention")
        print("Please check the error messages above")