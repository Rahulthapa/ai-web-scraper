# Section-Based Data Extraction

## Overview

The system now extracts and categorizes data based on **section titles** found in the HTML. This means if a restaurant page has sections like "About", "Amenities & More", "Location & Hours", etc., the extracted data will be organized under these section categories.

## How It Works

### 1. **HTML Parsing**
When scraping a page, the system:
- Identifies section headings (h2, h3, h4 tags)
- Extracts all content that follows each heading until the next heading
- Organizes content (text, lists, links) under each section title

### 2. **Section Detection**
The system looks for:
- **Headings**: h2, h3, h4 tags that represent section titles
- **Content grouping**: All content between one heading and the next is grouped under that section
- **Section structure**: Each section contains:
  - `title`: The section heading text
  - `text`: Combined text content from that section
  - `lists`: Any lists (ul/ol) found in that section
  - `links`: Any links found in that section

### 3. **AI-Powered Categorization**
When sections are detected:
- The AI receives the section structure along with the content
- The AI is instructed to organize extracted data by section titles
- Data is categorized under the appropriate section (e.g., amenities go under "Amenities & More")
- The output JSON structure reflects the section organization

## Example

### Input HTML Structure:
```html
<h2>About</h2>
<p>This restaurant serves authentic Italian cuisine...</p>

<h2>Amenities & More</h2>
<ul>
  <li>Wi-Fi</li>
  <li>Parking</li>
  <li>Outdoor Seating</li>
</ul>

<h2>Location & Hours</h2>
<p>123 Main St, City, State 12345</p>
<p>Mon-Fri: 11am-10pm</p>
```

### Extracted Data Structure:
```json
{
  "sections": {
    "About": {
      "title": "About",
      "text": "This restaurant serves authentic Italian cuisine...",
      "lists": null,
      "links": null
    },
    "Amenities & More": {
      "title": "Amenities & More",
      "text": "",
      "lists": [["Wi-Fi", "Parking", "Outdoor Seating"]],
      "links": null
    },
    "Location & Hours": {
      "title": "Location & Hours",
      "text": "123 Main St, City, State 12345 Mon-Fri: 11am-10pm",
      "lists": null,
      "links": null
    }
  }
}
```

### AI-Processed Output:
```json
[
  {
    "name": "Restaurant Name",
    "sections": {
      "About": {
        "description": "This restaurant serves authentic Italian cuisine...",
        "cuisine": "Italian"
      },
      "Amenities & More": {
        "amenities": ["Wi-Fi", "Parking", "Outdoor Seating"]
      },
      "Location & Hours": {
        "address": "123 Main St, City, State 12345",
        "hours": "Mon-Fri: 11am-10pm"
      }
    }
  }
]
```

## Benefits

1. **Better Organization**: Data is automatically organized by the page's natural structure
2. **Context Preservation**: Information is grouped with related content
3. **Easier Analysis**: CSV/Excel exports will have clear categories
4. **Accurate Categorization**: Uses the page's own section titles, not guesswork

## When Sections Are Used

- ✅ **Individual restaurant pages**: Sections like "About", "Amenities", "Hours" are detected
- ✅ **Listing pages**: Section titles help organize multiple restaurants
- ✅ **Any HTML with headings**: The system automatically detects and uses section structure
- ✅ **Paste HTML mode**: Works with pasted HTML that has section headings

## Technical Details

### Section Extraction Method
- Located in: `app/scraper.py` → `_extract_sections()`
- Processes: BeautifulSoup parsed HTML
- Returns: Dictionary with section titles as keys

### AI Integration
- Located in: `app/ai_filter.py` → `_filter_with_gemini()`
- Enhancement: AI prompt includes section structure
- Output: Data organized by section categories

### Content Preparation
- Located in: `app/ai_filter.py` → `_prepare_content()`
- Enhancement: Section data is included in AI input
- Format: Clear section markers for AI processing

## Usage

The section-based extraction is **automatic** - no configuration needed! When you:
1. Scrape a URL with section headings
2. Paste HTML with section headings
3. Extract from individual restaurant pages

The system will automatically:
- Detect sections
- Extract content by section
- Organize data by section titles
- Return categorized results

## Output Format

The final output will have data organized like:
```json
{
  "name": "Restaurant",
  "url": "https://...",
  "sections": {
    "Section Title 1": {
      "field1": "value1",
      "field2": "value2"
    },
    "Section Title 2": {
      "field3": "value3"
    }
  }
}
```

This structure makes it easy to:
- Export to CSV with section columns
- Filter by section
- Understand data context
- Match the original page layout

