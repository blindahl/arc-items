#!/usr/bin/env python
"""
Combined script that scrapes Arc Raiders wiki data and generates HTML.
This script imports and uses functions from scrape.py and generate_html.py.
"""

import sys
import os

# Import scraping functionality
from scrape import main as scrape_main

# Import HTML generation functionality
from generate_html import main as generate_html_main


def main():
    print("=== Arc Raiders Item Scraper & HTML Generator ===\n")
    
    # Check if --scrape flag is passed
    should_scrape = '--scrape' in sys.argv
    
    output_dir = 'output'
    json_file = os.path.join(output_dir, 'items_data.json')
    
    # Check if we need to scrape
    if should_scrape:
        print("--scrape flag detected, fetching fresh data from web...\n")
        scrape_main()
    elif not os.path.exists(json_file):
        print(f"No cached data found at {json_file}, scraping from web...\n")
        scrape_main()
    else:
        print(f"Using cached data from {json_file}")
        print("Tip: Use 'python scrape_and_generate.py --scrape' to force fresh data from web\n")
    
    # Generate HTML
    print("\n" + "="*50)
    print("Generating HTML...")
    print("="*50 + "\n")
    generate_html_main()
    
    print("\n" + "="*50)
    print("Complete!")
    print("="*50)


if __name__ == "__main__":
    main()
