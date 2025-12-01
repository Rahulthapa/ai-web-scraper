# Production Web Scraper

Enterprise-grade, fault-tolerant, scalable web data extraction system.

## Features

- ✅ **Multi-source scraping**: Google Maps, Yelp, OpenTable, Official Websites
- ✅ **Strict CSV output**: RFC-4180 compliant with exact column ordering
- ✅ **Robots.txt compliance**: Automatic enforcement
- ✅ **Rate limiting**: Configurable delays and retries
- ✅ **Error handling**: CAPTCHA detection, bot challenges, graceful failures
- ✅ **Data normalization**: Merges data from multiple sources
- ✅ **Stable ID generation**: SHA256-based entity identification
- ✅ **Structured logging**: Rich console output and file logging

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

1. **Install Python dependencies:**

```bash
cd scraper
pip install -r requirements.txt
```

2. **Install Playwright browsers:**

```bash
playwright install chromium
```

## Quick Start

### Search Mode (Recommended)

Search for businesses and scrape results:

```bash
python -m scraper.main --mode search --query "steakhouses in Houston Texas" --output results.csv
```

### Single URL Mode

Scrape a specific URL:

```bash
python -m scraper.main --mode single-url --url "https://www.google.com/maps/place/..." --output result.csv
```

### List from File Mode

Scrape multiple URLs from a file:

```bash
# Create urls.txt with one URL per line
python -m scraper.main --mode list-from-file --file urls.txt --output results.csv
```

## Configuration

### Command Line Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--mode` | Scraping mode: `single-url`, `list-from-file`, or `search` | Yes |
| `--url` | URL to scrape (single-url mode) | If mode=single-url |
| `--file` | File with URLs (list-from-file mode) | If mode=list-from-file |
| `--query` | Search query (search mode) | If mode=search |
| `--output` | Output CSV file path | No (default: output.csv) |
| `--limit` | Maximum number of results | No (default: 100) |
| `--headless` | Run browser in headless mode | No (default: True) |
| `--no-headless` | Run browser with GUI | No |
| `--city` | City name for location | No |
| `--state` | State code for location | No |
| `--config` | Path to YAML config file | No |
| `--debug` | Enable debug mode | No |

### Configuration File (YAML)

Create `config.yaml`:

```yaml
# Rate Limiting
delay_between_requests: 2.0
delay_jitter: 0.5
max_retries: 3
request_timeout: 30

# Browser
headless: true
browser_type: chromium
viewport_width: 1920
viewport_height: 1080

# Location
default_location: "Houston, TX"
city: "Houston"
state: "TX"

# Limits
max_results: 100
max_pages_per_source: 50

# Sources
enabled_sources:
  - "Google Maps"
  - "Yelp"
  - "OpenTable"
  - "Official Website"

# Error Handling
skip_on_captcha: true
skip_on_403: true
skip_on_429: true
max_consecutive_errors: 5

# Logging
log_level: "INFO"
log_file: "scraper.log"
debug_mode: false
```

Use with:

```bash
python -m scraper.main --mode search --query "restaurants" --config config.yaml
```

## CSV Output Format

The scraper outputs CSV files with these exact columns (in order):

1. ID
2. Title
3. Slug
4. Content
5. Excerpt
6. Post Status
7. Post Date
8. Featured Image URL
9. Location
10. Address
11. Phone
12. Website
13. Email
14. Rating
15. Price Range
16. Latitude
17. Longitude
18. Diners Choice
19. Top Rated
20. Outdoor Dining
21. Neighborhood
22. Dress Code
23. Chef Bio
24. Gift Card URL
25. Private Dining Email
26. Private Dining Phone
27. Video URL
28. Phone Number (ACF)
29. Parking
30. Payment Method
31. Noise
32. Executive Chef
33. Cross Street
34. Google Business Link
35. Categories
36. Tags
37. Cuisines

**Important**: All missing fields are output as empty strings `""` (never `None` or `null`).

## Examples

### Example 1: Search for Steakhouses

```bash
python -m scraper.main \
  --mode search \
  --query "steakhouses in Houston Texas" \
  --city "Houston" \
  --state "TX" \
  --limit 50 \
  --output steakhouses_houston.csv
```

### Example 2: Scrape Specific Google Maps Place

```bash
python -m scraper.main \
  --mode single-url \
  --url "https://www.google.com/maps/place/..." \
  --output restaurant.csv
```

### Example 3: Batch Scrape from File

Create `urls.txt`:
```
https://www.google.com/maps/place/Restaurant+1
https://www.google.com/maps/place/Restaurant+2
https://www.yelp.com/biz/restaurant-3
```

Run:
```bash
python -m scraper.main \
  --mode list-from-file \
  --file urls.txt \
  --output batch_results.csv \
  --limit 100
```

### Example 4: Debug Mode

```bash
python -m scraper.main \
  --mode search \
  --query "restaurants" \
  --debug \
  --no-headless \
  --output debug_output.csv
```

## Architecture

### Module Structure

```
scraper/
├── main.py          # CLI entry point
├── config.py         # Configuration management
├── fetch.py          # HTTP fetching and browser automation
├── parse.py          # HTML parsing for each source
├── normalize.py      # Data normalization and merging
├── export.py         # CSV export
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

### Data Flow

1. **Fetch**: Retrieve HTML from URLs using HTTPX or Playwright
2. **Parse**: Extract structured data using BeautifulSoup
3. **Normalize**: Merge data from multiple sources, standardize formats
4. **Export**: Write to RFC-4180 compliant CSV

### Error Handling

The scraper handles:

- **CAPTCHAs**: Detects and skips (configurable)
- **Bot challenges**: Detects Cloudflare and similar
- **Rate limiting**: Automatic retries with exponential backoff
- **403/429 errors**: Configurable skip or retry
- **Timeouts**: Retry with backoff
- **Missing data**: Empty strings in output

## ID Generation

Entity IDs are generated using SHA256 hash of:
- Canonical business name (lowercase, stripped)
- Canonical address (lowercase, stripped)
- Optional salt

This ensures:
- Stable IDs across runs
- Deduplication of entities
- No collisions (with high probability)

## Logging

Logs are written to:
- **Console**: Rich-formatted output with progress bars
- **File**: `scraper.log` (configurable)

Log levels:
- `DEBUG`: Verbose debugging information
- `INFO`: General progress and status
- `WARNING`: Non-fatal issues (CAPTCHA, rate limits)
- `ERROR`: Failures that cause skipping

## Ethical Considerations

This scraper is designed to be ethical and legal:

- ✅ Respects `robots.txt`
- ✅ Configurable rate limiting
- ✅ No login bypassing
- ✅ No CAPTCHA solving
- ✅ Stops on repeated errors
- ✅ User-agent identification

**Important**: Always:
- Check website Terms of Service
- Use reasonable rate limits
- Respect website resources
- Obtain permission when required

## Troubleshooting

### Playwright Browser Not Found

```bash
playwright install chromium
```

### Import Errors

```bash
pip install -r requirements.txt
```

### CAPTCHA Detected

- Increase `delay_between_requests` in config
- Use `--no-headless` to see what's happening
- Consider using proxies (not included)

### No Results

- Check if URLs are accessible
- Verify search query format
- Enable `--debug` mode
- Check logs in `scraper.log`

### Rate Limited

- Increase delays in config
- Reduce `max_results`
- Use different user agents
- Consider proxies

## Performance

Typical performance:
- **Static pages**: ~2-5 seconds per page
- **Dynamic pages**: ~5-10 seconds per page
- **With delays**: Add 2-3 seconds per request

For 100 results:
- Estimated time: 5-15 minutes (depending on sources)

## License

This code is provided as-is for educational and legitimate business purposes.

## Support

For issues or questions:
1. Check logs in `scraper.log`
2. Enable `--debug` mode
3. Review error messages
4. Check website accessibility manually

