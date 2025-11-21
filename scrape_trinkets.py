import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin
import base64

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
    
    # Find all trinket links
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
    
    # Get the main image
    content = soup.find('div', {'id': 'mw-content-text'})
    if content:
        img = content.find('img')
        if img:
            img_url = urljoin("https://arcraiders.wiki", img.get('src'))
            trinket_data['image_url'] = img_url
            trinket_data['image_base64'] = download_image_as_base64(img_url)
    
    # Get infobox data
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

def main():
    import sys
    
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
            print("\nTip: Use 'python scrape_trinkets.py --scrape' to force fresh data from web")
            return all_trinket_data
        except Exception as e:
            print(f"Error loading cache: {e}")
            print("Falling back to web scraping...")
            should_scrape = True
    else:
        if should_scrape:
            print("--scrape flag detected, fetching fresh data from web...")
        else:
            print(f"No cached data found at {json_file}, scraping from web...")
    
    # Scrape from web
    trinkets = scrape_trinket_category()
    
    # Scrape each trinket page
    all_trinket_data = []
    for trinket in trinkets:
        try:
            data = scrape_trinket_page(trinket['url'])
            data['name'] = trinket['name']
            all_trinket_data.append(data)
        except Exception as e:
            print(f"Error scraping {trinket['name']}: {e}")
    
    # Save data to JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_trinket_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nScraped {len(all_trinket_data)} trinkets successfully!")
    print(f"Data saved to {json_file}")
    
    return all_trinket_data

if __name__ == "__main__":
    main()
