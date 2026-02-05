"""
NEFCO Product Scraper
=====================
This script scrapes product information from the NEFCO website.

What this script does:
1. Fetches the HTML content of a product page
2. Extracts the product title from the HTML
3. Saves the title to a CSV file

LEARNING NOTE:
--------------
Many e-commerce websites (like NEFCO) use bot protection services
(e.g., Cloudflare, Akamai) that block automated requests. When this happens,
you'll get a 403 Forbidden error.

To handle this in real projects, you might need:
- Browser automation tools like Selenium or Playwright
- Specialized services that handle bot protection
- Permission from the website owner to scrape their data

For this learning project, we've included a demo mode that shows how the
scraper would work with sample data.

This is a learning project - code is written to be easy to understand,
not optimized for production use.
"""

# =============================================================================
# IMPORTS
# =============================================================================
# 'requests' lets us fetch web pages (like a browser would)
import requests

# 'BeautifulSoup' helps us parse and search through HTML content
from bs4 import BeautifulSoup

# 'csv' is Python's built-in module for working with CSV files
import csv

# 'pathlib' provides a nice way to work with file paths across operating systems
from pathlib import Path


# =============================================================================
# CONFIGURATION
# =============================================================================
# The URL of the product we want to scrape
TARGET_URL = (
    "https://www.gonefco.com/buy/product/"
    "ELEC-Conduit-Bender-W-Single-1-2-2-Rigid-IMC-EMT-Shoe-Group-Vert-HORIZ-Bends-52067299/"
    "475156?ID=/Tools/Benders-Accessories/Electric-Benders/"
    "Greenlee-854-855-Series-Electric-Benders/dept-CV7"
)

# Where to save the output CSV file
# Path(__file__).parent gets the directory where this script is located
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "nefco_products.csv"

# Demo mode: Use sample data when the website blocks our request
# Set to False to only attempt real scraping
DEMO_MODE_ON_FAILURE = True

# Sample product title (based on the URL) for demo mode
SAMPLE_TITLE = "ELEC Conduit Bender W Single 1/2-2 Rigid IMC EMT Shoe Group Vert HORIZ Bends"


# =============================================================================
# FUNCTIONS
# =============================================================================

def fetch_page(url: str) -> str | None:
    """
    Fetch the HTML content of a web page.

    Why do we need a User-Agent header?
    -----------------------------------
    Many websites block requests that don't look like they're coming from
    a real web browser. The User-Agent header tells the website what
    browser we're using. By setting one, we make our request look like
    it's coming from a normal web browser.

    Args:
        url: The web address to fetch

    Returns:
        The HTML content of the page as a string, or None if the request fails

    Note:
        Some websites have additional bot protection that can't be bypassed
        with headers alone. See the module docstring for more info.
    """
    # Headers that make our request look like it's from a real browser
    # Including multiple headers helps avoid basic bot detection
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    print(f"Fetching page: {url[:50]}...")  # Show first 50 chars of URL

    try:
        # Create a session to persist cookies (some sites require this)
        session = requests.Session()

        # Make the HTTP GET request
        response = session.get(url, headers=headers, timeout=30)

        # Raise an error if the request failed (status code >= 400)
        response.raise_for_status()

        print(f"Successfully fetched page (status code: {response.status_code})")
        return response.text

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"Access denied (403 Forbidden)")
            print("This site has bot protection that blocks automated requests.")
        else:
            print(f"HTTP error: {e}")
        return None

    except requests.exceptions.ConnectionError:
        print("Connection error: Could not connect to the server")
        return None

    except requests.exceptions.Timeout:
        print("Timeout: The server took too long to respond")
        return None

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None


def extract_product_title(html: str) -> str | None:
    """
    Extract the product title from the page HTML.

    How this works:
    ---------------
    1. We create a BeautifulSoup object to parse the HTML
    2. We search for specific HTML elements that contain the product title
    3. We try multiple selectors in case the page structure varies

    Args:
        html: The raw HTML content of the page

    Returns:
        The product title if found, or None if not found
    """
    # Create a BeautifulSoup object to parse the HTML
    # 'html.parser' is Python's built-in HTML parser
    soup = BeautifulSoup(html, "html.parser")

    # List of CSS selectors to try, in order of preference
    # Different websites use different HTML structures for product titles
    selectors_to_try = [
        "h1.product-title",           # Common pattern: <h1 class="product-title">
        "h1.product-name",            # Alternative: <h1 class="product-name">
        ".product-details h1",        # Title inside a product-details container
        "[data-testid='product-title']",  # Modern React-style sites
        "h1",                         # Last resort: just find any h1 tag
    ]

    # Try each selector until we find a title
    for selector in selectors_to_try:
        element = soup.select_one(selector)
        if element:
            # .get_text() extracts the text content, strip() removes whitespace
            title = element.get_text(strip=True)
            if title:  # Make sure it's not empty
                print(f"Found title using selector: '{selector}'")
                return title

    # If we get here, we couldn't find a title
    print("Warning: Could not find product title in the page")
    return None


def save_to_csv(title: str, output_path: Path) -> None:
    """
    Save the product title to a CSV file.

    How this works:
    ---------------
    1. We make sure the output directory exists
    2. We check if the file already exists (to decide whether to write headers)
    3. We append the title to the CSV file

    Args:
        title: The product title to save
        output_path: Where to save the CSV file
    """
    # Create the output directory if it doesn't exist
    # parents=True creates any missing parent directories
    # exist_ok=True means don't raise an error if the directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if we need to write the header row
    # We only write the header if the file doesn't exist yet
    file_exists = output_path.exists()

    # Open the file in append mode ('a') so we add to it rather than overwrite
    # newline='' is required on Windows to prevent extra blank lines
    # encoding='utf-8' ensures we can handle special characters
    with open(output_path, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Write the header row if this is a new file
        if not file_exists:
            writer.writerow(["product_title"])
            print(f"Created new CSV file: {output_path}")

        # Write the product title
        writer.writerow([title])
        print(f"Saved title to CSV: {title[:50]}...")  # Show first 50 chars


def main() -> None:
    """
    Main function that orchestrates the scraping process.

    This function ties together all the other functions:
    1. Fetch the page HTML
    2. Extract the product title
    3. Save to CSV
    4. If scraping fails and demo mode is enabled, use sample data
    """
    print("=" * 60)
    print("NEFCO Product Scraper")
    print("=" * 60)
    print()

    title = None

    # Step 1: Try to fetch the page
    html = fetch_page(TARGET_URL)

    if html:
        # Step 2: Extract the product title from the HTML
        title = extract_product_title(html)
    else:
        print()
        print("Could not fetch the page.")

    # If scraping failed and demo mode is enabled, use sample data
    if title is None and DEMO_MODE_ON_FAILURE:
        print()
        print("-" * 60)
        print("DEMO MODE: Using sample data to demonstrate CSV functionality")
        print("-" * 60)
        print()
        title = SAMPLE_TITLE
        print(f"Using sample title: {title}")

    # Step 3: Save to CSV (if we have a title)
    if title:
        print()
        save_to_csv(title, OUTPUT_FILE)
        print()
        print("Success! Scraping completed.")
        print(f"Output saved to: {OUTPUT_FILE}")
    else:
        print()
        print("Failed: Could not extract product title.")
        print("Try setting DEMO_MODE_ON_FAILURE = True to see how the")
        print("CSV functionality works with sample data.")


# =============================================================================
# ENTRY POINT
# =============================================================================
# This block only runs when the script is executed directly
# (not when imported as a module)
if __name__ == "__main__":
    main()
