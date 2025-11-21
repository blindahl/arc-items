import requests
from bs4 import BeautifulSoup
import json
import base64
from urllib.parse import urljoin

def get_page_content(url):
    """Fetch page content"""
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def download_image_as_base64(img_url):
    """Download image and convert to base64"""
    try:
        response = requests.get(img_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        print(f"Error downloading image {img_url}: {e}")
        return None

def scrape_trinket_category():
    """Scrape the main trinket category page"""
    base_url = "https://arcraiders.wiki"
    category_url = "https://arcraiders.wiki/wiki/Category:Trinket"
    
    print("Fetching category page...")
    html = get_page_content(category_url)
    soup = BeautifulSoup(html, 'html.parser')
    
    trinket_links = []
    category_content = soup.find('div', {'id': 'mw-pages'})
    
    if category_content:
        links = category_content.find_all('a')
        for link in links:
            href = link.get('href')
            if href and '/wiki/' in href and 'Category:' not in href:
                full_url = urljoin(base_url, href)
                trinket_links.append({
                    'name': link.text.strip(),
                    'url': full_url
                })
    
    print(f"Found {len(trinket_links)} trinkets")
    return trinket_links

def scrape_trinket_page(trinket_url):
    """Scrape individual trinket page"""
    print(f"Scraping {trinket_url}...")
    html = get_page_content(trinket_url)
    soup = BeautifulSoup(html, 'html.parser')
    
    trinket_data = {}
    trinket_data['url'] = trinket_url
    
    content = soup.find('div', {'id': 'mw-content-text'})
    if content:
        img = content.find('img')
        if img:
            img_url = urljoin("https://arcraiders.wiki", img.get('src'))
            trinket_data['image_url'] = img_url
            trinket_data['image_base64'] = download_image_as_base64(img_url)
    
    infobox = soup.find('table', {'class': 'infobox'})
    if infobox:
        rows = infobox.find_all('tr')
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            if th and td:
                key = th.text.strip()
                value = td.text.strip()
                trinket_data[key] = value
    
    return trinket_data

def generate_html(trinkets_data):
    """Generate static HTML page"""
    
    # Convert trinkets data to JSON for JavaScript
    import json
    trinkets_json = json.dumps(trinkets_data)
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arc Raiders - Trinkets</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            padding: 15px;
            min-height: 100vh;
        }
        .container { max-width: 1600px; margin: 0 auto; }
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
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
        .trinkets-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(132px, 1fr));
            gap: 5px;
            padding: 6px;
        }
        .trinket-card {
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
        .trinket-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 7px rgba(0,0,0,0.2);
            cursor: pointer;
        }
        .trinket-image {
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
        .trinket-name {
            font-size: 14px;
            font-weight: bold;
            color: #2a5298;
            margin-bottom: 2px;
            text-align: center;
            line-height: 1.1;
            min-height: 31px;
        }
        .trinket-details {
            font-size: 13px;
            line-height: 1.2;
        }
        .trinket-details div {
            display: flex;
            justify-content: space-between;
            padding: 1px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .trinket-details div:last-child {
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
        @media (max-width: 768px) {
            .trinkets-grid {
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            }
            h1 { font-size: 1.8em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Arc Raiders - Trinkets Collection</h1>
        <div class="controls">
            <label for="sortBy">Sort by:</label>
            <select id="sortBy" onchange="sortTrinkets()">
                <option value="name-asc">Name (A-Z)</option>
                <option value="name-desc">Name (Z-A)</option>
                <option value="sellprice-asc">Sell Price (Low to High)</option>
                <option value="sellprice-desc" selected>Sell Price (High to Low)</option>
                <option value="stacksize-asc">Stack Size (Low to High)</option>
                <option value="stacksize-desc">Stack Size (High to Low)</option>
                <option value="stackvalue-asc">Stack Value (Low to High)</option>
                <option value="stackvalue-desc">Stack Value (High to Low)</option>
                <option value="weight-asc">Weight (Low to High)</option>
                <option value="weight-desc">Weight (High to Low)</option>
            </select>
        </div>
        <div class="trinkets-grid" id="trinketsGrid">
        </div>
    </div>
    
    <script>
        const trinketsData = """ + trinkets_json + """;
        
        function parseNumber(value) {
            if (!value) return 0;
            const str = String(value).replace(/[^0-9.-]/g, '');
            return parseFloat(str) || 0;
        }
        
        function sortTrinkets() {
            const sortBy = document.getElementById('sortBy').value;
            const [field, order] = sortBy.split('-');
            
            let sorted = [...trinketsData];
            
            sorted.sort((a, b) => {
                let aVal, bVal;
                
                if (field === 'name') {
                    aVal = (a.name || '').toLowerCase();
                    bVal = (b.name || '').toLowerCase();
                    return order === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                } else if (field === 'sellprice') {
                    aVal = parseNumber(a['Sell Price'] || a['Sell price'] || a['sell price'] || 0);
                    bVal = parseNumber(b['Sell Price'] || b['Sell price'] || b['sell price'] || 0);
                } else if (field === 'stacksize') {
                    aVal = parseNumber(a['Stack Size'] || a['Stack size'] || a['stack size'] || 0);
                    bVal = parseNumber(b['Stack Size'] || b['Stack size'] || b['stack size'] || 0);
                } else if (field === 'stackvalue') {
                    const aPrice = parseNumber(a['Sell Price'] || a['Sell price'] || a['sell price'] || 0);
                    const aStack = parseNumber(a['Stack Size'] || a['Stack size'] || a['stack size'] || 0);
                    const bPrice = parseNumber(b['Sell Price'] || b['Sell price'] || b['sell price'] || 0);
                    const bStack = parseNumber(b['Stack Size'] || b['Stack size'] || b['stack size'] || 0);
                    aVal = aPrice * aStack;
                    bVal = bPrice * bStack;
                } else if (field === 'weight') {
                    aVal = parseNumber(a['Weight'] || a['weight'] || 0);
                    bVal = parseNumber(b['Weight'] || b['weight'] || 0);
                }
                
                return order === 'asc' ? aVal - bVal : bVal - aVal;
            });
            
            renderTrinkets(sorted);
        }
        
        function renderTrinkets(trinkets) {
            const grid = document.getElementById('trinketsGrid');
            grid.innerHTML = '';
            
            trinkets.forEach(trinket => {
                const card = document.createElement('a');
                card.className = 'trinket-card';
                card.href = trinket.url || '#';
                card.target = '_blank';
                card.rel = 'noopener noreferrer';
                
                const name = trinket.name || 'Unknown Trinket';
                let sellPrice = trinket['Sell Price'] || trinket['Sell price'] || trinket['sell price'] || 'N/A';
                if (sellPrice !== 'N/A') {
                    sellPrice = sellPrice.replace(/,/g, '');
                }
                const stackSize = trinket['Stack Size'] || trinket['Stack size'] || trinket['stack size'] || 'N/A';
                const weight = trinket['Weight'] || trinket['weight'] || 'N/A';
                
                let imageHtml = '';
                if (trinket.image_base64) {
                    imageHtml = `<img src="data:image/png;base64,${trinket.image_base64}" alt="${name}" class="trinket-image">`;
                } else {
                    imageHtml = '<div class="no-image">No Image</div>';
                }
                
                card.innerHTML = `
                    ${imageHtml}
                    <div class="trinket-name">${name}</div>
                    <div class="trinket-details">
                        <div><span class="detail-label">Sell:</span><span class="detail-value">${sellPrice}</span></div>
                        <div><span class="detail-label">Stack:</span><span class="detail-value">${stackSize}</span></div>
                        <div><span class="detail-label">Weight:</span><span class="detail-value">${weight}</span></div>
                    </div>
                `;
                
                grid.appendChild(card);
            });
        }
        
        // Initial render with default sort
        sortTrinkets();
    </script>
</body>
</html>"""
    
    return html

def main():
    import sys
    import os
    
    print("=== Arc Raiders Trinket Scraper ===\n")
    
    # Create output directory if it doesn't exist
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if --scrape flag is passed
    should_scrape = '--scrape' in sys.argv
    json_file = os.path.join(output_dir, 'trinkets_data.json')
    
    all_trinket_data = []
    
    # Try to load from cache first
    if not should_scrape and os.path.exists(json_file):
        print(f"Loading cached data from {json_file}...")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                all_trinket_data = json.load(f)
            print(f"Loaded {len(all_trinket_data)} trinkets from cache")
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
        trinkets = scrape_trinket_category()
        all_trinket_data = []
        
        for trinket in trinkets:
            try:
                data = scrape_trinket_page(trinket['url'])
                data['name'] = trinket['name']
                all_trinket_data.append(data)
            except Exception as e:
                print(f"Error scraping {trinket['name']}: {e}")
        
        # Save JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_trinket_data, f, indent=2, ensure_ascii=False)
        print(f"\nScraped {len(all_trinket_data)} trinkets")
        print(f"Data saved to: {json_file}")
    
    # Generate HTML
    print("\nGenerating HTML...")
    html_content = generate_html(all_trinket_data)
    html_file = os.path.join(output_dir, 'trinkets.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n=== Complete! ===")
    print(f"Total trinkets: {len(all_trinket_data)}")
    print(f"Data saved to: {json_file}")
    print(f"HTML page saved to: {html_file}")
    print(f"\nTip: Use 'python scrape_and_generate.py --scrape' to force fresh data from web")

if __name__ == "__main__":
    main()
