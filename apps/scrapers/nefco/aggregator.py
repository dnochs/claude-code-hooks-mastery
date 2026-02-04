"""
Lead Aggregator - Combines all category CSV files into one master file.

What does the Lead Aggregator do?
---------------------------------
Think of it like a manager collecting reports from different departments:
1. It finds all the individual category CSV files (electrical_products.csv, etc.)
2. It reads each one and adds a "category" field to track where each product came from
3. It combines them all into one big master_products.csv file
4. It removes any duplicates (same title + category)
5. It prints a summary showing how many products are in each category

This is useful because:
- You can have one single file with ALL products
- You can sort and filter by category
- You can see the total count at a glance

Usage:
    python -m apps.scrapers.nefco.aggregator
    python -m apps.scrapers.nefco.aggregator --output output/custom_folder
"""

import argparse
import glob
import os
from pathlib import Path

# Import our base utility functions for reading/writing CSVs
from .base import read_csv, save_to_csv


# =============================================================================
# FINDING CSV FILES
# =============================================================================

def find_category_csvs(output_dir):
    """
    Find all category product CSV files in the output directory.

    This looks for files matching the pattern *_products.csv, which is
    how individual category scrapers save their data (e.g., electrical_products.csv).

    IMPORTANT: We exclude master_products.csv from the results because:
    - That's the file we're going to CREATE (or update)
    - Including it would cause duplicates if we run the aggregator twice

    Args:
        output_dir (str or Path): Directory to search for CSV files

    Returns:
        list: List of file paths (as strings) to category CSV files

    Example:
        csv_files = find_category_csvs("output/")
        # Returns: ["output/electrical_products.csv", "output/plumbing_products.csv"]
    """
    # Convert to Path for easier manipulation
    output_dir = Path(output_dir)

    # Build the search pattern: any file ending in _products.csv
    # The ** would search subdirectories too, but we just use * for this folder
    search_pattern = str(output_dir / "*_products.csv")

    print(f"Searching for CSV files in: {output_dir}")
    print(f"Using pattern: {search_pattern}")

    # Use glob to find all matching files
    all_csv_files = glob.glob(search_pattern)

    # Filter out the master file - we don't want to include our output in our input!
    category_csvs = []
    for filepath in all_csv_files:
        filename = os.path.basename(filepath)
        if filename != "master_products.csv":
            category_csvs.append(filepath)
        else:
            print(f"  Skipping master file: {filename}")

    print(f"Found {len(category_csvs)} category CSV file(s)")
    return category_csvs


# =============================================================================
# AGGREGATING DATA
# =============================================================================

def aggregate_csvs(csv_files):
    """
    Read all category CSVs and combine them into one list.

    For each CSV file:
    1. Extract the category name from the filename (e.g., "electrical" from "electrical_products.csv")
    2. Read all products from that CSV
    3. Add a "category" field to each product (so we know where it came from)
    4. Add all products to our combined list

    At the end, we remove duplicates based on title + category combination.

    Args:
        csv_files (list): List of file paths to CSV files to aggregate

    Returns:
        list: Combined list of all products from all CSVs

    Example:
        files = ["output/electrical_products.csv", "output/plumbing_products.csv"]
        all_products = aggregate_csvs(files)
        # Returns combined list with "category" field added to each product
    """
    # This will hold ALL products from ALL files
    all_products = []

    print("\n" + "="*60)
    print("AGGREGATING CSV FILES")
    print("="*60)

    for filepath in csv_files:
        # Extract category name from filename
        # Example: "output/electrical_products.csv" -> "electrical"
        filename = os.path.basename(filepath)  # "electrical_products.csv"
        category_name = filename.replace("_products.csv", "")  # "electrical"

        print(f"\nProcessing: {filename}")
        print(f"  Category: {category_name}")

        # Read all products from this CSV using our base module function
        products = read_csv(filepath)

        if not products:
            print(f"  WARNING: No products found in {filename}")
            continue

        # Add the category field to each product
        # This is important so we know which category each product came from
        for product in products:
            # Add or update the category field
            product["category"] = category_name

        # Add these products to our combined list
        all_products.extend(products)
        print(f"  Added {len(products)} products from {category_name}")

    # Remove duplicates
    # A duplicate is defined as having the same title AND category
    # (same title in different categories is fine - might be different products)
    print("\nRemoving duplicates...")
    original_count = len(all_products)

    # Use a set to track unique combinations we've seen
    seen = set()
    unique_products = []

    for product in all_products:
        # Create a unique key from title + category
        # We use .get() with defaults in case fields are missing
        title = product.get("title", "")
        category = product.get("category", "")
        unique_key = (title, category)

        # Only add if we haven't seen this combination before
        if unique_key not in seen:
            seen.add(unique_key)
            unique_products.append(product)

    duplicates_removed = original_count - len(unique_products)
    if duplicates_removed > 0:
        print(f"  Removed {duplicates_removed} duplicate(s)")
    else:
        print("  No duplicates found")

    return unique_products


# =============================================================================
# SUMMARY AND REPORTING
# =============================================================================

def print_summary(products):
    """
    Print a nice summary of the aggregated products.

    Shows:
    - Total number of products
    - Breakdown by category (how many products in each)

    Args:
        products (list): List of product dictionaries (with "category" field)

    Example output:
        AGGREGATION SUMMARY
        ====================
        Total products: 150

        Products by category:
          electrical: 75
          plumbing: 50
          hvac: 25
    """
    print("\n" + "="*60)
    print("AGGREGATION SUMMARY")
    print("="*60)

    # Total count
    print(f"\nTotal products: {len(products)}")

    # Count products per category
    # We'll use a dictionary to count: {"electrical": 75, "plumbing": 50, ...}
    category_counts = {}

    for product in products:
        category = product.get("category", "unknown")
        # If we've seen this category, add 1; otherwise start at 1
        if category in category_counts:
            category_counts[category] += 1
        else:
            category_counts[category] = 1

    # Print the breakdown
    if category_counts:
        print("\nProducts by category:")
        # Sort categories alphabetically for consistent output
        for category in sorted(category_counts.keys()):
            count = category_counts[category]
            print(f"  {category}: {count}")
    else:
        print("\nNo categories found.")


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main(output_dir="output"):
    """
    Main function that orchestrates the aggregation process.

    Steps:
    1. Find all category CSV files in the output directory
    2. If none found, print an error and exit
    3. Aggregate all CSVs into one combined list
    4. Save to master_products.csv
    5. Print a summary

    Args:
        output_dir (str): Directory containing category CSVs and where
                         master_products.csv will be saved
    """
    print("\n" + "="*60)
    print("NEFCO LEAD AGGREGATOR")
    print("="*60)
    print(f"Output directory: {output_dir}")

    # Step 1: Find all category CSV files
    csv_files = find_category_csvs(output_dir)

    # Step 2: Check if we found any files
    if not csv_files:
        print("\nERROR: No category CSV files found!")
        print("Make sure you have *_products.csv files in the output directory.")
        print("Run the category scrapers first to generate these files.")
        return

    # Step 3: Aggregate all CSVs
    all_products = aggregate_csvs(csv_files)

    # Step 4: Save to master file
    if all_products:
        master_filepath = Path(output_dir) / "master_products.csv"
        print(f"\nSaving master file to: {master_filepath}")
        success = save_to_csv(all_products, master_filepath)

        if success:
            print("\n" + "="*60)
            print("SUCCESS!")
            print("="*60)
            print(f"Master CSV created: {master_filepath}")
        else:
            print("\nERROR: Failed to save master CSV file.")
            return
    else:
        print("\nWARNING: No products to aggregate. Master file not created.")
        return

    # Step 5: Print summary
    print_summary(all_products)


# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Set up command line argument parsing
    # This allows users to specify a custom output directory
    parser = argparse.ArgumentParser(
        description="Aggregate all category CSV files into a master products file."
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Directory containing category CSVs (default: output/)"
    )

    # Parse the command line arguments
    args = parser.parse_args()

    # Run the main function with the specified output directory
    main(output_dir=args.output)
