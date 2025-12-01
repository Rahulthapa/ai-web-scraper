#!/usr/bin/env python3
"""
Standalone script to scrape steakhouses from Google Maps
Usage: python scrape_steakhouses.py
"""
import asyncio
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_maps_scraper import GoogleMapsScraper

async def main():
    """Main function"""
    search_query = 'steakhouse houston tx'
    output_file = 'steakhouses_houston.csv'
    max_listings = 120
    
    print(f"Starting Google Maps scraper...")
    print(f"Search query: {search_query}")
    print(f"Max listings: {max_listings}")
    print(f"Output file: {output_file}")
    print(f"\nThis may take a while. Please be patient...\n")
    
    async with GoogleMapsScraper(
        max_listings=max_listings,
        headless=True,
        wait_between_actions_ms=1200
    ) as scraper:
        results = await scraper.scrape(search_query, output_file)
        
        print(f"\n✅ Successfully scraped {len(results)} listings!")
        print(f"📄 Results saved to: {output_file}")
        
        if results:
            print(f"\nFirst few results:")
            for i, result in enumerate(results[:3], 1):
                print(f"\n{i}. {result.get('Title', 'N/A')}")
                print(f"   Address: {result.get('Address', 'N/A')}")
                print(f"   Phone: {result.get('Phone', 'N/A')}")
                print(f"   Rating: {result.get('Rating', 'N/A')}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

