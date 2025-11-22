import requests
from bs4 import BeautifulSoup

url = 'https://arcraiders.wiki/wiki/Kettle'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')

infobox = soup.find('table', {'class': 'infobox'})
rows = infobox.find_all('tr')

for row in rows:
    th = row.find('th')
    td = row.find('td')
    if th and td:
        key = th.text.strip()
        if 'Sell' in key:
            print(f"Key: {key}")
            print(f"TD text: {td.text.strip()}")
            
            # Find all template-price divs
            price_divs = td.find_all('div', {'class': 'template-price'})
            print(f"Found {len(price_divs)} price divs")
            
            for i, div in enumerate(price_divs):
                # Get text content, excluding the image
                text_content = div.get_text(strip=True)
                print(f"  Price {i+1}: '{text_content}'")
            
            # Try getting just the first one
            if price_divs:
                first_price = price_divs[0].get_text(strip=True)
                print(f"\nFirst price extracted: '{first_price}'")
