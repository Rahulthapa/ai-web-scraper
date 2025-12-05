# API Usage Guide

## 🔧 How to Use the Extract Internal Data Endpoint

The `/extract-internal-data` endpoint requires a **POST** request, not GET. When you type a URL in a browser, it sends a GET request, which is why you see "Method Not Allowed".

### ✅ **Correct Usage:**

#### Option 1: Using cURL (Command Line)

```bash
curl -X POST https://ai-web-scraper-7ctv.onrender.com/extract-internal-data \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX",
    "extract_individual_pages": true,
    "wait_time": 5,
    "scroll": true
  }'
```

#### Option 2: Using JavaScript/Fetch

```javascript
fetch('https://ai-web-scraper-7ctv.onrender.com/extract-internal-data', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX',
    extract_individual_pages: true,
    wait_time: 5,
    scroll: true,
    ai_prompt: 'Extract all restaurants with complete data'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Option 3: Using Python requests

```python
import requests

response = requests.post(
    'https://ai-web-scraper-7ctv.onrender.com/extract-internal-data',
    json={
        'url': 'https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX',
        'extract_individual_pages': True,
        'wait_time': 5,
        'scroll': True,
        'ai_prompt': 'Extract all restaurants with complete data'
    }
)

data = response.json()
print(data)
```

#### Option 4: Using Postman

1. Open Postman
2. Set method to **POST**
3. URL: `https://ai-web-scraper-7ctv.onrender.com/extract-internal-data`
4. Headers: `Content-Type: application/json`
5. Body (raw JSON):
```json
{
  "url": "https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX",
  "extract_individual_pages": true,
  "wait_time": 5,
  "scroll": true
}
```

### 📋 **Endpoint Information:**

**GET** `/extract-internal-data` - Shows usage information (what you see in browser)

**POST** `/extract-internal-data` - Actually extracts data (requires JSON body)

### 🔍 **Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | ✅ Yes | - | URL to extract internal data from |
| `wait_time` | integer | ❌ No | 5 | Seconds to wait for data to load |
| `scroll` | boolean | ❌ No | true | Scroll page to trigger lazy loading |
| `intercept_network` | boolean | ❌ No | true | Intercept API calls |
| `extract_individual_pages` | boolean | ❌ No | false | Extract from individual restaurant pages |
| `ai_prompt` | string | ❌ No | null | AI extraction prompt |

### 📝 **Example Request:**

```json
{
  "url": "https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX",
  "wait_time": 5,
  "scroll": true,
  "intercept_network": true,
  "extract_individual_pages": true,
  "ai_prompt": "Extract all restaurants with complete data including addresses, amenities, and menu URLs"
}
```

### 📤 **Example Response:**

```json
{
  "success": true,
  "source": "internal_data",
  "extraction_method": "JavaScript rendering + network interception",
  "results": [
    {
      "name": "Restaurant Name",
      "address": "123 Main St, Houston, TX 77001",
      "rating": 4.5,
      "menu_urls": {...},
      "amenities": [...]
    }
  ],
  "total_items": 20
}
```

### 🧪 **Quick Test:**

Visit in browser (GET request - shows info):
```
https://ai-web-scraper-7ctv.onrender.com/extract-internal-data
```

Use POST request (actual extraction):
```bash
curl -X POST https://ai-web-scraper-7ctv.onrender.com/extract-internal-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.yelp.com/search?find_desc=steakhouse&find_loc=Houston,TX"}'
```

---

## 🎯 **Other Endpoints:**

### `/extract-from-individual-pages` (POST)
Extract detailed data from individual restaurant pages.

### `/parse-html` (POST)
Parse pasted HTML content.

### `/jobs` (POST)
Create a scraping job (URL or Crawl mode).

### `/docs` (GET)
FastAPI automatic API documentation (Swagger UI).

---

**Note:** Most endpoints require POST method with JSON body. Use the frontend interface, Postman, curl, or your programming language's HTTP client.

