import json
import os
import base64

def load_image_as_base64(image_path):
    """Load an image file and convert it to base64"""
    try:
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
    return None

def generate_html(items_data, output_dir='output'):
    """Generate static HTML page with all item categories"""
    
    # Convert images to base64 and embed in items data
    items_with_base64 = {}
    for category, items in items_data.items():
        items_with_base64[category] = []
        for item in items:
            item_copy = item.copy()
            # If item has an image path, load and convert to base64
            if 'image_path' in item_copy:
                image_full_path = os.path.join(output_dir, item_copy['image_path'])
                base64_data = load_image_as_base64(image_full_path)
                if base64_data:
                    item_copy['image_base64'] = base64_data
                # Remove the image_path since we're embedding
                del item_copy['image_path']
            items_with_base64[category].append(item_copy)
    
    # Convert items data to JSON for JavaScript
    items_json = json.dumps(items_with_base64)
    
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
                
                // Get background color for rarity
                let backgroundColor = 'white';
                if (item.background_color) {
                    backgroundColor = item.background_color;
                } else if (item.Rarity) {
                    // Fallback rarity colors
                    const rarityColors = {
                        'Common': '#f5f5f5',
                        'Uncommon': '#e8f5e8', 
                        'Rare': '#e8f0ff',
                        'Epic': '#f0e8ff',
                        'Legendary': '#fff0e8',
                        'Mythic': '#fffae8'
                    };
                    backgroundColor = rarityColors[item.Rarity] || 'white';
                }
                
                // Build image style with gradient if available
                let imageStyle = `background-color: ${backgroundColor};`;
                if (item.image_gradient) {
                    // Use the original gradient style from the wiki
                    imageStyle = item.image_gradient;
                } else {
                    // Create a dramatic gradient effect based on rarity color
                    const gradientColor = backgroundColor === 'white' ? '#f5f5f5' : backgroundColor;
                    if (gradientColor === '#f5f5f5') {
                        // For white/gray, create a light to dark gradient
                        imageStyle = `background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 50%, #c0c0c0 100%);`;
                    } else {
                        // For colored rarities, create a bright to dark gradient
                        imageStyle = `background: linear-gradient(135deg, ${gradientColor} 0%, ${gradientColor}80 50%, ${gradientColor}40 100%);`;
                    }
                }
                
                let imageHtml = '';
                if (item.image_base64) {
                    imageHtml = `<img src="data:image/png;base64,${item.image_base64}" alt="${name}" class="item-image" style="${imageStyle}">`;
                } else {
                    imageHtml = `<div class="no-image" style="${imageStyle}">No Image</div>`;
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
    # Create output directory if it doesn't exist
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    json_file = os.path.join(output_dir, 'items_data.json')
    html_file = os.path.join(output_dir, 'items.html')
    
    # Load items data
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            items_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_file} not found. Run scrape.py first.")
        return
    
    # Generate HTML with embedded images
    print("Embedding images as base64...")
    html_content = generate_html(items_data, output_dir)
    
    # Save to file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    total_items = sum(len(items) for items in items_data.values())
    file_size_mb = os.path.getsize(html_file) / (1024 * 1024)
    print(f"HTML page generated successfully!")
    print(f"Total items: {total_items}")
    print(f"Categories: {len(items_data)}")
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"Saved to: {html_file}")
    print(f"Open {html_file} in your browser to view the results.")
    print(f"\nNote: All images are embedded as base64 - this is a single self-contained file!")

if __name__ == "__main__":
    main()
