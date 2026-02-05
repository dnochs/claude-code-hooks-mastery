"""
Base utility functions for the NEFCO scraper.

This module provides the core building blocks that other scraper modules use:
    - Making HTTP requests with proper headers
    - Adding delays between requests (to be polite to servers)
    - Saving data to CSV files
    - Reading data from CSV files

These functions are designed to be simple, reusable, and beginner-friendly.
"""

import csv
import os
import time
from pathlib import Path

import requests
import cloudscraper
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# Import our configuration settings
from . import config


# =============================================================================
# HTTP REQUEST FUNCTIONS
# =============================================================================

def get_headers():
    """
    Return a dictionary of HTTP headers that make our requests look like
    they're coming from a regular web browser.

    Why do we need this?
    - Websites can see information about who/what is making requests
    - By default, Python's requests library identifies itself as a script
    - Many websites block requests that don't look like they're from a browser
    - These headers mimic what a Chrome browser would send

    Returns:
        dict: A dictionary of HTTP headers

    Example:
        headers = get_headers()
        response = requests.get(url, headers=headers)
    """
    return {
        # User-Agent tells the server what browser we're using
        # This string says we're Chrome on Windows 10
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        # Accept tells the server what types of content we can handle
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/webp,*/*;q=0.8"
        ),
        # Accept-Language tells the server our preferred language
        "Accept-Language": "en-US,en;q=0.5",
        # Accept-Encoding tells the server what compression we support
        "Accept-Encoding": "gzip, deflate, br",
        # Connection: keep-alive means reuse the connection if possible
        "Connection": "keep-alive",
    }


def delay_between_requests():
    """
    Pause execution for the configured delay time.

    Why do we need delays?
    - Being polite: Rapid-fire requests can overwhelm a server
    - Avoiding blocks: Many sites detect and block "bot-like" behavior
    - Rate limiting: Some sites have limits on requests per minute
    - Mimicking humans: Real users don't click links instantly

    The delay duration is set in config.REQUEST_DELAY (default: 5 seconds)

    Example:
        delay_between_requests()  # Waits 5 seconds
        response = fetch_page(url)  # Then makes the request
    """
    delay_seconds = config.REQUEST_DELAY
    print(f"  Waiting {delay_seconds} seconds before next request...")
    time.sleep(delay_seconds)


def fetch_page(url):
    """
    Fetch a web page and return the response.

    This function:
    1. Waits the configured delay time (to be polite)
    2. Makes the HTTP GET request with browser-like headers
    3. Returns the response object if successful
    4. Returns None and prints an error if something goes wrong

    Args:
        url (str): The full URL of the page to fetch

    Returns:
        requests.Response or None: The response object if successful,
                                   None if an error occurred

    Example:
        response = fetch_page("https://www.example.com")
        if response:
            html = response.text
            print(f"Got {len(html)} characters of HTML")
        else:
            print("Failed to fetch page")
    """
    # First, wait the polite delay
    delay_between_requests()

    print(f"  Fetching: {url}")

    try:
        # Make the request with our browser-like headers
        response = requests.get(url, headers=get_headers(), timeout=30)

        # Check if the request was successful (status code 200-299)
        # This will raise an exception if the status code indicates an error
        response.raise_for_status()

        print(f"  Success! Status code: {response.status_code}")
        return response

    except requests.exceptions.Timeout:
        # The server took too long to respond
        print(f"  ERROR: Request timed out for {url}")
        return None

    except requests.exceptions.ConnectionError:
        # Could not connect to the server
        print(f"  ERROR: Could not connect to {url}")
        return None

    except requests.exceptions.HTTPError as e:
        # Server returned an error status code (like 403 Forbidden or 404 Not Found)
        print(f"  ERROR: HTTP error for {url}: {e}")
        return None

    except requests.exceptions.RequestException as e:
        # Catch-all for any other request-related errors
        print(f"  ERROR: Request failed for {url}: {e}")
        return None


def fetch_page_playwright(url, wait_for_selector=None):
    """
    Fetch a web page using Playwright (real browser automation).

    This function uses a real Chromium browser to fetch pages, which can bypass
    simple bot detection that blocks regular HTTP requests.

    Why use Playwright instead of requests?
    - Some websites block requests that don't come from real browsers
    - Playwright runs an actual browser, so the website sees a real visitor
    - It can handle JavaScript-rendered content
    - It can wait for dynamic content to load

    Args:
        url (str): The full URL of the page to fetch
        wait_for_selector (str, optional): CSS selector to wait for before returning.
                                           Useful for pages that load content dynamically.

    Returns:
        str or None: The HTML content of the page if successful, None if an error occurred

    Example:
        html = fetch_page_playwright("https://www.example.com")
        if html:
            print(f"Got {len(html)} characters of HTML")
        else:
            print("Failed to fetch page")
    """
    # First, wait the polite delay
    delay_between_requests()

    print(f"  Fetching with Playwright: {url}")

    try:
        with sync_playwright() as p:
            # Launch Chromium with stealth mode
            # Using headless=False can help bypass some detection
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ]
            )

            # Create a new browser context with realistic settings
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                ignore_https_errors=True,
            )

            # Create a new page
            page = context.new_page()

            # Apply stealth patches to avoid bot detection
            # This modifies browser fingerprints to look more human
            stealth = Stealth()
            stealth.apply_stealth_sync(page)

            # Navigate to the URL with a timeout
            page.goto(url, timeout=60000, wait_until="networkidle")

            # Wait for Cloudflare challenge to complete (if present)
            # Cloudflare pages typically redirect after solving the challenge
            # We wait for the page to stabilize
            page.wait_for_load_state("networkidle")

            # Additional wait to let any JavaScript finish executing
            page.wait_for_timeout(3000)

            # If a selector was provided, wait for it to appear
            if wait_for_selector:
                page.wait_for_selector(wait_for_selector, timeout=10000)

            # Get the full HTML content
            html = page.content()

            # Clean up
            browser.close()

            print(f"  Success! Got {len(html)} characters of HTML")
            return html

    except Exception as e:
        print(f"  ERROR: Playwright failed for {url}: {e}")
        return None


def fetch_page_cloudscraper(url):
    """
    Fetch a web page using cloudscraper (designed to bypass Cloudflare).

    Cloudscraper is specifically built to handle Cloudflare's anti-bot protection.
    It solves JavaScript challenges automatically.

    Args:
        url (str): The full URL of the page to fetch

    Returns:
        str or None: The HTML content of the page if successful, None if an error occurred
    """
    # First, wait the polite delay
    delay_between_requests()

    print(f"  Fetching with cloudscraper: {url}")

    try:
        # Create a cloudscraper session
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )

        # Make the request
        response = scraper.get(url, timeout=30)

        # Check if successful
        response.raise_for_status()

        print(f"  Success! Got {len(response.text)} characters of HTML")
        return response.text

    except Exception as e:
        print(f"  ERROR: cloudscraper failed for {url}: {e}")
        return None


# =============================================================================
# CSV FILE FUNCTIONS
# =============================================================================

def save_to_csv(data, filepath):
    """
    Save a list of dictionaries to a CSV file.

    Each dictionary in the list becomes one row in the CSV.
    The dictionary keys become the column headers.

    Args:
        data (list): A list of dictionaries with the same keys
                     Example: [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        filepath (str or Path): Where to save the CSV file

    Returns:
        bool: True if save was successful, False if an error occurred

    Example:
        categories = [
            {"name": "Electrical", "url": "https://..."},
            {"name": "Plumbing", "url": "https://..."},
        ]
        save_to_csv(categories, "output/categories.csv")
    """
    # Handle empty data
    if not data:
        print("  WARNING: No data to save (empty list)")
        return False

    # Convert to Path object for easier handling
    filepath = Path(filepath)

    # Create the parent directory if it doesn't exist
    # For example, if filepath is "output/categories.csv", this creates "output/"
    filepath.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Open file with UTF-8 encoding and newline='' (required for CSV on Windows)
        with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            # Get column names from the keys of the first dictionary
            fieldnames = list(data[0].keys())

            # Create a DictWriter that will write our dictionaries as rows
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the header row (column names)
            writer.writeheader()

            # Write all the data rows
            writer.writerows(data)

        print(f"  Saved {len(data)} rows to: {filepath}")
        return True

    except IOError as e:
        print(f"  ERROR: Could not write to file {filepath}: {e}")
        return False
    except Exception as e:
        print(f"  ERROR: Unexpected error saving CSV: {e}")
        return False


def read_csv(filepath):
    """
    Read a CSV file and return its contents as a list of dictionaries.

    Each row in the CSV becomes one dictionary.
    The column headers become the dictionary keys.

    Args:
        filepath (str or Path): Path to the CSV file to read

    Returns:
        list: A list of dictionaries, one per row in the CSV.
              Returns an empty list if the file doesn't exist or can't be read.

    Example:
        categories = read_csv("output/categories.csv")
        for category in categories:
            print(f"Category: {category['name']}")
    """
    filepath = Path(filepath)

    # Check if file exists
    if not filepath.exists():
        print(f"  WARNING: File not found: {filepath}")
        return []

    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as csvfile:
            # DictReader automatically uses the first row as column headers
            reader = csv.DictReader(csvfile)

            # Convert the reader to a list of dictionaries
            data = list(reader)

        print(f"  Read {len(data)} rows from: {filepath}")
        return data

    except IOError as e:
        print(f"  ERROR: Could not read file {filepath}: {e}")
        return []
    except Exception as e:
        print(f"  ERROR: Unexpected error reading CSV: {e}")
        return []
