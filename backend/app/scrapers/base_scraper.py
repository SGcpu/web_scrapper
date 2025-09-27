"""Base scraper class with common functionality."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page, Browser
import asyncio
import time
import random
from datetime import datetime
import re

from app.core.config import settings


class BaseScraper(ABC):
    """Base scraper class with common functionality."""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.delay = settings.SCRAPING_DELAY
        self.user_agent = settings.USER_AGENT
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.setup_browser()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup_browser()
    
    async def setup_browser(self):
        """Initialize browser and page."""
        try:
            print("Setting up browser...")
            # Make sure we don't have a stale browser
            await self.cleanup_browser()
            
            # Import inside method to handle any import errors
            from playwright.async_api import async_playwright
            import random
            
            playwright = await async_playwright().start()
            
            # Use randomized user agent to avoid detection patterns
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
            ]
            
            selected_user_agent = random.choice(user_agents)
            print(f"Selected user agent: {selected_user_agent}")
            
            # Random viewport dimensions to appear more human-like
            viewport_widths = [1920, 1800, 1680, 1600, 1440]
            viewport_heights = [1080, 1000, 900, 960, 850]
            
            viewport_width = random.choice(viewport_widths)
            viewport_height = random.choice(viewport_heights)
            
            # Randomize timezones and locales
            timezones = ['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles', 'Europe/London']
            locales = ['en-US', 'en-GB', 'en-CA']
            
            print(f"Launching chromium browser with enhanced anti-detection measures")
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-extensions',
                    '--disable-blink-features=AutomationControlled',  # Hide automation
                    '--disable-features=IsolateOrigins,site-per-process', # Disable site isolation
                    f'--window-size={viewport_width},{viewport_height}',
                    '--disable-infobars',
                    '--disable-notifications',
                ]
            )
            
            print(f"Creating browser context with viewport {viewport_width}x{viewport_height}")
            context = await self.browser.new_context(
                user_agent=selected_user_agent,
                viewport={'width': viewport_width, 'height': viewport_height},
                locale=random.choice(locales),
                timezone_id=random.choice(timezones),
                accept_downloads=True,
                permissions=['geolocation', 'notifications'],
                color_scheme=random.choice(['light', 'no-preference']),
                reduced_motion='no-preference',
                # Add some HTTP headers that normal browsers send
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'sec-ch-ua': '"Chromium";v="123", "Google Chrome";v="123"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-site': 'none',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-user': '?1',
                    'sec-fetch-dest': 'document',
                }
            )
            
            # Enhanced anti-detection script that handles more fingerprinting techniques
            await context.add_init_script("""
                // Hide automation flags
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 1 });
                
                // Add typical Chrome plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format', 
                          length: 1, item: () => { return { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' }; } },
                        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: 'Portable Document Format', 
                          length: 1, item: () => { return { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' }; } },
                        { name: 'Native Client', filename: 'internal-nacl-plugin', description: 'Native Client', 
                          length: 1, item: () => { return { name: 'Native Client', filename: 'internal-nacl-plugin' }; } }
                    ]
                });
                
                // Spoof mimeTypes
                Object.defineProperty(navigator, 'mimeTypes', {
                    get: () => [
                        { type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format', enabledPlugin: {} },
                        { type: 'application/x-google-chrome-pdf', suffixes: 'pdf', description: 'Chrome PDF Viewer', enabledPlugin: {} }
                    ]
                });
                
                // Consistent languages
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                
                // Override hardware concurrency to appear more like a typical computer
                Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
                
                // Override deviceMemory
                Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
                
                // Modify screen properties
                if (window.screen) {
                    Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
                    Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });
                }
                
                // Modify getClientRects function to return more consistent values
                HTMLElement.prototype._getBoundingClientRect = HTMLElement.prototype.getBoundingClientRect;
                HTMLElement.prototype.getBoundingClientRect = function() {
                    const rect = this._getBoundingClientRect();
                    // Round to integer to remove floating point artifacts that fingerprinters might use
                    return {
                        x: Math.round(rect.x),
                        y: Math.round(rect.y),
                        top: Math.round(rect.top),
                        left: Math.round(rect.left),
                        right: Math.round(rect.right),
                        bottom: Math.round(rect.bottom),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height)
                    };
                };
            """)
            
            print("Creating new page...")
            self.page = await context.new_page()
            
            # Only block minimal resources to avoid detection
            print("Setting up minimal request interception...")
            # Allow most resources through, only block some rarely needed ones
            # This makes the browser appear more normal
            
            print("Browser setup completed successfully")
            
        except Exception as e:
            print(f"Failed to setup browser: {e}")
            raise
    
    async def cleanup_browser(self):
        """Clean up browser resources."""
        try:
            print("Cleaning up browser resources...")
            if self.page:
                print("Closing page...")
                await self.page.close()
                self.page = None
            if self.browser:
                print("Closing browser...")
                await self.browser.close()
                self.browser = None
            print("Browser cleanup completed")
        except Exception as e:
            print(f"Error during browser cleanup: {e}")
            # Reset references even if cleanup fails
            self.page = None
            self.browser = None
    
    async def navigate_to_url(self, url: str, timeout: int = 30000) -> bool:
        """Navigate to URL with error handling."""
        try:
            # Make sure browser is initialized
            if not self.browser or not self.page:
                await self.setup_browser()
                
            print(f"Navigating to: {url}")
            await self.page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            await self.random_delay()
            
            # Take screenshot for debugging
            try:
                import os
                os.makedirs("debug_screenshots", exist_ok=True)
                screenshot_path = f"debug_screenshots/page_{url.split('/')[-1][:20]}.png"
                await self.page.screenshot(path=screenshot_path)
                print(f"Screenshot saved to {screenshot_path}")
            except Exception as e:
                print(f"Failed to save screenshot: {e}")
                
            # Log page title and URL
            title = await self.page.title()
            current_url = self.page.url
            print(f"Page loaded: '{title}' at URL: {current_url}")
            
            return True
        except Exception as e:
            print(f"Failed to navigate to {url}: {e}")
            return False
    
    async def random_delay(self, min_delay: float = None, max_delay: float = None):
        """Add random delay between requests."""
        if min_delay is None:
            min_delay = self.delay
        if max_delay is None:
            max_delay = self.delay * 2
            
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to appear."""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception:
            return False
    
    async def scroll_to_load_content(self, max_scrolls: int = 10):
        """Scroll page to load dynamic content."""
        for i in range(max_scrolls):
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)
            
            # Check if new content loaded
            new_height = await self.page.evaluate('document.body.scrollHeight')
            if i > 0 and new_height == getattr(self, '_last_height', 0):
                break
            self._last_height = new_height
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable() or char.isspace())
        return text
    
    def parse_rating(self, rating_text: str) -> Optional[float]:
        """Parse rating from text."""
        if not rating_text:
            return None
            
        # Extract number from rating text
        match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None
    
    def parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from various text formats."""
        if not date_text:
            return None
            
        # Common date patterns
        patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\w+)\s+(\d{1,2}),\s+(\d{4})',  # Month DD, YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_text)
            if match:
                try:
                    # This is a simplified parser - in production, use dateutil
                    groups = match.groups()
                    if len(groups) == 3:
                        # Assume YYYY-MM-DD format for now
                        year, month, day = groups[0], groups[1], groups[2]
                        return datetime(int(year), int(month), int(day))
                except (ValueError, IndexError):
                    continue
        
        return None
    
    @abstractmethod
    async def scrape_reviews(self, url: str, max_reviews: int = 100) -> List[Dict[str, Any]]:
        """Scrape reviews from the given URL."""
        pass
    
    @abstractmethod
    def can_handle_url(self, url: str) -> bool:
        """Check if this scraper can handle the given URL."""
        pass