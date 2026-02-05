"""
Generic category scraper for the NEFCO scraper system.

This module scrapes products from a specific category page.
It can work with any category URL and extracts product information.

Usage:
    python scrape_category.py --name "Electrical" --url "https://www.nefco.com/catalog/..."
    python scrape_category.py --name "Plumbing" --url "https://..." --output custom_output/

In DEMO_MODE, this returns sample product data without hitting the real website.
"""

import argparse
import os
from pathlib import Path

# BeautifulSoup is used to parse HTML and extract data
from bs4 import BeautifulSoup

# Import our local configuration and base utilities
from . import config
from . import base


# =============================================================================
# DEMO PRODUCT DATA
# =============================================================================
# When DEMO_MODE is True, we return these sample products instead of scraping.
# This allows us to develop and test without making real requests.
#
# The dictionary is keyed by category slug (the URL-friendly version of the name).
# Each category has a list of product names that are typical for that trade.

DEMO_PRODUCTS = {
    "electrical": [
        "Wire Connectors",
        "Junction Boxes",
        "Conduit Fittings",
        "Cable Ties",
        "Electrical Tape",
    ],
    "plumbing": [
        "Pipe Fittings",
        "Valves",
        "Drain Parts",
        "Water Heater Accessories",
        "PVC Cement",
    ],
    "hvac": [
        "Duct Tape",
        "Refrigerant",
        "Thermostats",
        "Air Filters",
        "Insulation",
    ],
    "fire-protection": [
        "Sprinkler Heads",
        "Fire Extinguishers",
        "Smoke Detectors",
        "Fire Alarm Panels",
        "Standpipe Equipment",
    ],
    "mechanical": [
        "Bearings",
        "Seals",
        "Gaskets",
        "Fasteners",
        "Lubricants",
    ],
    "data-communications": [
        "Ethernet Cables",
        "Patch Panels",
        "Wall Plates",
        "Cable Management",
        "Network Racks",
    ],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_category_slug(category_name):
    """
    Convert a category name to a URL-friendly slug.

    Example:
        "Fire Protection" -> "fire-protection"
        "Data/Communications" -> "data-communications"

    Args:
        category_name (str): The human-readable category name

    Returns:
        str: A lowercase, hyphenated version suitable for filenames/URLs
    """
    # Convert to lowercase
    slug = category_name.lower()
    # Replace slashes and spaces with hyphens
    slug = slug.replace("/", "-").replace(" ", "-")
    return slug


# =============================================================================
# MAIN SCRAPING FUNCTION
# =============================================================================

def scrape_category(category_name, category_url):
    """
    Scrape products from a single category page.

    In DEMO_MODE, this returns sample product data.
    Otherwise, it fetches the real page and parses it.

    Args:
        category_name (str): The name of the category (e.g., "Electrical")
        category_url (str): The full URL of the category page

    Returns:
        list: A list of product dictionaries, each containing:
              - title: The product name
              - category: Which category this product belongs to
              - url: Link to the product page (or placeholder in demo mode)
    """
    print(f"Scraping category: {category_name}...")

    # Get the slug for looking up demo data
    category_slug = get_category_slug(category_name)

    # List to store all the products we find
    products = []

    # -------------------------------------------------------------------------
    # DEMO MODE: Return sample data without hitting the real website
    # -------------------------------------------------------------------------
    if config.DEMO_MODE:
        print("  [DEMO MODE] Using sample product data...")

        # Add a polite delay even in demo mode (good practice for learning)
        # This simulates what would happen with real requests
        base.delay_between_requests()

        # Look up demo products for this category
        # If the category isn't in our demo data, use an empty list
        demo_product_names = DEMO_PRODUCTS.get(category_slug, [])

        if not demo_product_names:
            print(f"  WARNING: No demo data for category slug '{category_slug}'")
            print(f"  Available slugs: {list(DEMO_PRODUCTS.keys())}")

        # Create product dictionaries from the demo data
        for product_name in demo_product_names:
            product = {
                "title": product_name,
                "category": category_name,
                "url": f"{config.BASE_URL}/catalog/product/{category_slug}/{product_name.lower().replace(' ', '-')}",
            }
            products.append(product)

        print(f"  [DEMO MODE] Generated {len(products)} sample products")
        return products

    # -------------------------------------------------------------------------
    # LIVE MODE: Actually scrape the website
    # -------------------------------------------------------------------------
    print("  [LIVE MODE] Fetching real page with cloudscraper...")

    # Use cloudscraper to fetch the page (designed for Cloudflare bypass)
    html_content = base.fetch_page_cloudscraper(category_url)

    # Check if we got a valid response
    if html_content is None:
        print(f"  ERROR: Failed to fetch category page: {category_url}")
        return products  # Return empty list

    # Parse the HTML with BeautifulSoup
    # 'html.parser' is Python's built-in HTML parser (no extra install needed)
    soup = BeautifulSoup(html_content, 'html.parser')

    # -------------------------------------------------------------------------
    # NOTE: The selectors below are placeholders!
    #
    # To make this work with the real NEFCO site, you would need to:
    # 1. Inspect the actual HTML structure of their category pages
    # 2. Find the CSS selectors that match their product listings
    # 3. Update the code below to use those selectors
    #
    # For now, this is a generic approach that might work with some sites.
    # -------------------------------------------------------------------------

    # Try to find product elements - this is a common pattern
    # Many e-commerce sites use class names containing 'product' or 'item'
    product_elements = soup.select('.product-item, .product-card, .product')

    print(f"  Found {len(product_elements)} product elements on page")

    for element in product_elements:
        # Try to extract the product title
        # Common patterns: h2, h3, .product-title, .product-name
        title_element = element.select_one('h2, h3, .product-title, .product-name, .title')

        if title_element:
            product_title = title_element.get_text(strip=True)
        else:
            # Fallback: try to get any text from the element
            product_title = element.get_text(strip=True)[:50]  # Limit to 50 chars

        # Try to extract the product URL
        link_element = element.select_one('a')
        if link_element and link_element.get('href'):
            product_url = link_element.get('href')
            # Make sure it's a full URL (not relative)
            if product_url.startswith('/'):
                product_url = config.BASE_URL + product_url
        else:
            product_url = "URL not found"

        # Create the product dictionary and add to our list
        product = {
            "title": product_title,
            "category": category_name,
            "url": product_url,
        }
        products.append(product)

    print(f"  Extracted {len(products)} products from {category_name}")
    return products


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main(category_name, category_url, output_dir="output"):
    """
    Main entry point for scraping a category and saving results.

    This function:
    1. Calls scrape_category() to get the products
    2. Generates an appropriate output filename
    3. Saves the results to a CSV file

    Args:
        category_name (str): The name of the category to scrape
        category_url (str): The URL of the category page
        output_dir (str): Directory to save the output file (default: "output")
    """
    print(f"\n{'='*60}")
    print(f"NEFCO Category Scraper")
    print(f"{'='*60}")
    print(f"Category: {category_name}")
    print(f"URL: {category_url}")
    print(f"Output directory: {output_dir}")
    print(f"Demo mode: {config.DEMO_MODE}")
    print(f"{'='*60}\n")

    # Step 1: Scrape the category to get products
    products = scrape_category(category_name, category_url)

    # Step 2: Generate the output filename
    # Convert category name to a slug for the filename
    category_slug = get_category_slug(category_name)
    output_filename = f"{category_slug}_products.csv"
    output_path = Path(output_dir) / output_filename

    # Step 3: Save the products to CSV
    if products:
        success = base.save_to_csv(products, output_path)

        if success:
            print(f"\nSaved {len(products)} products to {output_path}")
        else:
            print(f"\nERROR: Failed to save products to {output_path}")
    else:
        print(f"\nWARNING: No products found for category '{category_name}'")
        print("No CSV file was created.")

    print(f"\n{'='*60}")
    print("Scraping complete!")
    print(f"{'='*60}\n")

    return products


# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

if __name__ == "__main__":
    # Set up argument parser
    # This lets users run the script from the command line with options
    parser = argparse.ArgumentParser(
        description="Scrape products from a NEFCO category page.",
        epilog="Example: python scrape_category.py --name 'Electrical' --url 'https://www.nefco.com/catalog/...'",
    )

    # Required arguments
    parser.add_argument(
        "--name",
        required=True,
        help="The name of the category (e.g., 'Electrical', 'Plumbing')",
    )

    parser.add_argument(
        "--url",
        required=True,
        help="The full URL of the category page to scrape",
    )

    # Optional arguments
    parser.add_argument(
        "--output",
        default="output",
        help="Directory to save the output CSV file (default: output/)",
    )

    # Parse the command line arguments
    args = parser.parse_args()

    # Run the main function with the parsed arguments
    main(
        category_name=args.name,
        category_url=args.url,
        output_dir=args.output,
    )
