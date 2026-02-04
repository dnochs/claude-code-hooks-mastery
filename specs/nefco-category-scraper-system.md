# Plan: NEFCO Category Scraper System

## Task Description
Create a multi-agent web scraper system that scrapes all sub-categories from the NEFCO "Specialty By Trade" catalog page. Each sub-category will be scraped by a dedicated agent running in parallel, and a "Lead Aggregator" agent will combine all individual CSV outputs into one master CSV file. The system includes a 5-second delay between requests to be polite to the server and avoid 403 errors.

## Objective
Build a modular, multi-agent scraper system that:
1. Identifies all sub-categories on the NEFCO Specialty By Trade page
2. Creates separate scraper modules for each sub-category
3. Runs scrapers in parallel using dedicated builder agents
4. Aggregates all results into a master CSV via a Lead Aggregator agent
5. Uses polite scraping practices (5-second delays, proper headers)

## Problem Statement
Scraping an entire product catalog manually is time-consuming and error-prone. We need an automated system that can:
- Handle multiple sub-categories independently
- Run scrapers in parallel for efficiency
- Combine results into a single, unified dataset
- Respect the website by adding delays between requests

## Solution Approach
Create a modular architecture with:
1. **Base scraper module** - Shared utilities (fetch, parse, delay, CSV writing)
2. **Category discovery script** - Identifies all sub-categories from the main page
3. **Individual category scrapers** - One script per sub-category (can run in parallel)
4. **Aggregator script** - Combines all individual CSVs into one master file
5. **Orchestrator script** - Runs the entire pipeline

Since the NEFCO site blocks automated requests (403 Forbidden), we'll use demo mode with realistic sample data to demonstrate the architecture.

## Relevant Files

### Existing Files
- `apps/scrapers/nefco_scraper.py` - Reference implementation with patterns to follow
- `apps/scrapers/__init__.py` - Package marker
- `apps/scrapers/output/` - Output directory

### New Files
- `apps/scrapers/nefco/` - New directory for the category scraper system
- `apps/scrapers/nefco/__init__.py` - Package marker
- `apps/scrapers/nefco/base.py` - Shared utilities (fetch, delay, headers, CSV helpers)
- `apps/scrapers/nefco/config.py` - Configuration (URLs, delays, demo mode settings)
- `apps/scrapers/nefco/category_discovery.py` - Discovers sub-categories from main page
- `apps/scrapers/nefco/scrape_category.py` - Generic category scraper (takes category as argument)
- `apps/scrapers/nefco/aggregator.py` - Combines all CSVs into master file
- `apps/scrapers/nefco/run_all.py` - Orchestrator script to run the full pipeline
- `apps/scrapers/nefco/output/` - Directory for individual category CSVs
- `apps/scrapers/nefco/output/master_products.csv` - Final aggregated output

## Implementation Phases

### Phase 1: Foundation
- Create directory structure for `apps/scrapers/nefco/`
- Create `base.py` with shared utilities (fetch with delay, CSV helpers)
- Create `config.py` with URLs, timing, and demo mode settings

### Phase 2: Core Implementation
- Create `category_discovery.py` to identify sub-categories
- Create `scrape_category.py` - generic scraper that accepts category as argument
- Create `aggregator.py` to combine all individual CSVs

### Phase 3: Integration & Polish
- Create `run_all.py` orchestrator script
- Test the complete pipeline
- Validate master CSV output

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- You're responsible for deploying the right team members with the right context to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use `Task` and `Task*` tools to deploy team members to do the building, validating, testing, deploying, and other tasks.

### Team Members

- Builder
  - Name: foundation-builder
  - Role: Create directory structure and base modules (base.py, config.py)
  - Agent Type: builder
  - Resume: true

- Builder
  - Name: discovery-builder
  - Role: Create the category discovery script
  - Agent Type: builder
  - Resume: true

- Builder
  - Name: scraper-builder
  - Role: Create the generic category scraper script
  - Agent Type: builder
  - Resume: true

- Builder
  - Name: aggregator-builder (Lead Aggregator)
  - Role: Create the aggregator script that combines all CSVs
  - Agent Type: builder
  - Resume: true

- Builder
  - Name: orchestrator-builder
  - Role: Create the run_all.py orchestrator script
  - Agent Type: builder
  - Resume: true

- Validator
  - Name: system-validator
  - Role: Validate the entire scraper system works end-to-end
  - Agent Type: validator
  - Resume: false

## Step by Step Tasks

### 1. Create Directory Structure and Base Module
- **Task ID**: setup-foundation
- **Depends On**: none
- **Assigned To**: foundation-builder
- **Agent Type**: builder
- **Parallel**: false
- Create `apps/scrapers/nefco/` directory
- Create `apps/scrapers/nefco/__init__.py`
- Create `apps/scrapers/nefco/output/` directory
- Create `apps/scrapers/nefco/config.py` with:
  - BASE_URL for NEFCO catalog
  - TARGET_CATEGORY_URL for Specialty By Trade
  - REQUEST_DELAY = 5 (seconds between requests)
  - DEMO_MODE = True (fallback for 403 errors)
  - Sample sub-categories data for demo mode
- Create `apps/scrapers/nefco/base.py` with:
  - `fetch_page(url)` - fetches with proper headers and 5-second delay
  - `delay_between_requests()` - implements the 5-second pause
  - `get_headers()` - returns browser-like headers
  - `save_to_csv(data, filepath)` - saves list of dicts to CSV
  - `read_csv(filepath)` - reads CSV into list of dicts

### 2. Create Category Discovery Script
- **Task ID**: create-discovery
- **Depends On**: setup-foundation
- **Assigned To**: discovery-builder
- **Agent Type**: builder
- **Parallel**: false
- Create `apps/scrapers/nefco/category_discovery.py` with:
  - Function to fetch the main category page
  - Function to parse and extract all sub-category links
  - Demo mode with sample sub-categories (Electrical, Plumbing, HVAC, Fire Protection, etc.)
  - Save discovered categories to `output/categories.json`
  - Main block that runs discovery and prints results

### 3. Create Generic Category Scraper
- **Task ID**: create-scraper
- **Depends On**: setup-foundation
- **Assigned To**: scraper-builder
- **Agent Type**: builder
- **Parallel**: true (can run alongside task 2)
- Create `apps/scrapers/nefco/scrape_category.py` with:
  - Accept category name and URL as command-line arguments
  - Function to fetch category page
  - Function to extract product titles from the page
  - Function to save products to `output/{category_name}_products.csv`
  - Demo mode with sample product data per category
  - 5-second delay before each request (using base.delay_between_requests)
  - Clear progress output showing which category is being scraped

### 4. Create Lead Aggregator Script
- **Task ID**: create-aggregator
- **Depends On**: setup-foundation
- **Assigned To**: aggregator-builder
- **Agent Type**: builder
- **Parallel**: true (can run alongside tasks 2 and 3)
- Create `apps/scrapers/nefco/aggregator.py` with:
  - Function to find all `*_products.csv` files in output directory
  - Function to read and combine all CSVs
  - Add a "category" column to track which category each product came from
  - Remove duplicates if any
  - Save combined data to `output/master_products.csv`
  - Print summary: total products, products per category

### 5. Create Orchestrator Script
- **Task ID**: create-orchestrator
- **Depends On**: create-discovery, create-scraper, create-aggregator
- **Assigned To**: orchestrator-builder
- **Agent Type**: builder
- **Parallel**: false
- Create `apps/scrapers/nefco/run_all.py` with:
  - Step 1: Run category discovery
  - Step 2: For each category, run the scraper (with delays between)
  - Step 3: Run the aggregator to combine results
  - Print overall progress and timing
  - Handle errors gracefully (continue with other categories if one fails)

### 6. Validate Complete System
- **Task ID**: validate-system
- **Depends On**: create-orchestrator
- **Assigned To**: system-validator
- **Agent Type**: validator
- **Parallel**: false
- Run syntax check on all Python files: `uv run python -m py_compile apps/scrapers/nefco/*.py`
- Run the full pipeline: `uv run python apps/scrapers/nefco/run_all.py`
- Verify individual category CSVs were created
- Verify master_products.csv exists and contains data from all categories
- Check that the "category" column is present in master CSV

## Acceptance Criteria
- [ ] `apps/scrapers/nefco/` directory structure exists
- [ ] `base.py` contains shared utilities with 5-second delay function
- [ ] `config.py` contains all configuration including REQUEST_DELAY = 5
- [ ] `category_discovery.py` can discover/list sub-categories
- [ ] `scrape_category.py` can scrape a single category and save to CSV
- [ ] `aggregator.py` combines all category CSVs into master_products.csv
- [ ] `run_all.py` orchestrates the full pipeline
- [ ] All scripts have clear comments explaining what they do
- [ ] 5-second delay is implemented between requests
- [ ] Demo mode works when site returns 403
- [ ] `master_products.csv` contains products from all categories with category column
- [ ] No syntax errors in any Python files

## Validation Commands
Execute these commands to validate the task is complete:

- `uv run python -m py_compile apps/scrapers/nefco/base.py` - Validate base module
- `uv run python -m py_compile apps/scrapers/nefco/config.py` - Validate config
- `uv run python -m py_compile apps/scrapers/nefco/category_discovery.py` - Validate discovery
- `uv run python -m py_compile apps/scrapers/nefco/scrape_category.py` - Validate scraper
- `uv run python -m py_compile apps/scrapers/nefco/aggregator.py` - Validate aggregator
- `uv run python -m py_compile apps/scrapers/nefco/run_all.py` - Validate orchestrator
- `uv run python apps/scrapers/nefco/run_all.py` - Run full pipeline
- `type apps\scrapers\nefco\output\master_products.csv` - Display master CSV (Windows)

## Notes
- The user prefers Python and wants beginner-friendly, well-commented code
- NEFCO blocks automated requests (403 Forbidden), so demo mode is essential
- The 5-second delay is important for polite scraping and avoiding rate limits
- The system is designed to be modular - each script can be run independently
- Sub-categories to scrape (demo data based on typical NEFCO offerings):
  - Electrical
  - Plumbing
  - HVAC
  - Fire Protection
  - Mechanical
  - Data/Communications
- Future enhancement: Use Playwright for browser automation to bypass bot protection
