# Plan: NEFCO Product Title Scraper

## Task Description
Create a simple Python web scraper that extracts the product title from a specific NEFCO product page and saves it to a CSV file. This is a beginner-friendly introduction to web scraping using Python.

## Objective
Build a working Python script that:
1. Fetches the NEFCO product page at the given URL
2. Extracts the product title from the HTML
3. Saves the title to a CSV file

## Problem Statement
We need to extract product information from the NEFCO website (gonefco.com). Specifically, we want to pull the product title from a conduit bender product page and store it in a structured CSV format for future use.

## Solution Approach
Use Python with the `requests` library to fetch the page HTML and `BeautifulSoup` to parse and extract the product title. This approach is:
- Beginner-friendly and easy to understand
- No browser automation needed (simpler than Playwright/Selenium)
- Minimal dependencies

## Relevant Files

### New Files
- `apps/scrapers/nefco_scraper.py` - Main scraper script
- `apps/scrapers/output/nefco_products.csv` - Output CSV file (generated)
- `apps/scrapers/__init__.py` - Package init file

### Existing Files
- `pyproject.toml` - Will need to add dependencies (requests, beautifulsoup4)

## Implementation Phases

### Phase 1: Foundation
- Set up project structure with `apps/scrapers/` directory
- Add required dependencies to pyproject.toml

### Phase 2: Core Implementation
- Create the scraper script with:
  - HTTP request to fetch the page
  - HTML parsing to extract product title
  - CSV writing functionality

### Phase 3: Integration & Polish
- Test the scraper
- Verify CSV output is correct
- Add error handling for network issues

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- You're responsible for deploying the right team members with the right context to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use `Task` and `Task*` tools to deploy team members to do the building, validating, testing, deploying, and other tasks.

### Team Members

- Builder
  - Name: scraper-builder
  - Role: Implement the NEFCO product scraper script and set up project structure
  - Agent Type: builder
  - Resume: true

- Validator
  - Name: scraper-validator
  - Role: Verify the scraper works correctly and produces valid CSV output
  - Agent Type: validator
  - Resume: false

## Step by Step Tasks

### 1. Set Up Project Structure
- **Task ID**: setup-structure
- **Depends On**: none
- **Assigned To**: scraper-builder
- **Agent Type**: builder
- **Parallel**: false
- Create `apps/scrapers/` directory
- Create `apps/scrapers/__init__.py` file
- Create `apps/scrapers/output/` directory for CSV output

### 2. Add Dependencies
- **Task ID**: add-dependencies
- **Depends On**: setup-structure
- **Assigned To**: scraper-builder
- **Agent Type**: builder
- **Parallel**: false
- Run `uv add requests beautifulsoup4` to add required packages
- Verify packages are added to pyproject.toml

### 3. Implement Scraper Script
- **Task ID**: implement-scraper
- **Depends On**: add-dependencies
- **Assigned To**: scraper-builder
- **Agent Type**: builder
- **Parallel**: false
- Create `apps/scrapers/nefco_scraper.py` with:
  - Import statements (requests, bs4, csv, pathlib)
  - Function to fetch page HTML
  - Function to extract product title from HTML
  - Function to save title to CSV
  - Main execution block
- Target URL: `https://www.gonefco.com/buy/product/ELEC-Conduit-Bender-W-Single-1-2-2-Rigid-IMC-EMT-Shoe-Group-Vert-HORIZ-Bends-52067299/475156?ID=/Tools/Benders-Accessories/Electric-Benders/Greenlee-854-855-Series-Electric-Benders/dept-CV7`
- Output CSV: `apps/scrapers/output/nefco_products.csv`

### 4. Validate Scraper
- **Task ID**: validate-scraper
- **Depends On**: implement-scraper
- **Assigned To**: scraper-validator
- **Agent Type**: validator
- **Parallel**: false
- Run the scraper: `uv run python apps/scrapers/nefco_scraper.py`
- Check that CSV file was created
- Verify CSV contains the product title
- Run Python syntax check: `uv run python -m py_compile apps/scrapers/nefco_scraper.py`

## Acceptance Criteria
- [ ] `apps/scrapers/nefco_scraper.py` exists and is valid Python
- [ ] Script successfully fetches the NEFCO product page
- [ ] Script extracts the product title from the page
- [ ] Script saves the title to `apps/scrapers/output/nefco_products.csv`
- [ ] CSV file contains at least one row with the product title
- [ ] No syntax errors or import errors

## Validation Commands
Execute these commands to validate the task is complete:

- `uv run python -m py_compile apps/scrapers/nefco_scraper.py` - Verify Python syntax is valid
- `uv run python apps/scrapers/nefco_scraper.py` - Run the scraper
- `type apps\scrapers\output\nefco_products.csv` - Display CSV contents (Windows)

## Notes
- The user prefers Python (as noted in CLAUDE.md)
- This is a learning project, so code should be well-commented and easy to understand
- The scraper targets a single product page - future enhancements could scrape multiple products
- Dependencies will be managed with `uv add` (the project uses uv for Python package management)
- Some websites block scrapers - if the request fails, we may need to add a User-Agent header
