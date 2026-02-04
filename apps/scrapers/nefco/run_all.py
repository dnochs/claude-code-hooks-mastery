"""
Pipeline Orchestrator - Runs the entire NEFCO scraper workflow.

This script coordinates all steps of the scraping process:
    1. Discovery: Find all available categories on the NEFCO website
    2. Scraping: Scrape products from each category (in parallel or sequentially)
    3. Aggregation: Combine all category CSV files into a master file

Usage:
    python -m apps.scrapers.nefco.run_all

Why use an orchestrator?
    - Single command to run the entire pipeline
    - Handles errors gracefully (one failing category doesn't stop others)
    - Tracks timing so you know how long each step takes
    - Provides clear progress messages throughout
"""

import subprocess
import sys
import time
from pathlib import Path
import json

# Import our local modules
# The '.' means "from the same package/folder"
from . import config
from . import category_discovery
from . import aggregator


# =============================================================================
# STEP 1: CATEGORY DISCOVERY
# =============================================================================

def run_discovery(output_dir):
    """
    Run the category discovery step.

    This finds all trade categories available on the NEFCO website.
    In DEMO_MODE, it returns pre-defined demo categories.

    Args:
        output_dir (Path): Directory where categories.json will be saved

    Returns:
        list: List of category dictionaries with name, slug, and url
    """
    print("\n" + "=" * 60)
    print("Step 1: Discovering categories...")
    print("=" * 60)

    # Call the discovery function from category_discovery module
    categories = category_discovery.discover_categories()

    # Save categories to JSON file for reference
    category_discovery.save_categories(categories, output_dir)

    # Print summary
    print(f"\nFound {len(categories)} categories:")
    for cat in categories:
        print(f"  - {cat['name']}")

    return categories


# =============================================================================
# STEP 2: SCRAPE ALL CATEGORIES
# =============================================================================

def run_scrapers(categories, output_dir):
    """
    Run the category scraper for each discovered category.

    This function:
    1. Iterates through each category
    2. Runs scrape_category.py as a subprocess for each
    3. Captures output and handles errors gracefully
    4. Tracks timing for each category

    Args:
        categories (list): List of category dictionaries from discovery
        output_dir (Path): Directory where CSV files will be saved

    Returns:
        dict: Summary of results with success/failure counts and timing
    """
    print("\n" + "=" * 60)
    print(f"Step 2: Scraping {len(categories)} categories...")
    print("=" * 60)

    # Track results for each category
    results = {
        "successful": [],
        "failed": [],
        "timings": {}
    }

    # Get the path to scrape_category.py
    # This script is in the same directory as run_all.py
    script_dir = Path(__file__).parent
    scrape_script = script_dir / "scrape_category.py"

    for i, category in enumerate(categories, start=1):
        name = category["name"]
        url = category["url"]

        print(f"\n  [{i}/{len(categories)}] Scraping {name}...")

        # Record start time for this category
        start_time = time.time()

        try:
            # Run scrape_category.py as a subprocess
            # Using subprocess allows us to:
            # 1. Capture output separately for each category
            # 2. Continue even if one category fails
            # 3. Control the execution environment

            # Build the command
            # We use sys.executable to ensure we use the same Python interpreter
            command = [
                sys.executable,
                "-m", "apps.scrapers.nefco.scrape_category",
                "--name", name,
                "--url", url,
                "--output", str(output_dir)
            ]

            # Run the command and capture output
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout per category
                cwd=script_dir.parent.parent.parent  # Run from project root
            )

            # Calculate elapsed time
            elapsed = time.time() - start_time
            results["timings"][name] = elapsed

            # Check if the command succeeded
            if result.returncode == 0:
                results["successful"].append(name)
                print(f"      Success! ({elapsed:.1f}s)")
            else:
                results["failed"].append(name)
                print(f"      WARNING: Scraper returned error code {result.returncode}")
                print(f"      Error output: {result.stderr[:200] if result.stderr else 'None'}")

        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            results["timings"][name] = elapsed
            results["failed"].append(name)
            print(f"      WARNING: Scraper timed out after {elapsed:.1f}s")

        except Exception as e:
            elapsed = time.time() - start_time
            results["timings"][name] = elapsed
            results["failed"].append(name)
            print(f"      WARNING: Error running scraper: {e}")

    # Print summary of scraping results
    print("\n" + "-" * 40)
    print("SCRAPING SUMMARY")
    print("-" * 40)
    print(f"  Successful: {len(results['successful'])}")
    print(f"  Failed: {len(results['failed'])}")

    if results["failed"]:
        print(f"\n  Failed categories:")
        for name in results["failed"]:
            print(f"    - {name}")

    # Print timing information
    if results["timings"]:
        total_scrape_time = sum(results["timings"].values())
        print(f"\n  Total scraping time: {total_scrape_time:.1f}s")
        avg_time = total_scrape_time / len(results["timings"])
        print(f"  Average per category: {avg_time:.1f}s")

    return results


# =============================================================================
# STEP 3: AGGREGATE RESULTS
# =============================================================================

def run_aggregator(output_dir):
    """
    Run the aggregator to combine all category CSVs into a master file.

    This calls the aggregator module which:
    1. Finds all *_products.csv files in the output directory
    2. Combines them into one master_products.csv file
    3. Removes duplicates

    Args:
        output_dir (Path): Directory containing the category CSV files
    """
    print("\n" + "=" * 60)
    print("Step 3: Aggregating results...")
    print("=" * 60)

    # Call the aggregator's main function
    aggregator.main(output_dir=str(output_dir))

    # Check if master file was created
    master_file = output_dir / "master_products.csv"
    if master_file.exists():
        print(f"\nMaster file created successfully: {master_file}")
    else:
        print("\nWARNING: Master file was not created. Check for errors above.")


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def main():
    """
    Main function that orchestrates the entire scraping pipeline.

    This runs all three steps in sequence:
    1. Discover categories
    2. Scrape each category
    3. Aggregate results

    It also tracks total elapsed time and provides a final summary.
    """
    # Record the overall start time
    pipeline_start_time = time.time()

    print("\n" + "=" * 60)
    print("NEFCO SCRAPER PIPELINE")
    print("=" * 60)
    print(f"Demo mode: {config.DEMO_MODE}")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Set up output directory
    # We save to 'output' directory relative to the project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    output_dir = project_root / "output"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # -------------------------------------------------------------------------
    # Step 1: Discover categories
    # -------------------------------------------------------------------------
    categories = run_discovery(output_dir)

    if not categories:
        print("\nERROR: No categories discovered. Cannot continue.")
        return

    # -------------------------------------------------------------------------
    # Step 2: Scrape all categories
    # -------------------------------------------------------------------------
    scrape_results = run_scrapers(categories, output_dir)

    # -------------------------------------------------------------------------
    # Step 3: Aggregate results
    # -------------------------------------------------------------------------
    run_aggregator(output_dir)

    # -------------------------------------------------------------------------
    # Final Summary
    # -------------------------------------------------------------------------
    pipeline_end_time = time.time()
    total_elapsed = pipeline_end_time - pipeline_start_time

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Total elapsed time: {total_elapsed:.1f} seconds")
    print(f"Categories processed: {len(categories)}")
    print(f"  - Successful: {len(scrape_results['successful'])}")
    print(f"  - Failed: {len(scrape_results['failed'])}")
    print(f"\nOutput files are located in:")
    print(f"  {output_dir}")
    print(f"\nMaster product file:")
    print(f"  {output_dir / 'master_products.csv'}")
    print("\n" + "=" * 60)


# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

# This block only runs when you execute this file directly:
#   python -m apps.scrapers.nefco.run_all
#
# It does NOT run when you import this module from another file.

if __name__ == "__main__":
    main()
