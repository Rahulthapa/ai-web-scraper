# Restaurant Data Extraction Guide

This guide shows you how to extract comprehensive internal restaurant data using the AI Web Scraper.

## 🍽️ What Data Can Be Extracted

The scraper now extracts **comprehensive internal restaurant data** including:

### Basic Information
- Name, description, website URL
- Images and photos
- Business type and category

### Contact Details
- Phone number (formatted and raw)
- Email address
- Website URL

### Location Data
- Full formatted address
- Address components (street, city, state, zip, country)
- GPS coordinates (latitude/longitude)

### Ratings & Reviews
- Rating (1-5 stars)
- Review count
- Best/worst rating scale

### Restaurant-Specific
- Cuisine types (list)
- Price range ($, $$, $$$, $$$$)
- Menu URL
- Accepts reservations
- Opening hours (structured)
- Special hours
- Offers/deals/prices

### Additional Metadata
- Payment methods accepted
- Currencies accepted
- Number of employees
- Founding date
- Business attributes

---

## 📋 How to Extract Restaurant Data

### Method 1: Using AI Prompt (Recommended)

**Best for:** Any restaurant listing page (Yelp, Google Maps, TripAdvisor, etc.)

1. **Paste HTML Mode** (Most Reliable):
   - Open the restaurant listing page in your browser
   - Press `Ctrl+U` to view page source
   - Copy all HTML (`Ctrl+A`, `Ctrl+C`)
   - Paste into the "Paste HTML" tab
   - Use this AI prompt:

```
Extract all restaurants with their complete internal data including:
- Name, address (full and parts), phone, website
- Rating, review count
- Cuisine types, price range
- Opening hours, menu URL
- GPS coordinates, images
- Any offers or deals
Return as a JSON array with all available fields for each restaurant.
```

2. **URL Mode**:
   - Enter the restaurant listing URL
   - Enable "JavaScript rendering" if needed
   - Use the same AI prompt above

3. **Crawl Mode**:
   - Enter search query: `"steakhouses in Houston, TX"`
   - Set max pages (e.g., 10)
   - Use the AI prompt above

### Method 2: Using Yelp API (Official)

**Best for:** Yelp data with official API access

```bash
# API Endpoint
GET /api/yelp/search?term=steakhouse&location=Houston,TX&limit=20

# Returns structured Yelp data with all internal fields
```

### Method 3: Automatic Detection

**Best for:** Yelp, OpenTable, TripAdvisor pages

The scraper automatically detects restaurant listing pages and extracts:
- Embedded JSON-LD data (schema.org)
- Yelp-specific data structures
- OpenTable restaurant data
- Pattern-based extraction from HTML

Just scrape the URL - no AI prompt needed!

---

## 🎯 Example AI Prompts for Restaurant Extraction

### Comprehensive Extraction
```
Extract all restaurants with complete internal data: name, full address with city/state/zip, phone, website, rating, review count, cuisine types, price range, opening hours, menu URL, GPS coordinates, and images. Return as structured JSON.
```

### Specific Fields Only
```
Extract restaurant names, addresses, phone numbers, ratings, and price ranges. Return as a clean list.
```

### With Filters
```
Extract all restaurants with rating above 4.0, include their names, addresses, phone numbers, and cuisine types.
```

### Detailed Business Info
```
Extract restaurants with all available details: contact info, location (including coordinates), hours of operation, menu links, payment methods, and any special offers or deals.
```

---

## 📊 Output Format

### Example Restaurant Data Structure

```json
{
  "name": "Taste of Texas",
  "description": "Premium steakhouse...",
  "url": "https://yelp.com/biz/taste-of-texas",
  "image": "https://...",
  
  "phone": "(713) 555-1234",
  "email": "info@tasteoftexas.com",
  "website": "https://tasteoftexas.com",
  
  "address": "123 Main St, Houston, TX 77001",
  "address_parts": {
    "street_address": "123 Main St",
    "city": "Houston",
    "state": "TX",
    "postal_code": "77001",
    "country": "US"
  },
  "latitude": 29.7604,
  "longitude": -95.3698,
  
  "rating": 4.5,
  "review_count": 1234,
  "best_rating": 5,
  "worst_rating": 1,
  
  "cuisine": ["Steakhouse", "American", "Fine Dining"],
  "price_range": "$$$",
  "accepts_reservations": true,
  "menu_url": "https://...",
  
  "opening_hours": [
    {
      "day": "Monday",
      "opens": "11:00",
      "closes": "22:00"
    }
  ],
  
  "offers": {
    "price": "$50",
    "price_currency": "USD",
    "availability": "InStock"
  },
  
  "payment_accepted": ["Cash", "Credit Card"],
  "currencies_accepted": "USD"
}
```

---

## 🔧 Technical Details

### Data Sources (Priority Order)

1. **JSON-LD Structured Data** (schema.org)
   - Most reliable, standardized format
   - Extracted from `<script type="application/ld+json">` tags

2. **Yelp Internal Data**
   - Extracted from Yelp's JavaScript hydration
   - Includes: `searchPageProps`, `bizDetailsPageProps`

3. **Embedded JSON**
   - Next.js `__NEXT_DATA__`
   - Generic JSON patterns in script tags

4. **HTML Pattern Matching**
   - Fallback for pages without structured data
   - Extracts from headings, links, images

### Supported Sites

✅ **Fully Supported:**
- Yelp (scraping + API)
- OpenTable
- Google Maps (via search)
- TripAdvisor
- Any site with JSON-LD schema

✅ **Partially Supported:**
- Yellow Pages
- Zomato
- Foursquare
- Generic restaurant listing pages

---

## 💡 Tips for Best Results

1. **Use HTML Paste Mode** for sites with anti-bot protection
2. **Enable JavaScript Rendering** for SPAs (React/Vue sites)
3. **Be Specific in AI Prompts** - mention exact fields you need
4. **Use Yelp API** when available (more reliable, official data)
5. **Check Embedded Data** - many sites include JSON-LD which is automatically extracted

---

## 🚀 Quick Start Examples

### Example 1: Extract from Yelp Search Page

```
1. Go to: https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX
2. Copy page source (Ctrl+U, Ctrl+A, Ctrl+C)
3. Paste HTML in scraper
4. AI Prompt: "Extract all restaurants with complete data"
```

### Example 2: Use Yelp API

```bash
curl "http://localhost:8000/api/yelp/search?term=steakhouse&location=Houston,TX&limit=20"
```

### Example 3: Crawl Multiple Pages

```
1. Mode: Crawl
2. Search: "best restaurants in Houston"
3. Max Pages: 10
4. AI Prompt: "Extract restaurant names, addresses, ratings, and cuisine types"
```

---

## 📝 Notes

- All extracted data is automatically saved to Supabase
- Export formats: JSON, CSV, Excel
- Data is normalized across different sources
- GPS coordinates available when provided by source
- Opening hours parsed into structured format when available

