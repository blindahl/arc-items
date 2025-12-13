import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin
import re

# All categories to scrape
CATEGORIES = {
    'Grenades': 'https://arcraiders.wiki/wiki/Grenades',
    'Trinkets': 'https://arcraiders.wiki/wiki/Category:Trinket',
    'Loot': 'https://arcraiders.wiki/wiki/Loot'
}
#,
#    'Weapons': 'https://arcraiders.wiki/wiki/Weapons',
#    'Augments': 'https://arcraiders.wiki/wiki/Augments',
#    'Shields': 'https://arcraiders.wiki/wiki/Shields',
#    'Healing': 'https://arcraiders.wiki/wiki/Healing',
#    'Quick Use': 'https://arcraiders.wiki/wiki/Quick_Use',
#    'Traps': 'https://arcraiders.wiki/wiki/Traps'
#}

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
    
    # Determine actual category from data-tag row content
    actual_category = category_name  # Default to scraped category
    
    # Find all data-tag rows without 'icon' and get the one with meaningful content
    data_tag_rows = soup.find_all('tr', class_=lambda x: x and 'data-tag' in x and 'icon' not in x)
    data_tag_row = None
    for row in data_tag_rows:
        td = row.find('td')
        if td:
            text = td.get_text(strip=True)
            # Look for category names (not rarity like 'Common', 'Rare', etc.)
            if text in ['Trinket', 'Weapon', 'Augment', 'Shield', 'Healing', 'Quick Use', 'Grenade', 'Trap', 'Loot']:
                data_tag_row = row
                break
    if data_tag_row:
        td = data_tag_row.find('td')
        if td:
            tag_value = td.get_text(strip=True)
            #if tag_value:  # Only print if tag_value is not empty
            #    print(f"  → Found data-tag for {item_name}: '{tag_value}'")
            # Map tag values to our categories
            category_mapping = {
                'Weapon': 'Weapons',
                'Augment': 'Augments',
                'Shield': 'Shields',
                'Healing': 'Healing',
                'Quick Use': 'Quick Use',
                'Trap': 'Traps',
                'Grenade': 'Grenades',
                'Trinket': 'Trinkets',
                'Loot': 'Loot'
            }
            if tag_value in category_mapping:
                actual_category = category_mapping[tag_value]
                if actual_category != category_name:
                    print(f"  → Reassigned {item_name} from {category_name} to {actual_category}")
            else:
                print(f"  → Unknown data-tag value '{tag_value}' for {item_name}, keeping in {category_name}")
        else:
            print(f"  → No <td> found in data-tag row for {item_name}")
    
    item_data['category'] = actual_category
    
    # Extract rarity and background color from data-tag class
    rarity_row = soup.find('tr', class_=lambda x: x and 'data-tag' in x and any(cls.startswith('data-tag-') and cls != 'data-tag' for cls in x.split()))
    if rarity_row:
        classes = rarity_row.get('class', [])
        for cls in classes:
            if cls.startswith('data-tag-') and cls != 'data-tag':
                rarity = cls.replace('data-tag-', '').title()
                item_data['Rarity'] = rarity
                #print(f"  → Found rarity for {item_name}: {rarity}")
                break
        
        # Extract background color from the row's style or computed style
        style = rarity_row.get('style', '')
        if 'background' in style or 'background-color' in style:
            item_data['background_color'] = style
        else:
            # Try to get computed background color from CSS classes
            # Common rarity colors based on typical game conventions
            rarity_colors = {
                'Common': '#9d9d9d',      # Gray
                'Uncommon': '#1eff00',    # Green  
                'Rare': '#0070dd',        # Blue
                'Epic': '#a335ee',        # Purple
                'Legendary': '#ff8000',   # Orange
                'Mythic': '#e6cc80'       # Gold
            }
            if 'Rarity' in item_data and item_data['Rarity'] in rarity_colors:
                item_data['background_color'] = rarity_colors[item_data['Rarity']]
    
    # Get the main image and its gradient style
    content = soup.find('div', {'id': 'mw-content-text'})
    if content:
        img = content.find('img')
        if img:
            img_url = urljoin("https://arcraiders.wiki", img.get('src'))
            item_data['image_url'] = img_url
            
            # Check if the image has a gradient style applied
            img_parent = img.parent
            if img_parent:
                parent_style = img_parent.get('style', '')
                if 'background' in parent_style or 'gradient' in parent_style:
                    item_data['image_gradient'] = parent_style
                    print(f"  → Found gradient style for {item_name}: {parent_style}")
            
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

def main():
    print("=== Arc Raiders Item Scraper ===\n")
    
    # Create output directories
    output_dir = 'output'
    images_dir = os.path.join(output_dir, 'images')
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    json_file = os.path.join(output_dir, 'items_data.json')
    all_items_data = {}
    
    # Initialize all categories
    for category_name in CATEGORIES.keys():
        all_items_data[category_name] = []
    
    # Scrape all categories
    temp_items = []  # Store all items temporarily
    
    for category_name, category_url in CATEGORIES.items():
        print(f"\n{'='*50}")
        print(f"Processing category: {category_name}")
        print(f"{'='*50}")
        
        try:
            # Get all items in category
            items = scrape_category_page(category_url, category_name)
            
            # Scrape each item page
            for item in items:
                try:
                    data = scrape_item_page(item['url'], item['name'], category_name, images_dir)
                    temp_items.append(data)
                except Exception as e:
                    print(f"Error scraping {item['name']}: {e}")
            
            print(f"Successfully processed {len(items)} items from {category_name}")
            
        except Exception as e:
            print(f"Error processing category {category_name}: {e}")
    
    # Deduplicate items by URL and group by their actual categories
    seen_urls = set()
    for item in temp_items:
        item_url = item['url']
        if item_url not in seen_urls:
            seen_urls.add(item_url)
            actual_category = item['category']
            if actual_category in all_items_data:
                all_items_data[actual_category].append(item)
            else:
                # If category doesn't exist, create it
                all_items_data[actual_category] = [item]
        else:
            print(f"  → Skipping duplicate: {item['name']} (already processed)")
    
    # Remove empty categories
    all_items_data = {k: v for k, v in all_items_data.items() if v}
    
    # Save data to JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_items_data, f, indent=2, ensure_ascii=False)
    
    total_items = sum(len(items) for items in all_items_data.values())
    print(f"\n{'='*50}")
    print(f"Scraping complete!")
    print(f"Total items scraped: {total_items}")
    print(f"Categories: {len(all_items_data)}")
    print(f"Data saved to: {json_file}")
    print(f"Images saved to: {images_dir}")
    print(f"{'='*50}")
    
    return all_items_data

if __name__ == "__main__":
    main()
