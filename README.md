# Arc Raiders Items Database Scraper

This project scrapes item data from the Arc Raiders wiki across multiple categories and generates a static HTML page with thumbnails, category filtering, and sortable information for all items.

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
- `output/items.html` - Static HTML page with all items
- `output/images/` - Downloaded item images (named by category and item)

Open `output/items.html` in your browser to view the results.

## Features

- **Multi-Category Support**: Scrapes 8 different item categories
- **Category Filtering**: Checkboxes to show/hide each category (all visible by default)
- **Local Images**: Images saved locally for faster loading and offline access
- **Statistics Dashboard**: Shows total items, visible items, and category counts
- **Interactive Sorting**: Sort by name or category
  - Name (A-Z / Z-A)
  - Category (A-Z / Z-A)
- **Dynamic Properties**: Displays relevant properties based on item type (Sell Price, Stack Size, Weight, Damage, Type, Rarity, etc.)
- **Cached Data**: Fast regeneration using saved JSON
- **Responsive Design**: Mobile-friendly grid layout
- **Structured Data**: JSON organized by category for easy navigation
