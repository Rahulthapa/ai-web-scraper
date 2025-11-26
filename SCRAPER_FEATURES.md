# Enhanced General-Purpose Web Scraper

## Overview

The scraper has been upgraded to be a **general-purpose web scraper** that works on **any website** across the internet, not just specific sites.

## How It Works

### 1. **Static HTML Scraping** (Default - Fast)
- Uses `httpx` for async HTTP requests
- Parses HTML with BeautifulSoup
- Extracts comprehensive data from any webpage

### 2. **JavaScript Rendering** (Optional - For SPAs)
- Uses Playwright to render JavaScript-heavy sites
- Handles React, Vue, Angular, and other SPA frameworks
- Waits for dynamic content to load
- Extracts fully rendered content

## What It Extracts

The scraper intelligently extracts:

### Basic Information
- **Title**: Page title and main heading
- **Text Content**: All readable text from the page
- **Main Content**: Focused content from article/main sections
- **Word Count**: Total words on the page

### Links
- All links with their text and URLs
- Resolves relative URLs to absolute
- Includes link titles and context

### Media
- All images with alt text and titles
- Image sources (resolved to full URLs)

### Structured Data
- **Meta Tags**: Open Graph, Twitter Cards, SEO meta
- **Headings**: All H1-H6 headings organized by level
- **Lists**: Both ordered and unordered lists
- **Tables**: Table data extracted as arrays
- **Code Blocks**: Code snippets from the page
- **JSON-LD**: Structured data (Schema.org)

### Page Type Detection
Automatically detects:
- Articles/Blog posts
- Product pages
- Profile pages
- Forms
- Generic pages

## Features

### ✅ Works on Any Website
- No website-specific configuration needed
- Handles different HTML structures automatically
- Adapts to various content types

### ✅ Smart Content Extraction
- Finds main content areas (article, main, content divs)
- Removes navigation, ads, and boilerplate
- Preserves meaningful structure

### ✅ JavaScript Support
- Option to use Playwright for JS-rendered pages
- Automatically falls back to Playwright if static scraping fails
- Handles single-page applications (SPAs)

### ✅ Comprehensive Data
- Extracts more than just text
- Includes structured data, metadata, and relationships
- Preserves context and hierarchy

## Usage

### Via API

```bash
# Basic scraping (static HTML)
POST /jobs
{
  "url": "https://example.com",
  "use_javascript": false
}

# JavaScript rendering (for SPAs)
POST /jobs
{
  "url": "https://react-app.example.com",
  "use_javascript": true
}
```

### Via Frontend

1. Enter any website URL
2. Optionally check "Use JavaScript Rendering" for SPAs
3. Add AI prompt to filter/extract specific data
4. Click "Start Scraping"

## Examples

### Scrape a News Article
```json
{
  "url": "https://news.example.com/article",
  "ai_prompt": "Extract the headline, author, publish date, and main article text"
}
```

### Scrape a Product Page
```json
{
  "url": "https://shop.example.com/product/123",
  "ai_prompt": "Extract product name, price, description, and images"
}
```

### Scrape a JavaScript App
```json
{
  "url": "https://app.example.com",
  "use_javascript": true,
  "ai_prompt": "Extract all user posts and comments"
}
```

## Technical Details

### Static Scraping Flow
1. Fetch URL with httpx (async)
2. Parse HTML with BeautifulSoup
3. Remove scripts/styles/noscript
4. Extract structured data
5. Detect page type
6. Return comprehensive data object

### JavaScript Rendering Flow
1. Launch headless Chromium browser
2. Navigate to URL
3. Wait for network idle
4. Wait for dynamic content (2s)
5. Extract rendered HTML and execute JavaScript
6. Parse with BeautifulSoup for additional extraction
7. Return comprehensive data object

## Limitations

- **Rate Limiting**: Be respectful of website rate limits
- **Robots.txt**: Should respect robots.txt (not currently enforced)
- **Authentication**: Cannot scrape behind login (unless cookies provided)
- **CAPTCHA**: Cannot solve CAPTCHAs automatically
- **Legal**: Always respect website terms of service and copyright

## Best Practices

1. **Use JavaScript rendering only when needed** (it's slower)
2. **Add AI prompts** to extract specific data you need
3. **Respect rate limits** - don't hammer websites
4. **Check robots.txt** before scraping
5. **Use for legitimate purposes** only

## Future Enhancements

- [ ] Respect robots.txt
- [ ] Cookie/session support
- [ ] CAPTCHA solving
- [ ] Multi-page crawling
- [ ] Sitemap parsing
- [ ] Rate limiting per domain
- [ ] Caching support

