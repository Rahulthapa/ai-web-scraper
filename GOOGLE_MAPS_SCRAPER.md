# Google Maps Business Scraper

This module provides a Python/Playwright implementation for scraping business listings from Google Maps, adapted from the original Node.js/Puppeteer code.

## Features

- Scrapes Google Maps search results for businesses
- Extracts comprehensive business information:
  - Basic info (name, address, phone, website)
  - Ratings and reviews
  - Price range
  - Location (latitude/longitude)
  - Additional details from business websites
  - Yelp and OpenTable data when available
- Exports to CSV with all required fields
- Handles errors gracefully with retries
- Respects rate limits with configurable delays

## Installation

Make sure you have Playwright installed:

```bash
pip install playwright
playwright install chromium
```

## Usage

### Standalone Script

Run the standalone script:

```bash
python scrape_steakhouses.py
```

This will:
- Search for "steakhouse houston tx" on Google Maps
- Scrape up to 120 listings
- Save results to `steakhouses_houston.csv`

### Python Code

```python
import asyncio
from app.google_maps_scraper import GoogleMapsScraper

async def main():
    async with GoogleMapsScraper(
        max_listings=50,
        headless=True,
        wait_between_actions_ms=1200
    ) as scraper:
        results = await scraper.scrape('steakhouse houston tx', 'output.csv')
        print(f"Scraped {len(results)} listings")

asyncio.run(main())
```

### Integration with Existing App

You can integrate this into your existing scraper by:

1. **Adding a new job type** - Create a "Google Maps" scraping mode
2. **Using in worker** - Call the scraper from `app/worker.py`
3. **API endpoint** - Add a new endpoint for Google Maps scraping

Example integration:

```python
# In app/worker.py
from app.google_maps_scraper import GoogleMapsScraper

async def process_google_maps_job(self, job_id: str, search_query: str):
    async with GoogleMapsScraper(max_listings=job.get('max_pages', 50)) as scraper:
        results = await scraper.scrape(search_query)
        # Save results to database
        await self.storage.save_results(job_id, results)
```

## Configuration

The `GoogleMapsScraper` accepts these parameters:

- `max_listings` (int): Maximum number of listings to scrape (default: 120)
- `headless` (bool): Run browser in headless mode (default: True)
- `slow_mo` (int): Slow down operations by milliseconds (default: 0)
- `wait_between_actions_ms` (int): Base wait time between actions (default: 1200)

## Output Format

The scraper outputs CSV files with these columns:

- ID, Title, Slug, Content, Excerpt
- Post Status, Post Date, Featured Image URL
- Location, Address, Phone, Website, Email
- Rating, Price Range, Latitude, Longitude
- Diners Choice, Top Rated, Outdoor Dining
- Neighborhood, Dress Code, Chef Bio
- Gift Card URL, Private Dining Email/Phone
- Video URL, Phone Number (ACF)
- Parking, Payment Method, Noise
- Executive Chef, Cross Street
- Google Business Link
- Categories, Tags, Cuisines

## Notes

- **Rate Limiting**: The scraper includes delays between requests to avoid being blocked
- **Error Handling**: Failed listings are logged but don't stop the entire process
- **Data Quality**: Some fields may be empty if not available on the source pages
- **Legal**: Always respect website terms of service and robots.txt
- **Scaling**: For large-scale scraping, consider using proxies and rotating user agents

## Troubleshooting

### Browser not found
```bash
playwright install chromium
```

### Timeout errors
Increase timeout values or check your internet connection

### Empty results
- Google Maps may have changed their HTML structure
- Try running with `headless=False` to see what's happening
- Check if you're being blocked (captcha, rate limiting)

### Missing data
Some fields require visiting external sites (Yelp, OpenTable, business websites). These may fail if:
- The site is down
- The site blocks automated access
- The links aren't available on Google Maps

## Differences from Original Node.js Code

- Uses Python/Playwright instead of Node.js/Puppeteer
- Integrated with existing Python app architecture
- Can be used as a module or standalone script
- Better error handling and logging
- CSV writing is built-in

