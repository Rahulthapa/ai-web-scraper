# How Individual Page Scraping Works

This document explains the complete process of extracting data from individual restaurant pages.

## 🔄 Complete Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Get Restaurants from Listing Page                  │
│ (Yelp search, OpenTable, etc.)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Extract Restaurant URLs                             │
│ - Find 'url', 'website', or 'yelp_url' in each restaurant  │
│ - Filter out restaurants without URLs                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Process in Batches (Concurrent)                     │
│ - Split into groups of max_concurrent (default: 5)         │
│ - Process multiple pages simultaneously                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: For Each Individual Restaurant Page                 │
│                                                              │
│  4a. Get HTML Content                                       │
│      ├─ If use_javascript=True: Use Playwright             │
│      │  └─ Launch browser, load page, wait for JS          │
│      └─ Else: Use httpx (static HTML)                      │
│                                                              │
│  4b. Scrape Structured Data                                  │
│      └─ Extract title, links, images, text, etc.           │
│                                                              │
│  4c. Extract Embedded JSON                                   │
│      ├─ JSON-LD structured data (schema.org)               │
│      ├─ Yelp internal data (searchPageProps, etc.)         │
│      └─ Next.js data (__NEXT_DATA__)                       │
│                                                              │
│  4d. Extract Specific Data                                   │
│      ├─ Full address (from text patterns)                 │
│      ├─ Phone number (regex patterns)                       │
│      ├─ Menu URLs (from links containing "menu")           │
│      └─ Amenities (keyword matching in text)               │
│                                                              │
│  4e. Merge Data                                              │
│      └─ Combine listing data + individual page data        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Return Enhanced Restaurants                         │
│ - Each restaurant now has complete data                     │
│ - Listing data + Individual page data merged                │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Detailed Step-by-Step Process

### Step 1: Input - Restaurant List from Listing Page

**Input Example:**
```json
[
  {
    "name": "Taste of Texas",
    "url": "https://www.yelp.com/biz/taste-of-texas-houston",
    "rating": 4.5,
    "review_count": 1234
  },
  {
    "name": "Steak 48",
    "url": "https://www.yelp.com/biz/steak-48-houston",
    "rating": 4.7,
    "review_count": 890
  }
]
```

**What we have:**
- ✅ Restaurant names
- ✅ Basic URLs
- ✅ Basic ratings
- ❌ **Missing:** Full addresses, amenities, menu URLs

### Step 2: Extract URLs

**Code Logic:**
```python
for restaurant in restaurants:
    url = restaurant.get('url') or restaurant.get('website') or restaurant.get('yelp_url')
    if url:
        restaurant_urls.append((restaurant, url))
    else:
        # Skip restaurants without URLs
        logger.warning(f"No URL found for restaurant: {restaurant.get('name')}")
```

**Result:**
- List of (restaurant_data, url) tuples
- Restaurants without URLs are kept as-is (not processed)

### Step 3: Concurrent Processing Setup

**Code Logic:**
```python
# Create semaphore to limit concurrent requests
semaphore = asyncio.Semaphore(max_concurrent)  # Default: 5

# Create tasks for all restaurants
tasks = [
    extract_with_semaphore(restaurant, url) 
    for restaurant, url in restaurant_urls
]

# Execute all tasks concurrently (but limited by semaphore)
results = await asyncio.gather(*tasks)
```

**What happens:**
- Up to 5 pages processed simultaneously (configurable)
- Other pages wait in queue
- Prevents overwhelming the target server

### Step 4: Extract from Each Individual Page

For each restaurant page, the following happens:

#### 4a. Get HTML Content

**If `use_javascript=True` (default):**
```python
# Use Playwright to render JavaScript
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(url, wait_until="networkidle")
    await page.wait_for_timeout(2000)  # Wait for JS to load
    html_content = await page.content()  # Get fully rendered HTML
```

**If `use_javascript=False`:**
```python
# Use httpx for static HTML
async with httpx.AsyncClient() as client:
    response = await client.get(url)
    html_content = response.text
```

**Why both methods?**
- Playwright: Handles JavaScript-rendered content (React, Vue, etc.)
- httpx: Faster for static HTML pages

#### 4b. Scrape Structured Data

```python
page_data = await self.scrape(url, use_javascript=use_javascript)
```

**Extracts:**
- Page title
- All links
- Images
- Text content
- Meta tags
- Headings
- Tables, lists

#### 4c. Extract Embedded JSON

```python
soup = BeautifulSoup(html_content, 'html.parser')
embedded_data = self._extract_embedded_json(soup, url)
```

**Looks for:**
1. **JSON-LD** (`<script type="application/ld+json">`)
   - Schema.org structured data
   - Most reliable source
   - Contains: address, hours, menu, amenities

2. **Yelp Internal Data**
   - `searchPageProps`
   - `bizDetailsPageProps`
   - `legacyProps`

3. **Next.js Data**
   - `__NEXT_DATA__`
   - React app state

**Example JSON-LD found:**
```json
{
  "@type": "Restaurant",
  "name": "Taste of Texas",
  "address": {
    "streetAddress": "123 Main St",
    "addressLocality": "Houston",
    "addressRegion": "TX",
    "postalCode": "77001"
  },
  "openingHours": ["Mo-Sa 11:00-22:00"],
  "servesCuisine": ["Steakhouse", "American"]
}
```

#### 4d. Extract Specific Data from HTML

**Full Address Extraction:**
```python
# Pattern matching in text content
address_patterns = [
    r'\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave)[^,]*,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}',
    r'\d+[^,]+,\s*[^,]+,\s*[A-Z]{2}\s+\d{5}',
]
# Finds: "123 Main Street, Houston, TX 77001"
```

**Phone Number Extraction:**
```python
phone_pattern = r'(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
# Finds: "(713) 555-1234", "713-555-1234", etc.
```

**Menu URLs Extraction:**
```python
for link in structured_data.get('links', []):
    href = link.get('href', '').lower()
    text = link.get('text', '').lower()
    
    if 'menu' in href or 'menu' in text:
        if 'lunch' in href:
            menu_urls['lunch_menu'] = link.get('href')
        elif 'dinner' in href:
            menu_urls['dinner_menu'] = link.get('href')
        # ... etc
```

**Amenities Extraction:**
```python
amenities_keywords = {
    'wifi': ['wifi', 'wi-fi', 'wireless'],
    'parking': ['parking', 'valet', 'garage'],
    'outdoor_seating': ['outdoor', 'patio', 'terrace'],
    # ... etc
}

text_lower = structured_data.get('text_content', '').lower()
for amenity, keywords in amenities_keywords.items():
    if any(keyword in text_lower for keyword in keywords):
        amenities.append(amenity)
```

#### 4e. Merge Data

```python
# Start with listing data
detailed_restaurant = restaurant_data.copy()

# Add embedded JSON data (most reliable)
if embedded_data.get('restaurants'):
    detailed_restaurant.update(embedded_data['restaurants'][0])

# Add extracted specific data
detailed_restaurant['address'] = extracted_address
detailed_restaurant['phone'] = extracted_phone
detailed_restaurant['menu_urls'] = menu_urls
detailed_restaurant['amenities'] = amenities
```

**Result:**
- Listing data (name, rating) + Individual page data (address, amenities, menus)

### Step 5: Return Enhanced Restaurants

**Output Example:**
```json
[
  {
    "name": "Taste of Texas",  // From listing
    "rating": 4.5,              // From listing
    "url": "https://...",       // From listing
    
    "address": "123 Main St, Houston, TX 77001",  // NEW from individual page!
    "address_parts": {          // NEW!
      "street_address": "123 Main St",
      "city": "Houston",
      "state": "TX",
      "zip_code": "77001"
    },
    "phone": "(713) 555-1234",  // NEW!
    "menu_urls": {              // NEW!
      "main_menu": "https://...",
      "lunch_menu": "https://...",
      "dinner_menu": "https://..."
    },
    "amenities": [              // NEW!
      "wifi",
      "parking",
      "outdoor_seating"
    ],
    "opening_hours": [...]      // NEW!
  }
]
```

## ⚙️ Configuration Options

### `use_javascript` (default: `true`)
- **true**: Uses Playwright to render JavaScript
  - Slower (~5-10 seconds per page)
  - More accurate (gets JS-loaded content)
  - Required for React/Vue/Angular sites
  
- **false**: Uses static HTML scraping
  - Faster (~1-2 seconds per page)
  - May miss JS-loaded content
  - Good for static HTML sites

### `max_concurrent` (default: `5`)
- Number of pages processed simultaneously
- **Higher (10-20)**: Faster but may trigger rate limiting
- **Lower (3-5)**: Slower but safer, less likely to be blocked
- **Recommended**: 5 for most sites

## 🔍 Data Extraction Priority

When extracting from individual pages, data is merged in this order:

1. **Embedded JSON-LD** (highest priority)
   - Most reliable, structured data
   - Schema.org standard
   
2. **Yelp/OpenTable Internal Data**
   - Site-specific structured data
   - Very reliable for those sites
   
3. **HTML Pattern Matching**
   - Address patterns
   - Phone patterns
   - Menu URL extraction
   
4. **Text Content Analysis**
   - Amenities keyword matching
   - General text extraction

## ⏱️ Time Estimates

**Per Restaurant Page:**
- With JavaScript: ~5-10 seconds
- Without JavaScript: ~1-2 seconds

**For 10 Restaurants:**
- With JavaScript (concurrent=5): ~10-20 seconds
- Without JavaScript (concurrent=5): ~2-4 seconds

## 🛡️ Error Handling

**If a page fails:**
- Error is logged
- Original restaurant data is returned (not lost)
- Processing continues for other restaurants
- No data is lost if one page fails

**Common failures:**
- Page blocked by anti-bot protection
- Page requires login
- Page doesn't exist (404)
- Network timeout

## 📊 Example: Complete Flow

**Input (from listing page):**
```json
[
  {"name": "Restaurant A", "url": "https://yelp.com/biz/a", "rating": 4.5},
  {"name": "Restaurant B", "url": "https://yelp.com/biz/b", "rating": 4.7}
]
```

**Process:**
1. Extract URLs: ✅ Both have URLs
2. Process concurrently: 2 pages at once
3. For Restaurant A:
   - Load page with Playwright
   - Extract JSON-LD: Full address, hours, menu
   - Extract from HTML: Phone, amenities
   - Merge data
4. For Restaurant B:
   - Same process
5. Return enhanced data

**Output:**
```json
[
  {
    "name": "Restaurant A",
    "rating": 4.5,
    "address": "123 Main St, Houston, TX 77001",  // NEW!
    "phone": "(713) 555-1234",                     // NEW!
    "menu_urls": {...},                            // NEW!
    "amenities": [...]                             // NEW!
  },
  {
    "name": "Restaurant B",
    "rating": 4.7,
    "address": "456 Oak Ave, Houston, TX 77002",  // NEW!
    // ... all new data
  }
]
```

## 🎯 Key Benefits

1. **Complete Data**: Gets full addresses, not partial
2. **All Menu URLs**: Finds all menu types (lunch, dinner, etc.)
3. **Complete Amenities**: Extracts all available amenities
4. **Concurrent Processing**: Fast (5 pages at once)
5. **Error Resilient**: Continues even if some pages fail
6. **Data Merging**: Combines listing + individual page data

---

**This process ensures you get complete restaurant data that's only available on individual pages!** 🎉

