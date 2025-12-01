"""
Google Maps Business Scraper
Adapted from Node.js/Puppeteer code to Python/Playwright
Scrapes business listings from Google Maps and extracts detailed information
"""
import asyncio
import re
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import logging

try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    raise ImportError("Playwright not installed. Run: pip install playwright && playwright install chromium")

logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    """Scraper for Google Maps business listings"""
    
    def __init__(
        self,
        max_listings: int = 120,
        headless: bool = True,
        slow_mo: int = 0,
        wait_between_actions_ms: int = 1200
    ):
        self.max_listings = max_listings
        self.headless = headless
        self.slow_mo = slow_mo
        self.wait_between_actions_ms = wait_between_actions_ms
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ],
            slow_mo=self.slow_mo
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
    
    async def delay(self, ms: int):
        """Small delay helper"""
        await asyncio.sleep(ms / 1000.0)
    
    async def safe_text(self, page: Page, selector: str, get_attr: Optional[str] = None) -> str:
        """Robust text getter with error handling"""
        try:
            if get_attr:
                element = await page.query_selector(selector)
                if not element:
                    return ''
                value = await element.get_attribute(get_attr) or ''
                return value.strip()
            else:
                await page.wait_for_selector(selector, timeout=3000).catch(lambda _: None)
                element = await page.query_selector(selector)
                if not element:
                    return ''
                text = await element.inner_text()
                return text.strip()
        except Exception:
            return ''
    
    def find_email_in_text(self, text: str) -> str:
        """Find email in text using regex"""
        if not text:
            return ''
        pattern = r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches[0] if matches else ''
    
    def slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        if not text:
            return ''
        text = text.lower()
        text = re.sub(r'\s+', '-', text)
        text = re.sub(r'[^\w\-]+', '', text)
        text = re.sub(r'\-\-+', '-', text)
        text = text.strip('-')
        return text
    
    async def get_listing_urls(self, page: Page, search_query: str) -> List[str]:
        """Get listing URLs from Google Maps search results"""
        maps_search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        
        logger.info(f"Opening Google Maps: {maps_search_url}")
        await page.goto(maps_search_url, wait_until="networkidle", timeout=60000)
        await self.delay(2000)
        
        # Scroll to load more results
        await page.wait_for_timeout(1500)
        
        # Collect listing place URLs
        listing_urls = await page.evaluate("""(max) => {
            const out = new Set();
            const anchors = Array.from(document.querySelectorAll('a'));
            
            for (const a of anchors) {
                try {
                    const href = a.href || '';
                    if (href.includes('/place/') || href.includes('google.com/maps/place')) {
                        out.add(href.split('?')[0]);
                    }
                } catch (e) {}
                if (out.size >= max) break;
            }
            
            if (out.size === 0) {
                const items = document.querySelectorAll('[data-place-id], [data-result-id], [data-pid]');
                for (const it of items) {
                    const pid = it.getAttribute('data-place-id') || 
                                it.getAttribute('data-result-id') || 
                                it.getAttribute('data-pid');
                    if (pid) {
                        out.add(window.location.origin + '/maps/place/?q=place_id:' + pid);
                    }
                    if (out.size >= max) break;
                }
            }
            
            return Array.from(out).slice(0, max);
        }""", self.max_listings)
        
        logger.info(f"Found {len(listing_urls)} place URLs to visit")
        return listing_urls
    
    async def scrape_listing(self, page: Page, place_url: str) -> Dict[str, Any]:
        """Scrape a single Google Maps listing"""
        try:
            await page.goto(place_url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            logger.warn(f"Initial goto failed, retrying: {e}")
            await page.goto(f"{place_url}&hl=en", wait_until="networkidle", timeout=60000)
        
        await self.delay(1500 + (asyncio.get_event_loop().time() % 1) * 1000)
        
        # Extract Title
        title_selectors = [
            'h1.section-hero-header-title-title',
            'h1[data-section-id="title"]',
            'h1'
        ]
        title = ''
        for selector in title_selectors:
            title = await self.safe_text(page, selector) or title
            if title:
                break
        
        # Featured Image
        featured_image_url = ''
        try:
            og_image = await page.query_selector('meta[property="og:image"]')
            if og_image:
                featured_image_url = await og_image.get_attribute('content') or ''
        except:
            pass
        
        if not featured_image_url:
            img = await page.query_selector('img')
            if img:
                featured_image_url = await img.get_attribute('src') or ''
        
        # Address
        address = await page.evaluate("""() => {
            const sel = document.querySelector('[data-item-id="address"], button[data-tooltip*="Copy address"], button[aria-label*="Address"]');
            if (sel) return sel.innerText || sel.textContent || '';
            
            const possibles = Array.from(document.querySelectorAll('button, span, div'));
            for (const el of possibles) {
                try {
                    const txt = el.innerText || '';
                    if (txt && /[0-9]{1,5}\\s+[\\w\\s]+\\s+\\b[A-Za-z]{2,}\\b/.test(txt)) return txt;
                } catch(e) {}
            }
            return '';
        }""")
        
        # Phone
        phone = ''
        try:
            phone_btn = await page.query_selector('button[data-item-id="phone"]')
            if phone_btn:
                phone = await phone_btn.inner_text() or ''
        except:
            pass
        
        # Website
        website = ''
        try:
            website_link = await page.query_selector('a[data-item-id="authority"]')
            if website_link:
                website = await website_link.get_attribute('href') or ''
        except:
            pass
        
        if not website:
            website = await page.evaluate("""() => {
                const anchors = Array.from(document.querySelectorAll('a'));
                for (const a of anchors) {
                    if (a.innerText && /Website|Visit website/i.test(a.innerText)) return a.href;
                    if (a.href && /http/.test(a.href) && a.href.includes('http') && 
                        a.innerText && a.innerText.length < 50) {
                        if (!a.href.includes('google.com/url')) return a.href;
                    }
                }
                return '';
            }""")
        
        # Rating
        rating = ''
        try:
            rating_el = await page.query_selector('div[class*="gm2-display-2"] span[aria-hidden="true"]')
            if rating_el:
                rating = await rating_el.inner_text() or ''
        except:
            pass
        
        if not rating:
            rating = await self.safe_text(page, '[aria-label*="stars"]') or ''
        
        # Price Range
        price_range = await self.safe_text(page, 'span[aria-label*="Price"]') or ''
        if not price_range:
            price_range = await page.evaluate("""() => {
                const txt = document.body.innerText || '';
                const m = txt.match(/(\\${1,4})/);
                return m ? m[1] : '';
            }""")
        
        # Latitude / Longitude
        latitude = ''
        longitude = ''
        try:
            url = page.url
            match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', str(url))
            if match:
                latitude = match.group(1)
                longitude = match.group(2)
        except:
            pass
        
        # Neighborhood
        neighborhood = ''
        if address:
            pieces = address.split(',')
            if len(pieces) >= 2:
                neighborhood = pieces[-2].strip()
        
        # Cross Street
        cross_street = await self.safe_text(page, 'button[data-item-id="cross-streets"]') or ''
        if not cross_street:
            txt = await page.evaluate("() => document.body.innerText || ''")
            near_match = re.search(r'near\s+([A-Za-z0-9\s,&]+)', txt, re.IGNORECASE)
            if near_match:
                cross_street = near_match.group(1).split('\n')[0].strip()
        
        # Google Business Link
        google_business_link = str(page.url).split('&')[0]
        
        # Description/Content
        description = await self.safe_text(page, '[data-section-id="si_g"]') or ''
        if not description:
            description = await page.evaluate("""() => {
                const about = document.querySelector('[jsaction="pane.placeActions.moreDetails"]') || 
                             document.querySelector('.section-info-text');
                return about ? about.innerText : '';
            }""")
        
        excerpt = description.split('.')[0].strip() if description else ''
        
        # Initialize additional fields
        outdoor_dining = ''
        diners_choice = ''
        top_rated = ''
        noise = ''
        dress_code = ''
        gift_card_url = ''
        private_dining_email = ''
        private_dining_phone = ''
        video_url = ''
        parking = ''
        payment_method = ''
        executive_chef = ''
        chef_bio = ''
        categories = 'Steakhouse;Restaurant;Dining'
        tags = ''
        cuisines = 'Steakhouse'
        
        # Scrape website for additional info
        if website:
            try:
                wpage = await self.browser.new_page()
                await wpage.goto(website, wait_until="domcontentloaded", timeout=45000)
                await wpage.wait_for_timeout(1200)
                
                body_text = await wpage.evaluate("() => document.body.innerText") or ''
                
                # Find email
                if not private_dining_email:
                    private_dining_email = self.find_email_in_text(body_text) or ''
                
                # Gift card link
                gc_link = await wpage.evaluate("""() => {
                    const links = Array.from(document.querySelectorAll('a'));
                    for (const a of links) {
                        if (a.href && /gift/i.test(a.innerText || a.href)) return a.href;
                    }
                    return '';
                }""")
                if gc_link:
                    gift_card_url = gc_link
                
                # Executive Chef
                chef_match = re.search(r'Chef\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,3})', body_text, re.IGNORECASE)
                if chef_match:
                    executive_chef = chef_match.group(1)
                
                # Private dining
                pd_match = re.search(r'private\s+dining[\s\S]{0,200}', body_text, re.IGNORECASE)
                if pd_match:
                    pd_text = pd_match.group(0)
                    pd_email = self.find_email_in_text(pd_text)
                    if pd_email:
                        private_dining_email = private_dining_email or pd_email
                    pd_phone_match = re.search(r'(\+?\d[\d\-\s\(\)]{7,}\d)', pd_text)
                    if pd_phone_match:
                        private_dining_phone = pd_phone_match.group(1)
                
                # Video links
                video_link = await wpage.evaluate("""() => {
                    const iframes = Array.from(document.querySelectorAll('iframe'));
                    for (const i of iframes) {
                        if (i.src && i.src.includes('youtube')) return i.src;
                    }
                    const anchors = Array.from(document.querySelectorAll('a'));
                    for (const a of anchors) {
                        if (a.href && /youtube|vimeo|video/i.test(a.href)) return a.href;
                    }
                    return '';
                }""")
                if video_link:
                    video_url = video_link
                
                # Parking & Payment
                if re.search(r'valet', body_text, re.IGNORECASE):
                    parking = 'Valet'
                if re.search(r'street parking', body_text, re.IGNORECASE):
                    parking = f"{parking}; Street" if parking else 'Street'
                if re.search(r'credit card|visa|mastercard|amex|discover', body_text, re.IGNORECASE):
                    payment_method = 'Credit Cards'
                
                # Chef bio
                if executive_chef:
                    lines = body_text.split('\n')
                    chef_lines = [l for l in lines if 'chef' in l.lower()][:3]
                    chef_bio = ' '.join(chef_lines)
                
                await wpage.close()
            except Exception as err:
                logger.warn(f"Website scrape error: {err}")
        
        # Try Yelp
        yelp_link = await page.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a'));
            for (const a of anchors) {
                const href = a.href || '';
                if (href.includes('yelp.com/biz')) return href.split('?')[0];
            }
            return '';
        }""")
        
        if yelp_link:
            try:
                ypage = await self.browser.new_page()
                await ypage.goto(yelp_link, wait_until="domcontentloaded", timeout=45000)
                await ypage.wait_for_timeout(1200)
                
                page_text = await ypage.evaluate("() => document.body.innerText") or ''
                
                y_rating = await self.safe_text(ypage, 'div[role="img"][aria-label*="star rating"]') or \
                          await self.safe_text(ypage, 'div[aria-label*="star"]')
                if y_rating and not rating:
                    rating = y_rating
                
                if re.search(r'outdoor seating', page_text, re.IGNORECASE):
                    outdoor_dining = 'Yes'
                
                dc_match = re.search(r'Dress code:\\s*([A-Za-z\\s]+)', page_text, re.IGNORECASE)
                if dc_match:
                    dress_code = dc_match.group(1).strip()
                
                y_email = self.find_email_in_text(page_text)
                if y_email and not private_dining_email:
                    private_dining_email = y_email
                
                await ypage.close()
            except Exception as err:
                logger.warn(f"Yelp scrape error: {err}")
        
        # Try OpenTable
        open_table_link = await page.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a'));
            for (const a of anchors) {
                const href = a.href || '';
                if (href.includes('opentable.com')) return href.split('?')[0];
            }
            return '';
        }""")
        
        if open_table_link:
            try:
                opage = await self.browser.new_page()
                await opage.goto(open_table_link, wait_until="domcontentloaded", timeout=45000)
                await opage.wait_for_timeout(1200)
                
                op_text = await opage.evaluate("() => document.body.innerText") or ''
                
                if re.search(r"Diners' Choice", op_text, re.IGNORECASE):
                    diners_choice = 'Yes'
                
                if not price_range:
                    pr_match = re.search(r'\${1,4}', op_text)
                    if pr_match:
                        price_range = pr_match.group(0)
                
                await opage.close()
            except Exception as err:
                logger.warn(f"OpenTable scrape error: {err}")
        
        # Cuisines
        g_cuisines = await page.evaluate("""() => {
            const labels = Array.from(document.querySelectorAll('button, span'));
            const found = new Set();
            labels.forEach(el => {
                const t = el.innerText || '';
                if (t && /(Steakhouse|Steak|American|Seafood|Barbecue|Fine dining)/i.test(t)) {
                    found.add(t.trim());
                }
            });
            return Array.from(found).slice(0, 6).join(';');
        }""")
        if g_cuisines:
            cuisines = g_cuisines
        
        # Content
        content = description
        if executive_chef:
            content += f'\n\nExecutive Chef: {executive_chef}\n'
        if website:
            content += f'\nWebsite: {website}'
        content = content.strip()
        
        return {
            'Title': title or '',
            'Slug': self.slugify(title or f'restaurant-{datetime.now().timestamp()}'),
            'Content': content or '',
            'Excerpt': excerpt or '',
            'PostStatus': 'publish',
            'PostDate': datetime.now().strftime('%Y-%m-%d'),
            'FeaturedImageURL': featured_image_url or '',
            'Location': 'Houston, TX',
            'Address': address or '',
            'Phone': phone or '',
            'Website': website or '',
            'Email': private_dining_email or self.find_email_in_text(content) or '',
            'Rating': str(rating) if rating else '',
            'PriceRange': price_range or '',
            'Latitude': latitude or '',
            'Longitude': longitude or '',
            'DinersChoice': diners_choice or 'No',
            'TopRated': top_rated or '',
            'OutdoorDining': outdoor_dining or 'No',
            'Neighborhood': neighborhood or '',
            'DressCode': dress_code or '',
            'ChefBio': chef_bio or '',
            'GiftCardURL': gift_card_url or '',
            'PrivateDiningEmail': private_dining_email or '',
            'PrivateDiningPhone': private_dining_phone or '',
            'VideoURL': video_url or '',
            'PhoneACF': phone or '',
            'Parking': parking or '',
            'PaymentMethod': payment_method or '',
            'Noise': noise or '',
            'ExecutiveChef': executive_chef or '',
            'CrossStreet': cross_street or '',
            'GoogleBusinessLink': google_business_link or '',
            'Categories': categories,
            'Tags': tags,
            'Cuisines': cuisines
        }
    
    async def scrape(self, search_query: str, output_csv: str = 'steakhouses_houston.csv') -> List[Dict[str, Any]]:
        """Main scraping method"""
        if not self.browser:
            raise RuntimeError("Scraper must be used as async context manager")
        
        page = await self.browser.new_page()
        
        # Set user agent and viewport
        await page.set_viewport_size({"width": 1366, "height": 768})
        await page.set_extra_http_headers({
            'accept-language': 'en-US,en;q=0.9'
        })
        
        # Get listing URLs
        listing_urls = await self.get_listing_urls(page, search_query)
        await page.close()
        
        results = []
        id_counter = 1
        
        # Process each listing
        for i, place_url in enumerate(listing_urls):
            logger.info(f"\n[{i+1}/{len(listing_urls)}] Processing: {place_url}")
            
            lpage = await self.browser.new_page()
            await lpage.set_viewport_size({"width": 1200, "height": 800})
            await lpage.set_extra_http_headers({'accept-language': 'en-US,en;q=0.9'})
            
            try:
                record = await self.scrape_listing(lpage, place_url)
                record['ID'] = id_counter
                id_counter += 1
                results.append(record)
                
                await self.delay(self.wait_between_actions_ms + int((asyncio.get_event_loop().time() % 1) * 900))
            except Exception as err:
                logger.error(f"Failed to scrape listing: {err}")
            finally:
                await lpage.close()
        
        # Write CSV
        if results and output_csv:
            await self._write_csv(results, output_csv)
        
        logger.info(f"\nSaved {len(results)} records to {output_csv}")
        return results
    
    async def _write_csv(self, results: List[Dict[str, Any]], filename: str):
        """Write results to CSV file"""
        if not results:
            return
        
        fieldnames = [
            'ID', 'Title', 'Slug', 'Content', 'Excerpt', 'PostStatus', 'PostDate',
            'FeaturedImageURL', 'Location', 'Address', 'Phone', 'Website', 'Email',
            'Rating', 'PriceRange', 'Latitude', 'Longitude', 'DinersChoice',
            'TopRated', 'OutdoorDining', 'Neighborhood', 'DressCode', 'ChefBio',
            'GiftCardURL', 'PrivateDiningEmail', 'PrivateDiningPhone', 'VideoURL',
            'PhoneACF', 'Parking', 'PaymentMethod', 'Noise', 'ExecutiveChef',
            'CrossStreet', 'GoogleBusinessLink', 'Categories', 'Tags', 'Cuisines'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)


# Standalone usage example
async def main():
    """Example usage"""
    async with GoogleMapsScraper(max_listings=10, headless=True) as scraper:
        results = await scraper.scrape('steakhouse houston tx', 'steakhouses_houston.csv')
        print(f"Scraped {len(results)} listings")


if __name__ == '__main__':
    asyncio.run(main())

