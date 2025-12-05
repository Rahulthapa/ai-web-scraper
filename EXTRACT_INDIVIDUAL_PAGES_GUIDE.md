# Extract Data from Individual Restaurant Pages

This guide shows you how to extract **complete detailed data** from individual restaurant pages, including full addresses, amenities, menu URLs, and other data that's only available on detail pages.

## 🎯 Problem Solved

**Listing pages** (like Yelp search results) often only have:
- Restaurant name
- Basic rating
- Partial address
- Basic info

**Individual restaurant pages** have:
- ✅ **Full addresses** (street, city, state, zip, country)
- ✅ **Complete amenities** (Wi-Fi, parking, outdoor seating, etc.)
- ✅ **All menu URLs** (main, lunch, dinner, brunch, drinks, online ordering)
- ✅ **Detailed hours** (all days, special hours)
- ✅ **Complete services** (reservations, delivery, catering)
- ✅ **Payment methods**
- ✅ **Photos, reviews, and more**

## 🚀 How to Use

### Method 1: Extract from Individual Pages Endpoint (New!)

**Best for:** When you already have a list of restaurants from a listing page

```bash
POST /extract-from-individual-pages
{
  "restaurants": [
    {
      "name": "Restaurant Name",
      "url": "https://www.yelp.com/biz/restaurant-name-houston",
      "rating": 4.5
    },
    {
      "name": "Another Restaurant",
      "url": "https://www.yelp.com/biz/another-restaurant-houston"
    }
  ],
  "use_javascript": true,
  "max_concurrent": 5,
  "ai_prompt": "Extract all restaurant data including addresses, amenities, menu URLs"
}
```

**Response:**
```json
{
  "success": true,
  "source": "individual_pages",
  "results": [
    {
      "name": "Restaurant Name",
      "address": "123 Main St, Houston, TX 77001",
      "address_parts": {
        "street_address": "123 Main St",
        "city": "Houston",
        "state": "TX",
        "zip_code": "77001"
      },
      "phone": "(713) 555-1234",
      "menu_urls": {
        "main_menu": "https://...",
        "lunch_menu": "https://...",
        "dinner_menu": "https://...",
        "online_ordering": "https://..."
      },
      "amenities": ["wifi", "parking", "outdoor_seating", "wheelchair_accessible"],
      // ... all other detailed data
    }
  ],
  "total_items": 2
}
```

### Method 2: Extract Internal Data with Individual Pages Option

**Best for:** Starting from a listing page URL

```bash
POST /extract-internal-data
{
  "url": "https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX",
  "extract_individual_pages": true,  // NEW OPTION!
  "wait_time": 5,
  "scroll": true,
  "ai_prompt": "Extract all restaurants with complete data"
}
```

This will:
1. Extract restaurants from the listing page
2. **Automatically visit each individual restaurant page**
3. Extract detailed data from each page
4. Merge listing data + individual page data

### Method 3: Two-Step Process

**Step 1:** Get restaurants from listing page
```bash
POST /extract-internal-data
{
  "url": "https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX"
}
```

**Step 2:** Extract from individual pages
```bash
POST /extract-from-individual-pages
{
  "restaurants": [/* restaurants from step 1 */],
  "use_javascript": true
}
```

## 📋 What Gets Extracted from Individual Pages

### Address Data
- ✅ Full formatted address
- ✅ Street address
- ✅ City, state, zip code
- ✅ Country
- ✅ GPS coordinates (if available)
- ✅ Neighborhood, area

### Menu URLs (All Types)
- ✅ Main menu
- ✅ Lunch menu
- ✅ Dinner menu
- ✅ Brunch menu
- ✅ Drinks menu
- ✅ Dessert menu
- ✅ Online ordering URL
- ✅ Delivery menu URL
- ✅ Takeout menu URL

### Amenities
- ✅ Wi-Fi availability
- ✅ Parking (valet, street, lot, garage)
- ✅ Outdoor seating, patio, terrace
- ✅ Wheelchair accessible
- ✅ Pet-friendly
- ✅ Live music
- ✅ TV screens
- ✅ Private dining rooms
- ✅ Event space
- ✅ And more...

### Services
- ✅ Reservations (accepted, required, online)
- ✅ Takeout available
- ✅ Delivery services
- ✅ Catering
- ✅ Private events
- ✅ Group dining

### Additional Data
- ✅ Complete opening hours
- ✅ Payment methods
- ✅ Photos (all URLs)
- ✅ Reviews and ratings
- ✅ Contact information
- ✅ Social media links
- ✅ Any other page-specific data

## 💡 Usage Examples

### Example 1: Extract from Yelp Listing

```python
import requests

# Step 1: Get restaurants from listing
response = requests.post("http://localhost:8000/extract-internal-data", json={
    "url": "https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX",
    "extract_individual_pages": True,  # Automatically extract from individual pages
    "wait_time": 5
})

data = response.json()
restaurants = data['results']

# Each restaurant now has complete data from individual pages!
for restaurant in restaurants:
    print(f"{restaurant['name']}")
    print(f"  Address: {restaurant.get('address')}")
    print(f"  Menu URLs: {restaurant.get('menu_urls')}")
    print(f"  Amenities: {restaurant.get('amenities')}")
```

### Example 2: Manual Two-Step Process

```python
# Step 1: Get listing data
response1 = requests.post("http://localhost:8000/extract-internal-data", json={
    "url": "https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX"
})

listing_restaurants = response1.json()['results']

# Step 2: Extract detailed data from individual pages
response2 = requests.post("http://localhost:8000/extract-from-individual-pages", json={
    "restaurants": listing_restaurants,
    "use_javascript": True,
    "max_concurrent": 5
})

detailed_restaurants = response2.json()['results']
```

## ⚙️ Configuration Options

### `use_javascript` (default: `true`)
- **true**: Uses Playwright to render JavaScript (slower but more accurate)
- **false**: Uses static HTML scraping (faster but may miss JS-loaded content)

### `max_concurrent` (default: `5`)
- Number of pages to process simultaneously
- Higher = faster but more server load
- Recommended: 3-10

### `ai_prompt` (optional)
- AI prompt to further structure/extract data
- Useful for extracting specific fields or formatting

## 🎯 Best Practices

1. **Start with listing page** → Get restaurant URLs
2. **Extract from individual pages** → Get complete data
3. **Use JavaScript rendering** → For modern SPAs (React, Vue)
4. **Limit concurrency** → Don't overwhelm servers (3-5 is safe)
5. **Add delays if needed** → Some sites rate-limit requests

## ⚠️ Important Notes

- **Rate Limiting**: Some sites may block too many requests. Use `max_concurrent: 3-5` to be safe.
- **JavaScript Required**: Many modern sites require JS rendering. Set `use_javascript: true`.
- **Time**: Extracting from individual pages takes longer (5-10 seconds per page).
- **URLs Required**: Restaurants must have a `url`, `website`, or `yelp_url` field.

## 🔍 Troubleshooting

### No URLs Found
- Make sure restaurants have `url`, `website`, or `yelp_url` field
- Check that listing page extraction found restaurant URLs

### Extraction Fails
- Try `use_javascript: true` for JS-rendered pages
- Increase `wait_time` if pages load slowly
- Check if site blocks automated access

### Missing Data
- Some data may not be available on individual pages
- Try different extraction methods (embedded JSON, HTML parsing, AI)
- Use comprehensive AI prompt to extract all available data

---

**Now you can extract complete restaurant data including full addresses, amenities, and all menu URLs!** 🎉

