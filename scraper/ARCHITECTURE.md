# Architecture Documentation

## High-Level Architecture

The scraper follows a modular, layered architecture designed for production use:

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Layer (main.py)                   │
│  - Argument parsing                                      │
│  - Mode selection (single-url, list-from-file, search)  │
│  - Progress tracking                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Configuration Layer (config.py)             │
│  - CSV column definitions                                │
│  - Source patterns and selectors                         │
│  - Rate limiting settings                                │
│  - Error handling policies                              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐         ┌──────────────┐
│ Fetch Layer  │         │ Parse Layer  │
│ (fetch.py)   │────────▶│ (parse.py)   │
│              │         │              │
│ - HTTPX      │         │ - Beautiful  │
│ - Playwright │         │   Soup       │
│ - Robots.txt │         │ - JSON-LD    │
│ - Retries    │         │ - Microdata  │
└──────────────┘         └──────────────┘
        │                         │
        └────────────┬────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│          Normalization Layer (normalize.py)             │
│  - Multi-source merging                                  │
│  - Data standardization                                  │
│  - ID generation                                         │
│  - Field mapping to CSV columns                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            Export Layer (export.py)                     │
│  - RFC-4180 CSV generation                              │
│  - Column ordering enforcement                          │
│  - Data validation                                      │
└─────────────────────────────────────────────────────────┘
```

## Module Responsibilities

### 1. config.py - Configuration Management

**Purpose**: Centralized configuration with CLI and file overrides

**Key Components**:
- `CSV_COLUMNS`: Strict column order (immutable)
- `SOURCES`: Enabled data sources
- `SOURCE_PATTERNS`: URL patterns and selectors per source
- `ScraperConfig`: Dataclass with all settings
- Environment variable support
- YAML file loading

**Design Decisions**:
- Dataclass for type safety
- Default values for all settings
- Override hierarchy: CLI > File > Environment > Defaults

### 2. fetch.py - Data Retrieval

**Purpose**: Fetch HTML from web sources with error handling

**Key Components**:
- `Fetcher`: Main fetch class with async context manager
- `RobotsTxtChecker`: Robots.txt compliance with caching
- Static fetching (HTTPX) for simple pages
- Dynamic fetching (Playwright) for JavaScript-rendered content
- Error detection (CAPTCHA, bot challenges, rate limits)

**Design Decisions**:
- Async/await for concurrent operations
- Exponential backoff for retries
- Automatic fallback from static to dynamic
- User-agent rotation
- Request metadata tracking

### 3. parse.py - Data Extraction

**Purpose**: Extract structured data from HTML

**Key Components**:
- Source-specific parsers:
  - `parse_google_maps()`
  - `parse_yelp()`
  - `parse_opentable()`
  - `parse_official_website()`
- Structured data extraction:
  - `extract_json_ld()`: Schema.org JSON-LD
  - `extract_microdata()`: HTML5 microdata
  - `extract_og_tags()`: Open Graph tags
- Helper functions for safe extraction

**Design Decisions**:
- BeautifulSoup + lxml for parsing
- Multiple selector fallbacks for robustness
- JSON-LD as primary structured data source
- Pattern matching for unstructured data

### 4. normalize.py - Data Standardization

**Purpose**: Merge and standardize data from multiple sources

**Key Components**:
- `DataNormalizer`: Main normalization class
- Entity deduplication using stable IDs
- Field normalization functions:
  - Phone numbers → E.164-like format
  - Price ranges → $, $$, $$$, $$$$
  - Booleans → Yes/No
  - Ratings → Float strings
- ID generation using SHA256 hashing
- Content and excerpt generation

**Design Decisions**:
- Stable ID generation prevents duplicates
- Multi-source merging with preference rules
- Empty strings for all missing fields
- Strict CSV column mapping

### 5. export.py - CSV Generation

**Purpose**: Generate RFC-4180 compliant CSV files

**Key Components**:
- `CSVExporter`: CSV generation class
- Strict column ordering
- Proper quoting and escaping
- UTF-8 encoding
- Data validation

**Design Decisions**:
- Python csv module (not pandas) for strict compliance
- QUOTE_MINIMAL for clean output
- All columns always present (empty if missing)

### 6. main.py - CLI Interface

**Purpose**: Command-line interface and orchestration

**Key Components**:
- Argument parsing with argparse
- Mode selection:
  - `single-url`: One URL
  - `list-from-file`: Batch URLs
  - `search`: Google Maps search
- Progress tracking with Rich
- Error handling and reporting
- Summary statistics

**Design Decisions**:
- Rich library for beautiful CLI
- Async/await for non-blocking operations
- Comprehensive error messages
- Progress indicators for long operations

## Data Flow Example

### Search Mode Flow

1. **User Input**: `--mode search --query "steakhouses Houston"`
2. **Config Load**: Load settings from CLI args and config file
3. **Search**: Build Google Maps search URL, fetch results page
4. **Extract URLs**: Parse search results to get place URLs
5. **Fetch Places**: For each place URL:
   - Check robots.txt
   - Fetch HTML (static or dynamic)
   - Detect errors (CAPTCHA, rate limit)
   - Parse data
6. **Fetch Websites**: Extract official website URLs, scrape those
7. **Normalize**: Merge all data sources per entity
8. **Export**: Write to CSV with strict column order
9. **Summary**: Display statistics

## Error Handling Strategy

### Error Types

1. **Recoverable Errors**:
   - Network timeouts → Retry with backoff
   - Temporary 429 → Retry after delay
   - Connection errors → Retry

2. **Skippable Errors**:
   - CAPTCHA detected → Skip (if configured)
   - 403 Forbidden → Skip (if configured)
   - Bot challenge → Skip

3. **Fatal Errors**:
   - Too many consecutive errors → Stop
   - Invalid configuration → Exit
   - File write errors → Exit

### Error Logging

All errors are logged with:
- URL
- Timestamp
- Error type
- Error message
- Traceback (debug mode only)

## Performance Considerations

### Optimization Strategies

1. **Concurrent Fetching**: Use asyncio for parallel requests
2. **Caching**: Robots.txt cache to avoid repeated fetches
3. **Selective Parsing**: Only parse enabled sources
4. **Early Exit**: Stop on too many errors

### Rate Limiting

- Configurable delay between requests
- Random jitter to avoid patterns
- Exponential backoff on errors
- Respect for robots.txt crawl-delay

## Security Considerations

1. **No Authentication Bypass**: Never attempts to bypass login
2. **No CAPTCHA Solving**: Detects and skips
3. **User-Agent Identification**: Always identifies as bot
4. **Robots.txt Compliance**: Hard-enforced
5. **Rate Limiting**: Prevents abuse

## Extensibility

### Adding New Sources

1. Add source to `SOURCES` in `config.py`
2. Add URL patterns to `SOURCE_PATTERNS`
3. Create parser function in `parse.py`
4. Update normalization if needed

### Adding New Fields

1. Add column to `CSV_COLUMNS` in `config.py`
2. Extract in relevant parser
3. Normalize in `normalize.py`
4. Export automatically includes it

## Testing Strategy

### Unit Tests (Recommended)

- Test each parser with sample HTML
- Test normalization functions
- Test ID generation
- Test CSV export format

### Integration Tests (Recommended)

- Test full pipeline with mock data
- Test error handling paths
- Test multi-source merging

## Deployment Considerations

### Production Checklist

- [ ] Set appropriate rate limits
- [ ] Configure logging level
- [ ] Set up error monitoring
- [ ] Test with small dataset first
- [ ] Verify robots.txt compliance
- [ ] Check Terms of Service
- [ ] Monitor for CAPTCHAs
- [ ] Set up proxy rotation (if needed)

### Scaling

For large-scale scraping:
- Use proxy rotation
- Distribute across multiple machines
- Use message queues for job distribution
- Implement result deduplication across runs
- Monitor success rates

