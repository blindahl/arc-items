import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urljoin

# All categories to scrape
CATEGORIES = {
    'Weapons': 'https://arcraiders.wiki/wiki/Weapons',
    'Augments': 'https://arcraiders.wiki/wiki/Augments',
    'Shields': 'https://arcraiders.wiki/wiki/Shields',
    'Healing': 'https://arcraiders.wiki/wiki/Healing',
    'Quick Use': 'https://arcraiders.wiki/wiki/Quick_Use',
    'Grenades': 'https://arcraiders.wiki/wiki/Grenades',
    'Traps': 'https://arcraiders.wiki/wiki/Traps',
    'Trinkets': 'https://arcraiders.wiki/wiki/Category:Trinket'
}

def get_page_content(url):
    """Fetch page content"""
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def download_image(img_url, save_path):
    """Download image and save locally"""
    try:
        response = requests.get(img_url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading image {img_url}: {e}")
        return False

def sanitize_filename(name):
    """Sanitize filename to be safe for filesystem"""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def scrape_category_page(category_url, category_name):
    """Scrape a category page to get all item links"""
    base_url = "https://arcraiders.wiki"
    
    print(f"Fetching {category_name} page...")
    html = get_page_content(category_url)
    soup = BeautifulSoup(html, 'html.parser')
    
    item_links = []
    
    # Check if it's a Category page (like Trinkets)
    if 'Category:' in category_url:
        category_content = soup.find('div', {'id': 'mw-pages'})
        if category_content:
            links = category_content.find_all('a')
            for link in links:
                href = link.get('href')
                if href and '/wiki/' in href and 'Category:' not in href:
                    full_url = urljoin(base_url, href)
                    item_links.append({
                        'name': link.text.strip(),
                        'url': full_url
                    })
    else:
        # For regular pages, find tables with items
        content = soup.find('div', {'id': 'mw-content-text'})
        if content:
            # Look for tables with item information
            tables = content.find_all('table', {'class': 'wikitable'})
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    link = row.find('a')
                    if link and link.get('href'):
                        href = link.get('href')
                        if '/wiki/' in href and 'Category:' not in href:
                            full_url = urljoin(base_url, href)
                            item_links.append({
                                'name': link.text.strip(),
                                'url': full_url
                            })
    
    print(f"Found {len(item_links)} items in {category_name}")
    return item_links

def scrape_item_page(item_url, item_name, category_name, images_dir):
    """Scrape individual item page"""
    print(f"Scraping {item_name}...")
    html = get_page_content(item_url)
    soup = BeautifulSoup(html, 'html.parser')
    
    item_data = {}
    item_data['name'] = item_name
    item_data['url'] = item_url
    item_data['category'] = category_name
    
    # Get the main image
    content = soup.find('div', {'id': 'mw-content-text'})
    if content:
        img = content.find('img')
        if img:
            img_url = urljoin("https://arcraiders.wiki", img.get('src'))
            item_data['image_url'] = img_url
            
            # Save image locally
            img_filename = f"{sanitize_filename(category_name)}_{sanitize_filename(item_name)}.png"
            img_path = os.path.join(images_dir, img_filename)
            if download_image(img_url, img_path):
                item_data['image_path'] = f"images/{img_filename}"
    
    # Get infobox data
    infobox = soup.find('table', {'class': 'infobox'})
    if infobox:
        rows = infobox.find_all('tr')
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            if th and td:
                key = th.text.strip()
                
                # Special handling for Sell Price - extract all levels for weapons
                if key in ['Sell Price', 'Sell price', 'sell price']:
                    # Check if there are multiple prices with template-price divs
                    price_divs = td.find_all('div', {'class': 'template-price'})
                    if price_divs and len(price_divs) > 1:
                        # Multiple levels - extract all prices
                        prices = []
                        for price_div in price_divs:
                            price_text = price_div.get_text(strip=True)
                            # Remove commas from price
                            price_text = price_text.replace(',', '')
                            prices.append(price_text)
                        # Store as comma-separated string for levels 1-4
                        value = ','.join(prices)
                        # Also store the first level price separately
                        item_data['Sell Price'] = prices[0]
                        item_data['Sell Price All Levels'] = value
                        continue
                    elif price_divs:
                        # Single price in template-price div
                        value = price_divs[0].get_text(strip=True).replace(',', '')
                    else:
                        # Fallback to text content
                        value = td.text.strip().replace(',', '')
                else:
                    value = td.text.strip()
                
                item_data[key] = value
    
    return item_data

def generate_html(items_data):
    """Generate static HTML page with all item categories"""
    
    # Convert items data to JSON for JavaScript
    items_json = json.dumps(items_data)
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arc Raiders - Items Database</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            padding: 15px;
            min-height: 100vh;
        }
        .container { max-width: 1800px; margin: 0 auto; }
        h1 {
            text-align: center;
            color: white;
            margin-bottom: 20px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .controls {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .controls-row {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }
        .controls label {
            font-weight: 600;
            color: #2a5298;
        }
        .controls select {
            padding: 8px 12px;
            border: 2px solid #2a5298;
            border-radius: 5px;
            font-size: 14px;
            cursor: pointer;
            background: white;
        }

        .category-filter {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .category-filter input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }
        .category-filter label {
            cursor: pointer;
            font-weight: 500;
            color: #555;
        }
        .items-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(132px, 1fr));
            gap: 5px;
            padding: 6px;
        }
        .item-card {
            background: white;
            border-radius: 5px;
            overflow: hidden;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            padding: 5px;
            text-decoration: none;
            display: block;
            color: inherit;
        }
        .item-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 7px rgba(0,0,0,0.2);
            cursor: pointer;
        }
        .item-image {
            width: 120px;
            height: 120px;
            object-fit: contain;
            background: #f5f5f5;
            border-radius: 4px;
            margin: 0 auto 2px;
            display: block;
        }
        .no-image {
            width: 120px;
            height: 120px;
            background: #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 13px;
            text-align: center;
            border-radius: 4px;
            margin: 0 auto 2px;
        }
        .item-name {
            font-size: 14px;
            font-weight: bold;
            color: #2a5298;
            margin-bottom: 2px;
            text-align: center;
            line-height: 1.1;
            min-height: 31px;
        }
        .item-category {
            font-size: 11px;
            color: #888;
            text-align: center;
            margin-bottom: 4px;
            font-style: italic;
        }
        .item-details {
            font-size: 13px;
            line-height: 1.2;
        }
        .item-details div {
            display: flex;
            justify-content: space-between;
            padding: 1px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .item-details div:last-child {
            border-bottom: none;
        }
        .detail-label {
            font-weight: 600;
            color: #555;
        }
        .detail-value {
            color: #777;
            font-weight: 500;
        }
        .stats-summary {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stats-summary h2 {
            color: #2a5298;
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }
        .stat-item {
            padding: 8px;
            background: #f5f5f5;
            border-radius: 5px;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 3px;
        }
        .stat-value {
            font-size: 20px;
            font-weight: bold;
            color: #2a5298;
        }
        @media (max-width: 768px) {
            .items-grid {
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            }
            h1 { font-size: 1.8em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Arc Raiders - Items Database</h1>
        
        <div class="stats-summary">
            <h2>Collection Statistics</h2>
            <div class="stats-grid" id="statsGrid"></div>
        </div>
        
        <div class="controls">
            <div class="controls-row">
                <label for="sortBy">Sort by:</label>
                <select id="sortBy" onchange="renderItems()">
                    <option value="name-asc">Name (A-Z)</option>
                    <option value="name-desc">Name (Z-A)</option>
                    <option value="category-asc">Category (A-Z)</option>
                    <option value="category-desc">Category (Z-A)</option>
                    <option value="sellprice-asc">Sell Price (Low to High)</option>
                    <option value="sellprice-desc" selected>Sell Price (High to Low)</option>
                    <option value="stackvalue-asc">Stack Value (Low to High)</option>
                    <option value="stackvalue-desc">Stack Value (High to Low)</option>
                </select>
                <div style="display: flex; align-items: center; gap: 15px; margin-left: 30px;">
                    <strong style="color: #2a5298;">Show Categories:</strong>
                    <button onclick="selectAllCategories()" style="padding: 5px 15px; cursor: pointer; background: #2a5298; color: white; border: none; border-radius: 4px;">Select All</button>
                    <button onclick="selectNoneCategories()" style="padding: 5px 15px; cursor: pointer; background: #666; color: white; border: none; border-radius: 4px;">Select None</button>
                    <div id="categoryCheckboxes" style="display: flex; gap: 15px; flex-wrap: wrap;"></div>
                </div>
            </div>
        </div>
        
        <div class="items-grid" id="itemsGrid"></div>
    </div>
    
    <script>
        const itemsData = """ + items_json + """;
        let visibleCategories = new Set();
        
        function initializeCategoryFilters() {
            const checkboxContainer = document.getElementById('categoryCheckboxes');
            const categories = Object.keys(itemsData);
            
            // Initialize all categories as visible
            categories.forEach(cat => visibleCategories.add(cat));
            
            categories.forEach(category => {
                const wrapper = document.createElement('div');
                wrapper.className = 'category-filter';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `cat-${category}`;
                checkbox.checked = true;
                checkbox.onchange = () => toggleCategory(category);
                
                const label = document.createElement('label');
                label.htmlFor = `cat-${category}`;
                label.textContent = `${category} (${itemsData[category].length})`;
                
                wrapper.appendChild(checkbox);
                wrapper.appendChild(label);
                checkboxContainer.appendChild(wrapper);
            });
        }
        
        function toggleCategory(category) {
            const checkbox = document.getElementById(`cat-${category}`);
            if (checkbox.checked) {
                visibleCategories.add(category);
            } else {
                visibleCategories.delete(category);
            }
            renderItems();
        }
        
        function selectAllCategories() {
            const categories = Object.keys(itemsData);
            categories.forEach(category => {
                visibleCategories.add(category);
                const checkbox = document.getElementById(`cat-${category}`);
                if (checkbox) checkbox.checked = true;
            });
            renderItems();
        }
        
        function selectNoneCategories() {
            visibleCategories.clear();
            const categories = Object.keys(itemsData);
            categories.forEach(category => {
                const checkbox = document.getElementById(`cat-${category}`);
                if (checkbox) checkbox.checked = false;
            });
            renderItems();
        }
        
        function updateStats() {
            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = '';
            
            let totalItems = 0;
            let visibleItems = 0;
            
            Object.entries(itemsData).forEach(([category, items]) => {
                totalItems += items.length;
                if (visibleCategories.has(category)) {
                    visibleItems += items.length;
                }
            });
            
            const stats = [
                { label: 'Total Items', value: totalItems },
                { label: 'Visible Items', value: visibleItems },
                { label: 'Categories', value: Object.keys(itemsData).length },
                { label: 'Active Categories', value: visibleCategories.size }
            ];
            
            stats.forEach(stat => {
                const statDiv = document.createElement('div');
                statDiv.className = 'stat-item';
                statDiv.innerHTML = `
                    <div class="stat-label">${stat.label}</div>
                    <div class="stat-value">${stat.value}</div>
                `;
                statsGrid.appendChild(statDiv);
            });
        }
        
        function parseNumber(value) {
            if (!value) return 0;
            const str = String(value).replace(/[^0-9.-]/g, '');
            return parseFloat(str) || 0;
        }
        
        function getAllItems() {
            const allItems = [];
            Object.entries(itemsData).forEach(([category, items]) => {
                if (visibleCategories.has(category)) {
                    items.forEach(item => {
                        allItems.push({ ...item, category: category });
                    });
                }
            });
            return allItems;
        }
        
        function renderItems() {
            const sortBy = document.getElementById('sortBy').value;
            const [field, order] = sortBy.split('-');
            
            let items = getAllItems();
            
            items.sort((a, b) => {
                let aVal, bVal;
                
                if (field === 'name') {
                    aVal = (a.name || '').toLowerCase();
                    bVal = (b.name || '').toLowerCase();
                    return order === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                } else if (field === 'category') {
                    aVal = (a.category || '').toLowerCase();
                    bVal = (b.category || '').toLowerCase();
                    const result = order === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                    if (result === 0) {
                        // Secondary sort by name
                        return (a.name || '').toLowerCase().localeCompare((b.name || '').toLowerCase());
                    }
                    return result;
                } else if (field === 'sellprice') {
                    aVal = parseNumber(a['Sell Price'] || a['Sell price'] || a['sell price'] || 0);
                    bVal = parseNumber(b['Sell Price'] || b['Sell price'] || b['sell price'] || 0);
                    return order === 'asc' ? aVal - bVal : bVal - aVal;
                } else if (field === 'stackvalue') {
                    const aPrice = parseNumber(a['Sell Price'] || a['Sell price'] || a['sell price'] || 0);
                    const aStack = parseNumber(a['Stack Size'] || a['Stack size'] || a['stack size'] || 1);
                    const bPrice = parseNumber(b['Sell Price'] || b['Sell price'] || b['sell price'] || 0);
                    const bStack = parseNumber(b['Stack Size'] || b['Stack size'] || b['stack size'] || 1);
                    aVal = aPrice * aStack;
                    bVal = bPrice * bStack;
                    return order === 'asc' ? aVal - bVal : bVal - aVal;
                }
                
                return 0;
            });
            
            const grid = document.getElementById('itemsGrid');
            grid.innerHTML = '';
            
            items.forEach(item => {
                const card = document.createElement('a');
                card.className = 'item-card';
                card.href = item.url || '#';
                card.target = '_blank';
                card.rel = 'noopener noreferrer';
                
                const name = item.name || 'Unknown Item';
                const category = item.category || 'Unknown';
                
                let imageHtml = '';
                if (item.image_path) {
                    imageHtml = `<img src="${item.image_path}" alt="${name}" class="item-image" onerror="this.parentElement.querySelector('.no-image').style.display='flex'; this.style.display='none';">
                                 <div class="no-image" style="display:none;">No Image</div>`;
                } else {
                    imageHtml = '<div class="no-image">No Image</div>';
                }
                
                // Build details dynamically based on available properties
                let detailsHtml = '';
                const displayedProps = new Set();
                
                // Get sell price and stack size for calculations
                const sellPrice = parseNumber(item['Sell Price'] || item['Sell price'] || item['sell price'] || 0);
                const stackSize = parseNumber(item['Stack Size'] || item['Stack size'] || item['stack size'] || 0);
                
                // Display sell price without commas
                if (sellPrice > 0) {
                    detailsHtml += `<div><span class="detail-label">Sell Price:</span><span class="detail-value">${sellPrice}</span></div>`;
                    displayedProps.add('sell price');
                }
                
                // Display stack size
                if (stackSize > 0) {
                    detailsHtml += `<div><span class="detail-label">Stack Size:</span><span class="detail-value">${stackSize}</span></div>`;
                    displayedProps.add('stack size');
                }
                
                // Display stack value (sell price × stack size)
                if (sellPrice > 0 && stackSize > 0) {
                    const stackValue = sellPrice * stackSize;
                    detailsHtml += `<div><span class="detail-label">Stack Value:</span><span class="detail-value">${stackValue}</span></div>`;
                }
                
                // Display other properties
                const otherProps = ['Weight', 'weight', 'Damage', 'damage', 'Type', 'type', 'Rarity', 'rarity'];
                otherProps.forEach(prop => {
                    if (item[prop] && !displayedProps.has(prop.toLowerCase())) {
                        const label = prop.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
                        detailsHtml += `<div><span class="detail-label">${label}:</span><span class="detail-value">${item[prop]}</span></div>`;
                        displayedProps.add(prop.toLowerCase());
                    }
                });
                
                card.innerHTML = `
                    ${imageHtml}
                    <div class="item-name">${name}</div>
                    <div class="item-category">${category}</div>
                    ${detailsHtml ? `<div class="item-details">${detailsHtml}</div>` : ''}
                `;
                
                grid.appendChild(card);
            });
            
            updateStats();
        }
        
        // Initialize
        initializeCategoryFilters();
        renderItems();
    </script>
</body>
</html>"""
    
    return html

def main():
    import sys
    
    print("=== Arc Raiders Item Scraper ===\n")
    
    # Create output directories
    output_dir = 'output'
    images_dir = os.path.join(output_dir, 'images')
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    # Check if --scrape flag is passed
    should_scrape = '--scrape' in sys.argv
    json_file = os.path.join(output_dir, 'items_data.json')
    
    all_items_data = {}
    
    # Try to load from cache first
    if not should_scrape and os.path.exists(json_file):
        print(f"Loading cached data from {json_file}...")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                all_items_data = json.load(f)
            total_items = sum(len(items) for items in all_items_data.values())
            print(f"Loaded {total_items} items from cache across {len(all_items_data)} categories")
        except Exception as e:
            print(f"Error loading cache: {e}")
            print("Falling back to web scraping...")
            should_scrape = True
    else:
        if should_scrape:
            print("--scrape flag detected, fetching fresh data from web...")
        else:
            print(f"No cached data found at {json_file}, scraping from web...")
        should_scrape = True
    
    # Scrape if needed
    if should_scrape:
        for category_name, category_url in CATEGORIES.items():
            print(f"\n{'='*50}")
            print(f"Processing category: {category_name}")
            print(f"{'='*50}")
            
            try:
                # Get all items in category
                items = scrape_category_page(category_url, category_name)
                
                # Scrape each item page
                category_items = []
                for item in items:
                    try:
                        data = scrape_item_page(item['url'], item['name'], category_name, images_dir)
                        category_items.append(data)
                    except Exception as e:
                        print(f"Error scraping {item['name']}: {e}")
                
                all_items_data[category_name] = category_items
                print(f"Successfully scraped {len(category_items)} items from {category_name}")
                
            except Exception as e:
                print(f"Error processing category {category_name}: {e}")
                all_items_data[category_name] = []
        
        # Save data to JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_items_data, f, indent=2, ensure_ascii=False)
        
        total_items = sum(len(items) for items in all_items_data.values())
        print(f"\nScraped {total_items} items across {len(all_items_data)} categories")
        print(f"Data saved to: {json_file}")
        print(f"Images saved to: {images_dir}")
    
    # Generate HTML
    print("\nGenerating HTML...")
    html_content = generate_html(all_items_data)
    html_file = os.path.join(output_dir, 'items.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    total_items = sum(len(items) for items in all_items_data.values())
    print(f"\n{'='*50}")
    print(f"Complete!")
    print(f"Total items: {total_items}")
    print(f"Categories: {len(all_items_data)}")
    print(f"Data saved to: {json_file}")
    print(f"HTML page saved to: {html_file}")
    print(f"\nTip: Use 'python scrape_and_generate.py --scrape' to force fresh data from web")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
