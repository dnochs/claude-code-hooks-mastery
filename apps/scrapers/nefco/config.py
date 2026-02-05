"""
Configuration settings for the NEFCO category scraper.

This file contains all the settings that control how the scraper behaves.
By keeping configuration separate from code, it's easy to adjust settings
without changing the main logic.
"""

# =============================================================================
# URL SETTINGS
# =============================================================================

# The base URL for NEFCO's website (no trailing slash)
# The correct website is gonefco.com (not nefco.com which is a different company)
BASE_URL = "https://www.gonefco.com"

# The specific page we want to scrape - the "Specialty by Trade" category page
TARGET_CATEGORY_URL = "https://www.gonefco.com/catalog/specialty-by-trade"


# =============================================================================
# REQUEST SETTINGS
# =============================================================================

# How many seconds to wait between requests to the server.
# This is important because:
#   1. It's polite - we don't want to overwhelm their server
#   2. It helps avoid being blocked for making too many requests too fast
#   3. It mimics how a real human would browse (humans don't click instantly)
REQUEST_DELAY = 5  # seconds


# =============================================================================
# DEMO MODE SETTINGS
# =============================================================================

# When True, use demo data instead of making real requests to the website.
# This is useful because:
#   1. NEFCO's website blocks automated requests
#   2. We can develop and test without hitting the real server
#   3. We can learn the scraping concepts without getting blocked
DEMO_MODE = True

# Demo category data - these represent typical trade categories from NEFCO
# Each category has:
#   - name: Human-readable category name
#   - slug: URL-friendly version (lowercase, hyphens instead of spaces)
#   - url: Full URL to the category page
DEMO_CATEGORIES = [
    {
        "name": "Electrical",
        "slug": "electrical",
        "url": f"{BASE_URL}/catalog/specialty-by-trade/electrical"
    },
    {
        "name": "Plumbing",
        "slug": "plumbing",
        "url": f"{BASE_URL}/catalog/specialty-by-trade/plumbing"
    },
    {
        "name": "HVAC",
        "slug": "hvac",
        "url": f"{BASE_URL}/catalog/specialty-by-trade/hvac"
    },
    {
        "name": "Fire Protection",
        "slug": "fire-protection",
        "url": f"{BASE_URL}/catalog/specialty-by-trade/fire-protection"
    },
    {
        "name": "Mechanical",
        "slug": "mechanical",
        "url": f"{BASE_URL}/catalog/specialty-by-trade/mechanical"
    },
    {
        "name": "Data/Communications",
        "slug": "data-communications",
        "url": f"{BASE_URL}/catalog/specialty-by-trade/data-communications"
    },
]
