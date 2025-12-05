# Restaurant Data Extraction - Wireframe & Workflow

## 🎯 **Your Requested Process**

You want a **two-step process**:
1. **Step 1:** Get restaurant URLs from listing page
2. **Step 2:** Visit each individual restaurant page and extract ALL data
3. **Step 3:** Combine all data into one list
4. **Step 4:** Export to CSV/Excel

---

## 📊 **Wireframe Diagram**

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT                                    │
│                                                                   │
│  Enter Listing Page URL:                                         │
│  [https://www.yelp.com/search?find_desc=steakhouse&find_loc=...]│
│                                                                   │
│  ☑ Extract from individual pages (ALWAYS ON for this mode)      │
│                                                                   │
│  [Start Extraction]                                               │
└───────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STEP 1: GET RESTAURANT URLs                  │
│                                                                   │
│  Scraping: https://www.yelp.com/search?...                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Extracting restaurant URLs from listing page...          │   │
│  │                                                           │   │
│  │ Found:                                                    │   │
│  │ • https://yelp.com/biz/restaurant-1                       │   │
│  │ • https://yelp.com/biz/restaurant-2                       │   │
│  │ • https://yelp.com/biz/restaurant-3                       │   │
│  │ ...                                                       │   │
│  │ Total: 20 restaurant URLs found                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 2: VISIT EACH INDIVIDUAL PAGE                  │
│                                                                   │
│  Processing: 20 restaurants                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │  [1/20] Visiting: Restaurant 1                          │   │
│  │  ┌─────────────────────────────────────────────────┐     │   │
│  │  │ Extracting from:                                │     │   │
│  │  │ https://yelp.com/biz/restaurant-1               │     │   │
│  │  │                                                 │     │   │
│  │  │ ✅ Full Address                                 │     │   │
│  │  │ ✅ Phone Number                                 │     │   │
│  │  │ ✅ All Menu URLs                                │     │   │
│  │  │ ✅ Amenities                                    │     │   │
│  │  │ ✅ Hours                                        │     │   │
│  │  │ ✅ Services                                     │     │   │
│  │  │ ✅ Payment Methods                             │     │   │
│  │  │ ✅ Photos                                       │     │   │
│  │  │ ✅ Everything from this page                   │     │   │
│  │  └─────────────────────────────────────────────────┘     │   │
│  │                                                           │   │
│  │  [2/20] Visiting: Restaurant 2                          │   │
│  │  [3/20] Visiting: Restaurant 3                          │   │
│  │  ...                                                     │   │
│  │                                                           │   │
│  │  Progress: ████████████░░░░░░░░ 12/20 (60%)             │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STEP 3: COMBINE ALL DATA                      │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Combining data from all 20 restaurants...               │   │
│  │                                                           │   │
│  │ Restaurant 1: ✅ Complete                                │   │
│  │ Restaurant 2: ✅ Complete                                │   │
│  │ Restaurant 3: ✅ Complete                                │   │
│  │ ...                                                       │   │
│  │                                                           │   │
│  │ All data merged successfully!                           │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STEP 4: EXPORT RESULTS                        │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │  ✅ Extraction Complete!                                 │   │
│  │                                                           │   │
│  │  Total Restaurants: 20                                    │   │
│  │  Data Extracted:                                         │   │
│  │    • Full Addresses: 20/20                               │   │
│  │    • Phone Numbers: 20/20                                 │   │
│  │    • Menu URLs: 20/20                                    │   │
│  │    • Amenities: 20/20                                    │   │
│  │    • Hours: 20/20                                        │   │
│  │                                                           │   │
│  │  [Download JSON]  [Download CSV]  [Download Excel]      │   │
│  │                                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 **Detailed Process Flow**

```
┌──────────────────────────────────────────────────────────────┐
│ PHASE 1: URL EXTRACTION                                      │
│                                                              │
│ Input: Listing Page URL                                      │
│        (e.g., Yelp search results)                          │
│                                                              │
│ Process:                                                     │
│  1. Load listing page                                        │
│  2. Extract embedded JSON (restaurant URLs)                │
│  3. Extract from HTML links                                  │
│  4. Extract from JavaScript variables                        │
│                                                              │
│ Output: List of Restaurant URLs                             │
│         [url1, url2, url3, ..., url20]                      │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ PHASE 2: INDIVIDUAL PAGE EXTRACTION                          │
│                                                              │
│ For each URL in list:                                        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Visit: https://yelp.com/biz/restaurant-1            │    │
│  │                                                      │    │
│  │ Extract:                                            │    │
│  │  • JSON-LD structured data                         │    │
│  │  • Embedded JSON (Yelp internal data)              │    │
│  │  • HTML patterns (address, phone)                  │    │
│  │  • Links (menu URLs)                                │    │
│  │  • Text content (amenities, hours)                  │    │
│  │                                                      │    │
│  │ Result: Complete restaurant object                  │    │
│  │ {                                                    │    │
│  │   name, address, phone, menu_urls,                  │    │
│  │   amenities, hours, services, ...                   │    │
│  │ }                                                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Process 5 pages concurrently                                │
│  Continue until all URLs processed                          │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ PHASE 3: DATA COMBINATION                                     │
│                                                              │
│ Input: Array of restaurant objects                          │
│        [restaurant1, restaurant2, ..., restaurant20]        │
│                                                              │
│ Process:                                                     │
│  • Merge all restaurant objects                             │
│  • Ensure consistent structure                              │
│  • Handle missing data gracefully                           │
│                                                              │
│ Output: Combined list                                        │
│         [all restaurants with complete data]                │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ PHASE 4: EXPORT                                               │
│                                                              │
│ Format Options:                                              │
│  • JSON - Raw data structure                                 │
│  • CSV - Spreadsheet format                                  │
│  • Excel - .xlsx file with formatting                       │
│                                                              │
│ Each row = One restaurant                                    │
│ Each column = One data field                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 **Data Structure Example**

### What We Extract from Each Individual Page:

```json
{
  "name": "Taste of Texas",
  "url": "https://yelp.com/biz/taste-of-texas-houston",
  
  "address": "10505 Katy Fwy, Houston, TX 77024",
  "address_parts": {
    "street_address": "10505 Katy Fwy",
    "city": "Houston",
    "state": "TX",
    "zip_code": "77024",
    "country": "US"
  },
  
  "phone": "(713) 932-6901",
  "email": "info@tasteoftexas.com",
  "website": "https://tasteoftexas.com",
  
  "rating": 4.5,
  "review_count": 1234,
  
  "menu_urls": {
    "main_menu": "https://tasteoftexas.com/menu",
    "lunch_menu": "https://tasteoftexas.com/lunch",
    "dinner_menu": "https://tasteoftexas.com/dinner",
    "brunch_menu": "https://tasteoftexas.com/brunch",
    "drinks_menu": "https://tasteoftexas.com/drinks",
    "online_ordering": "https://tasteoftexas.com/order",
    "delivery_menu": "https://doordash.com/..."
  },
  
  "amenities": [
    "wifi",
    "parking",
    "outdoor_seating",
    "wheelchair_accessible",
    "pet_friendly",
    "live_music",
    "tv",
    "private_dining"
  ],
  
  "opening_hours": [
    {"day": "Monday", "opens": "11:00", "closes": "22:00"},
    {"day": "Tuesday", "opens": "11:00", "closes": "22:00"},
    // ... all days
  ],
  
  "services": {
    "reservations": true,
    "takeout": true,
    "delivery": ["DoorDash", "Uber Eats"],
    "catering": true,
    "private_events": true
  },
  
  "payment_methods": ["Cash", "Credit Card", "Apple Pay"],
  
  "cuisine": ["Steakhouse", "American", "Fine Dining"],
  "price_range": "$$$",
  
  "photos": [
    "https://yelp.com/photo1.jpg",
    "https://yelp.com/photo2.jpg",
    // ... all photos
  ],
  
  // ... any other data available on the page
}
```

---

## 🎯 **Key Points**

### ✅ **What We Do:**
1. **Step 1:** Extract restaurant URLs from listing page
2. **Step 2:** Visit each individual restaurant page
3. **Step 3:** Extract ALL data from each individual page
4. **Step 4:** Combine into one list
5. **Step 5:** Export to CSV/Excel

### ❌ **What We DON'T Do:**
- We DON'T extract data from the listing page (except URLs)
- We ONLY use listing page to get restaurant URLs
- ALL actual data comes from individual pages

### 🔑 **Key Difference:**
- **Old approach:** Extract from listing page → limited data
- **New approach:** Get URLs → Visit each page → Complete data

---

## 📊 **CSV/Excel Output Structure**

| Name | Address | City | State | Zip | Phone | Main Menu URL | Lunch Menu URL | Dinner Menu URL | Online Ordering | Wi-Fi | Parking | Outdoor Seating | Hours Mon | Hours Tue | ... |
|------|---------|------|-------|-----|-------|---------------|----------------|-----------------|-----------------|-------|---------|-----------------|-----------|-----------|-----|
| Restaurant 1 | 123 Main St | Houston | TX | 77001 | (713) 555-1234 | https://... | https://... | https://... | https://... | Yes | Yes | Yes | 11:00-22:00 | 11:00-22:00 | ... |
| Restaurant 2 | 456 Oak Ave | Houston | TX | 77002 | (713) 555-5678 | https://... | https://... | https://... | https://... | Yes | No | Yes | 10:00-21:00 | 10:00-21:00 | ... |

---

## ⏱️ **Time Estimate**

- **Step 1 (Get URLs):** ~10 seconds
- **Step 2 (Visit 20 pages):** ~2-3 minutes (5 pages at a time)
- **Step 3 (Combine):** ~1 second
- **Step 4 (Export):** ~1 second

**Total:** ~2-4 minutes for 20 restaurants

---

## ✅ **Confirmation**

**Is this correct?**
- ✅ Get restaurant URLs from listing page
- ✅ Visit each individual restaurant page
- ✅ Extract ALL data from each individual page (not from listing)
- ✅ Combine all data into one list
- ✅ Export to CSV/Excel

**If yes, I'll implement this exact workflow!**

