# Arc Raiders Items Database Scraper

This project scrapes item data from the Arc Raiders wiki across multiple categories and generates a static HTML page with thumbnails, category filtering, and sortable information for all items.

Hosted version can be found here: https://blindahl.github.io/arc-items/output/items.html

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

By default, the script will use cached data from `items_data.json` if it exists. This is much faster and avoids unnecessary web requests.

### Force Fresh Scraping
To scrape fresh data from the web:
```bash
python scrape_and_generate.py --scrape
```

### Separate Scripts

**Scrape only (always scrapes fresh data, saves to JSON and downloads images):**
```bash
python scrape.py
```

**Generate HTML from cached JSON:**
```bash
python generate_html.py
```

## Categories Scraped

The scraper collects data from all major item categories:
- **Weapons** - https://arcraiders.wiki/wiki/Weapons
- **Augments** - https://arcraiders.wiki/wiki/Augments
- **Shields** - https://arcraiders.wiki/wiki/Shields
- **Healing** - https://arcraiders.wiki/wiki/Healing
- **Quick Use** - https://arcraiders.wiki/wiki/Quick_Use
- **Grenades** - https://arcraiders.wiki/wiki/Grenades
- **Traps** - https://arcraiders.wiki/wiki/Traps
- **Trinkets** - https://arcraiders.wiki/wiki/Category:Trinket

## Project Structure

- **`scrape.py`** - Handles all web scraping functionality
- **`generate_html.py`** - Generates the HTML page from JSON data
- **`scrape_and_generate.py`** - Convenience script that combines both operations

## How It Works

1. **First run**: Scrapes all category pages from the Arc Raiders wiki
2. Visits each item page and extracts images and data
3. Downloads images locally to `output/images/`
4. Saves structured data to `output/items_data.json` (organized by category)
5. Generates a static HTML page at `output/items.html`
6. **Subsequent runs**: Uses cached JSON data unless `--scrape` flag is provided

## Output Files

All output files are saved in the `output/` folder:
- `output/items_data.json` - Cached scraped data in JSON format (structured by category)
- `output/items.html` - **Self-contained HTML page with embedded images** (single file, fully portable)
Open `output/items.html` in your browser to view the results. The HTML file is completely self-contained with all images embedded as base64 - you can share just this one file!

## Features

### Scraping
- **Multi-Category Support**: Scrapes 8 different item categories
- **Multi-Level Pricing**: Extracts all price levels for weapons (stores first level for sorting, all levels for reference)
- **Local Images**: Downloads and saves images locally for faster loading and offline access
- **Structured Data**: JSON organized by category for easy navigation
- **Error Handling**: Continues scraping even if individual items fail

### HTML Interface
- **Single File Output**: All images embedded as base64 - completely portable and self-contained
- **Category Filtering**: Checkboxes to show/hide each category (all visible by default)
  - Select All / Select None buttons for quick toggling
- **Statistics Dashboard**: Shows total items, visible items, and category counts
- **Advanced Sorting**: Multiple sort options
  - Name (A-Z / Z-A)
  - Category (A-Z / Z-A)
  - Sell Price (Low to High / High to Low) - Default
  - Stack Value (Low to High / High to Low)
- **Calculated Values**: Automatically calculates and displays Stack Value (Sell Price × Stack Size)
- **Dynamic Properties**: Displays relevant properties based on item type (Sell Price, Stack Size, Weight, Damage, Type, Rarity, etc.)
- **Clean Display**: Prices shown without commas for better readability
- **Responsive Design**: Mobile-friendly grid layout
- **Cached Data**: Fast regeneration using saved JSON
