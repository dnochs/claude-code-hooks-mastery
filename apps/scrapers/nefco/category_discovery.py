"""
Category Discovery Module for the NEFCO Scraper.

This module is responsible for finding all the categories (trades) on the NEFCO
website. Think of it as the first step in scraping - before we can get products,
we need to know what categories exist.

What this module does:
    1. Discovers category pages (either from demo data or by scraping the site)
    2. Saves the discovered categories to a JSON file for later use

Key concepts explained:
    - BeautifulSoup: A Python library that makes it easy to extract data from HTML.
      It turns messy HTML into a tree structure you can search through.
    - JSON: A file format for storing structured data (like a list of categories).
      It's human-readable and easy for Python to work with.
"""

import json
import os
from pathlib import Path

# BeautifulSoup is a library that parses HTML and makes it easy to extract data.
# We import it from the 'bs4' package (BeautifulSoup version 4).
# Think of it like a tool that reads HTML and lets you ask questions like
# "find all the links" or "find the element with class 'category-name'".
from bs4 import BeautifulSoup

# Import our local modules
# The '.' means "from the same package/folder"
from . import config  # Our configuration settings (URLs, demo mode, etc.)
from . import base    # Our utility functions (fetch_page, etc.)


# =============================================================================
# CATEGORY DISCOVERY FUNCTIONS
# =============================================================================

def discover_categories():
    """
    Discover all trade categories from the NEFCO website.

    This function works in two modes:

    1. DEMO MODE (config.DEMO_MODE = True):
       - Returns pre-defined demo categories from config.py
       - Use this when developing/testing to avoid hitting the real website
       - Helpful because the real NEFCO site blocks automated requests

    2. LIVE MODE (config.DEMO_MODE = False):
       - Actually fetches the category page from NEFCO
       - Parses the HTML to find category links
       - Returns the discovered categories

    Returns:
        list: A list of category dictionaries, each containing:
              - name (str): Human-readable category name (e.g., "Electrical")
              - slug (str): URL-friendly name (e.g., "electrical")
              - url (str): Full URL to the category page

    Example:
        categories = discover_categories()
        for cat in categories:
            print(f"Found: {cat['name']} at {cat['url']}")
    """
    print("\n" + "=" * 60)
    print("CATEGORY DISCOVERY")
    print("=" * 60)

    # Check if we're in demo mode
    if config.DEMO_MODE:
        print("\n[DEMO MODE] Using pre-defined demo categories.")
        print("(Set DEMO_MODE = False in config.py to scrape the real site)")
        return config.DEMO_CATEGORIES

    # --- LIVE MODE: Actually scrape the website ---
    print(f"\n[LIVE MODE] Fetching categories from: {config.TARGET_CATEGORY_URL}")

    # Use cloudscraper to fetch the HTML (designed for Cloudflare bypass)
    html_content = base.fetch_page_cloudscraper(config.TARGET_CATEGORY_URL)

    # Check if the fetch was successful
    if html_content is None:
        print("ERROR: Could not fetch the category page.")
        print("Falling back to demo categories...")
        return config.DEMO_CATEGORIES

    # --- Parse the HTML with BeautifulSoup ---
    # BeautifulSoup takes two arguments:
    #   1. The HTML content (as a string)
    #   2. The parser to use ('html.parser' is Python's built-in HTML parser)
    soup = BeautifulSoup(html_content, 'html.parser')

    # Now we need to find the category links in the HTML.
    # This is where web scraping gets tricky - you need to inspect the
    # actual HTML structure to know what to look for.
    #
    # Common patterns to look for:
    #   - Links (<a> tags) inside a navigation menu
    #   - Links with specific CSS classes like "category-link"
    #   - Links inside a container with an ID like "categories"
    #
    # We'll try to find links that look like they're subcategories of
    # the "specialty-by-trade" section.

    categories = []

    # Look for all links (<a> tags) on the page
    all_links = soup.find_all('a', href=True)

    # Filter to find links that are likely subcategories
    for link in all_links:
        href = link.get('href', '')

        # We're looking for links under /catalog/specialty-by-trade/
        # but NOT the parent page itself
        if '/catalog/specialty-by-trade/' in href and href != '/catalog/specialty-by-trade':
            # Extract the category slug from the URL
            # Example: "/catalog/specialty-by-trade/electrical" -> "electrical"
            slug = href.split('/')[-1]

            # Skip empty slugs or query parameters
            if not slug or '?' in slug:
                continue

            # Get the link text (the visible name)
            name = link.get_text(strip=True)

            # Skip if no name found
            if not name:
                continue

            # Build the full URL
            # If the href is a relative path (starts with /), prepend the base URL
            if href.startswith('/'):
                full_url = config.BASE_URL + href
            else:
                full_url = href

            # Create the category dictionary
            category = {
                "name": name,
                "slug": slug,
                "url": full_url
            }

            # Avoid duplicates (check by slug)
            if not any(c['slug'] == slug for c in categories):
                categories.append(category)
                print(f"  Found category: {name}")

    # Report results
    if categories:
        print(f"\nDiscovered {len(categories)} categories.")
    else:
        print("\nNo categories found in HTML. Falling back to demo categories.")
        return config.DEMO_CATEGORIES

    return categories


# =============================================================================
# FILE SAVING FUNCTIONS
# =============================================================================

def save_categories(categories, output_dir):
    """
    Save the discovered categories to a JSON file.

    JSON (JavaScript Object Notation) is a standard format for storing data.
    It's easy for humans to read and easy for Python to write/read.

    Args:
        categories (list): The list of category dictionaries to save
        output_dir (str or Path): Directory where to save the file.
                                  The file will be named 'categories.json'

    Returns:
        Path: The full path to the saved file, or None if save failed

    Example:
        categories = discover_categories()
        filepath = save_categories(categories, "output")
        # Saves to: output/categories.json
    """
    # Convert to Path object for easier handling
    output_dir = Path(output_dir)

    # Create the output directory if it doesn't exist
    # parents=True means create parent directories too if needed
    # exist_ok=True means don't error if directory already exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build the full file path
    filepath = output_dir / "categories.json"

    print(f"\nSaving categories to: {filepath}")

    try:
        # Open the file for writing with UTF-8 encoding
        # UTF-8 ensures special characters are handled correctly
        with open(filepath, 'w', encoding='utf-8') as f:
            # json.dump() writes Python data to a JSON file
            # Arguments:
            #   - categories: the Python data to write
            #   - f: the file object to write to
            #   - indent=2: format with 2-space indentation (makes it readable)
            #   - ensure_ascii=False: allow non-ASCII characters (like accents)
            json.dump(categories, f, indent=2, ensure_ascii=False)

        print(f"Successfully saved {len(categories)} categories.")
        return filepath

    except IOError as e:
        print(f"ERROR: Could not write to file {filepath}: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error saving categories: {e}")
        return None


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

# This block only runs when you execute this file directly:
#   python -m apps.scrapers.nefco.category_discovery
#
# It does NOT run when you import this module from another file:
#   from apps.scrapers.nefco import category_discovery

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("NEFCO CATEGORY DISCOVERY SCRIPT")
    print("=" * 60)

    # Step 1: Discover categories
    categories = discover_categories()

    # Step 2: Display what we found
    print("\n" + "-" * 40)
    print("CATEGORIES FOUND:")
    print("-" * 40)

    for i, category in enumerate(categories, start=1):
        print(f"  {i}. {category['name']}")
        print(f"     Slug: {category['slug']}")
        print(f"     URL:  {category['url']}")
        print()

    # Step 3: Save to output directory
    # We save to 'output' directory relative to the project root
    output_dir = Path(__file__).parent.parent.parent.parent / "output"
    saved_path = save_categories(categories, output_dir)

    # Final summary
    print("\n" + "=" * 60)
    print("DISCOVERY COMPLETE")
    print("=" * 60)
    if saved_path:
        print(f"Categories saved to: {saved_path}")
        print(f"Total categories: {len(categories)}")
    else:
        print("WARNING: Categories were discovered but could not be saved.")
    print()
