# Arc Raiders Trinket Scraper

This project scrapes trinket data from the Arc Raiders wiki and generates a static HTML page with compact thumbnails and sortable information for each trinket.

## Installation

Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start (Uses Cached Data)
```bash
python scrape_and_generate.py
```

By default, the script will use cached data from `trinkets_data.json` if it exists. This is much faster and avoids unnecessary web requests.

### Force Fresh Scraping
To scrape fresh data from the web:
```bash
python scrape_and_generate.py --scrape
```

### Separate Scripts

**Scrape only (saves to JSON):**
```bash
python scrape_trinkets.py --scrape
```

**Generate HTML from cached JSON:**
```bash
python generate_html.py
```

## How It Works

1. **First run**: Scrapes the trinket category page at https://arcraiders.wiki/wiki/Category:Trinket
2. Visits each trinket page and extracts images and data
3. Saves the data to `output/trinkets_data.json`
4. Generates a static HTML page at `output/trinkets.html`
5. **Subsequent runs**: Uses cached JSON data unless `--scrape` flag is provided

## Output Files

All output files are saved in the `output/` folder:
- `output/trinkets_data.json` - Cached scraped data in JSON format
- `output/trinkets.html` - Static HTML page with all trinkets

Open `output/trinkets.html` in your browser to view the results.

## Features

- **Compact Layout**: 100x100px thumbnails with tight 8px grid spacing
- **Essential Info Only**: Shows Sell Price, Stack Size, and Weight
- **Interactive Sorting**: Sort by any field in ascending or descending order
  - Name (A-Z / Z-A)
  - Sell Price (Low to High / High to Low)
  - Stack Size (Low to High / High to Low)
  - Weight (Low to High / High to Low)
- **Cached Data**: Fast regeneration using saved JSON
- **Embedded Images**: Base64 encoded for single-file portability
- **Responsive Design**: Mobile-friendly grid layout
- **Self-Contained**: All data in a single HTML file
