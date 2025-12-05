# Which Scraping Process Uses Individual Page Extraction?

## ✅ **Now Integrated Into ALL Processes!**

Individual page extraction is now available in **ALL three scraping modes**:

### 1. ✅ **URL Scraping** (`/jobs` POST - Single URL)

**How to use:**
```json
POST /jobs
{
  "url": "https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX",
  "use_javascript": true,
  "extract_individual_pages": true,  // NEW!
  "ai_prompt": "Extract all restaurants with complete data"
}
```

**Process Flow:**
1. Scrapes the listing page URL
2. Extracts restaurants from the page
3. **Automatically visits each individual restaurant page** (if `extract_individual_pages: true`)
4. Extracts detailed data (addresses, amenities, menu URLs)
5. Merges listing data + individual page data
6. Returns complete restaurant data

---

### 2. ✅ **Crawl Mode** (`/jobs` POST - Crawl)

**How to use:**
```json
POST /jobs
{
  "search_query": "steakhouses in Houston, TX",
  "crawl_mode": true,
  "max_pages": 10,
  "use_javascript": true,
  "extract_individual_pages": true,  // NEW!
  "ai_prompt": "Extract all restaurants"
}
```

**Process Flow:**
1. Crawls multiple listing pages based on search query
2. Extracts restaurants from all crawled pages
3. **Automatically visits each individual restaurant page** (if `extract_individual_pages: true`)
4. Extracts detailed data from each individual page
5. Merges all data together
6. Returns complete restaurant data

---

### 3. ✅ **Paste HTML** (`/parse-html` POST)

**How to use:**
```json
POST /parse-html
{
  "html": "<html>...pasted HTML from listing page...</html>",
  "extract_individual_pages": true,  // NEW!
  "ai_prompt": "Extract all restaurants with complete data"
}
```

**Process Flow:**
1. Parses the pasted HTML
2. Extracts restaurants from embedded JSON/HTML
3. **Automatically visits each individual restaurant page** (if `extract_individual_pages: true`)
4. Extracts detailed data from each individual page
5. Merges listing data + individual page data
6. Returns complete restaurant data

---

## 🔄 Complete Process Flow (All Modes)

```
┌─────────────────────────────────────────┐
│ Step 1: Scrape Listing Page            │
│ (URL / Crawl / Paste HTML)             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Step 2: Extract Restaurants            │
│ - From embedded JSON                   │
│ - From HTML patterns                   │
│ - From AI extraction                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Step 3: Check extract_individual_pages │
│ If true → Continue to Step 4           │
│ If false → Skip to Step 6              │
└──────────────┬──────────────────────────┘
               │
               ▼ (if extract_individual_pages = true)
┌─────────────────────────────────────────┐
│ Step 4: Extract URLs from Restaurants  │
│ - Find 'url', 'website', 'yelp_url'    │
│ - Filter restaurants with URLs          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Step 5: Visit Individual Pages         │
│ - Process 5 pages concurrently         │
│ - Extract detailed data from each       │
│   • Full addresses                      │
│   • All menu URLs                       │
│   • Complete amenities                  │
│   • Hours, services, etc.               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Step 6: Merge Data                      │
│ - Listing data + Individual page data  │
│ - Prioritize individual page data      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Step 7: Apply AI Filter (if prompt)    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Step 8: Return Complete Data           │
└─────────────────────────────────────────┘
```

## 📋 Summary Table

| Process | Endpoint | Individual Pages Option | Status |
|---------|----------|------------------------|--------|
| **URL Scraping** | `POST /jobs` | `extract_individual_pages: true` | ✅ **Integrated** |
| **Crawl Mode** | `POST /jobs` (with `crawl_mode: true`) | `extract_individual_pages: true` | ✅ **Integrated** |
| **Paste HTML** | `POST /parse-html` | `extract_individual_pages: true` | ✅ **Integrated** |
| **Extract Internal Data** | `POST /extract-internal-data` | `extract_individual_pages: true` | ✅ **Already had it** |
| **Extract Individual Pages** | `POST /extract-from-individual-pages` | N/A (dedicated endpoint) | ✅ **Standalone** |

## 🎯 When to Use Individual Page Extraction

### ✅ **Use it when:**
- You need **complete addresses** (not just partial)
- You need **all menu URLs** (lunch, dinner, brunch, etc.)
- You need **complete amenities list**
- You're scraping restaurant listing pages (Yelp, OpenTable, etc.)
- You want the most comprehensive data possible

### ❌ **Don't use it when:**
- You're scraping a single restaurant page (already has all data)
- You don't need detailed data (just names/ratings)
- Speed is critical (adds 5-10 seconds per restaurant)
- You're hitting rate limits (visits many pages)

## ⚙️ Configuration

**All processes support:**
```json
{
  "extract_individual_pages": true,  // Enable individual page extraction
  "use_javascript": true,            // Use Playwright (recommended for individual pages)
  "ai_prompt": "..."                 // Optional: AI extraction prompt
}
```

## 💡 Example: Complete Workflow

### URL Scraping with Individual Pages

```bash
# 1. Create job with individual page extraction
POST /jobs
{
  "url": "https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX",
  "use_javascript": true,
  "extract_individual_pages": true,
  "ai_prompt": "Extract all restaurants with complete data"
}

# 2. Job processes:
#    - Scrapes listing page
#    - Finds 20 restaurants
#    - Visits each individual page (5 at a time)
#    - Extracts detailed data
#    - Merges all data

# 3. Get results
GET /jobs/{job_id}/results

# Returns complete restaurant data with:
# - Full addresses
# - All menu URLs
# - Complete amenities
# - Everything from individual pages
```

---

**Now ALL scraping processes can extract complete data from individual restaurant pages!** 🎉

