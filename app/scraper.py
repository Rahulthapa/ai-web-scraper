import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
import httpx
import re
from urllib.parse import urljoin, urlparse
import json


class WebScraper:
    def __init__(self, use_playwright: bool = False):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.use_playwright = use_playwright
        self.playwright_browser = None

    async def scrape(self, url: str, use_javascript: bool = False) -> Dict[str, Any]:
        """
        General-purpose web scraper that works on any website
        
        Args:
            url: The URL to scrape
            use_javascript: Whether to use Playwright for JavaScript-rendered pages
        
        Returns:
            Dictionary containing structured data from the page
        """
        try:
            # Try to fetch with requests first (faster)
            if not use_javascript:
                return await self._scrape_static(url)
            else:
                return await self._scrape_with_playwright(url)
                
        except Exception as e:
            # If static scraping fails and we haven't tried JS, try with Playwright
            if not use_javascript:
                try:
                    return await self._scrape_with_playwright(url)
                except:
                    pass
            raise Exception(f"Scraping failed: {str(e)}")

    async def _scrape_static(self, url: str) -> Dict[str, Any]:
        """Scrape static HTML content"""
        # Use async httpx for proper async support
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=self.session.headers)
            response.raise_for_status()
            
            # Detect content type
            content_type = response.headers.get('Content-Type', '').lower()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            
            # Extract comprehensive data
            data = await self._extract_structured_data(soup, url, response.text)
            
            return data

    async def _scrape_with_playwright(self, url: str) -> Dict[str, Any]:
        """Scrape JavaScript-rendered content using Playwright"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set viewport
                await page.set_viewport_size({"width": 1920, "height": 1080})
                
                # Navigate and wait for content
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Wait a bit for dynamic content
                await page.wait_for_timeout(2000)
                
                # Get page content
                html_content = await page.content()
                title = await page.title()
                
                # Extract text content
                text_content = await page.evaluate("""
                    () => {
                        // Remove script and style elements
                        const scripts = document.querySelectorAll('script, style, noscript');
                        scripts.forEach(el => el.remove());
                        
                        // Get main content
                        const body = document.body;
                        return body.innerText || body.textContent || '';
                    }
                """)
                
                # Extract links
                links = await page.evaluate("""
                    () => {
                        const links = Array.from(document.querySelectorAll('a[href]'));
                        return links.map(a => ({
                            text: a.innerText.trim(),
                            href: a.href,
                            title: a.title || ''
                        })).slice(0, 100);
                    }
                """)
                
                # Extract images
                images = await page.evaluate("""
                    () => {
                        const imgs = Array.from(document.querySelectorAll('img[src]'));
                        return imgs.map(img => ({
                            src: img.src,
                            alt: img.alt || '',
                            title: img.title || ''
                        })).slice(0, 50);
                    }
                """)
                
                # Extract meta tags
                meta_data = await page.evaluate("""
                    () => {
                        const metas = {};
                        document.querySelectorAll('meta').forEach(meta => {
                            const name = meta.getAttribute('name') || meta.getAttribute('property');
                            const content = meta.getAttribute('content');
                            if (name && content) {
                                metas[name] = content;
                            }
                        });
                        return metas;
                    }
                """)
                
                await browser.close()
                
                # Parse with BeautifulSoup for additional extraction
                soup = BeautifulSoup(html_content, 'html.parser')
                structured_data = await self._extract_structured_data(soup, url, html_content)
                
                # Merge Playwright data
                structured_data.update({
                    'title': title,
                    'text_content': text_content[:10000],  # Limit text
                    'links': links,
                    'images': images,
                    'meta_tags': meta_data,
                    'rendered_with_javascript': True
                })
                
                return structured_data
                
        except ImportError:
            raise Exception("Playwright not available. Install with: pip install playwright && playwright install chromium")
        except Exception as e:
            raise Exception(f"Playwright scraping failed: {str(e)}")

    async def _extract_structured_data(self, soup: BeautifulSoup, url: str, html_content: str) -> Dict[str, Any]:
        """Extract structured data from parsed HTML"""
        base_url = url
        
        # Extract title
        title = None
        if soup.title:
            title = soup.title.string.strip() if soup.title.string else None
        if not title:
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
        
        # Extract main content (try to find article, main, or content areas)
        main_content = None
        for selector in ['article', 'main', '[role="main"]', '.content', '#content', '.main-content']:
            element = soup.select_one(selector)
            if element:
                main_content = element.get_text(strip=True, separator=' ')
                break
        
        if not main_content:
            # Fallback to body text
            body = soup.find('body')
            if body:
                main_content = body.get_text(strip=True, separator=' ')
        
        # Extract all text (cleaned)
        all_text = soup.get_text(strip=True, separator=' ')
        
        # Extract links with context
        links = []
        for a in soup.find_all('a', href=True)[:100]:
            href = a.get('href')
            if href:
                # Resolve relative URLs
                full_url = urljoin(base_url, href)
                link_text = a.get_text(strip=True)
                links.append({
                    'text': link_text,
                    'href': full_url,
                    'title': a.get('title', '')
                })
        
        # Extract images with context
        images = []
        for img in soup.find_all('img', src=True)[:50]:
            src = img.get('src')
            if src:
                full_url = urljoin(base_url, src)
                images.append({
                    'src': full_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
        
        # Extract meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('itemprop')
            content = meta.get('content')
            if name and content:
                meta_tags[name] = content
        
        # Extract headings
        headings = {}
        for level in range(1, 7):
            tag = f'h{level}'
            headings[tag] = [h.get_text(strip=True) for h in soup.find_all(tag)][:20]
        
        # Extract lists
        lists = []
        for ul in soup.find_all(['ul', 'ol'])[:10]:
            items = [li.get_text(strip=True) for li in ul.find_all('li')]
            if items:
                lists.append(items)
        
        # Extract tables
        tables = []
        for table in soup.find_all('table')[:5]:
            rows = []
            for tr in table.find_all('tr'):
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)
        
        # Extract code blocks
        code_blocks = []
        for code in soup.find_all(['code', 'pre'])[:10]:
            code_text = code.get_text(strip=True)
            if code_text and len(code_text) > 10:
                code_blocks.append(code_text[:500])  # Limit length
        
        # Detect page type
        page_type = self._detect_page_type(soup, meta_tags)
        
        # Extract structured data (JSON-LD, microdata)
        structured_data = self._extract_json_ld(soup)
        
        return {
            'url': url,
            'title': title,
            'text_content': all_text[:10000],  # Limit to 10k chars
            'main_content': main_content[:5000] if main_content else None,
            'links': links,
            'images': images,
            'meta_tags': meta_tags,
            'headings': headings,
            'lists': lists,
            'tables': tables,
            'code_blocks': code_blocks,
            'page_type': page_type,
            'structured_data': structured_data,
            'word_count': len(all_text.split()) if all_text else 0,
            'rendered_with_javascript': False
        }

    def _detect_page_type(self, soup: BeautifulSoup, meta_tags: Dict[str, str]) -> str:
        """Detect the type of page (article, product, blog, etc.)"""
        # Check Open Graph type
        og_type = meta_tags.get('og:type', '').lower()
        if og_type:
            return og_type
        
        # Check schema.org type
        schema_type = soup.find(attrs={'itemtype': True})
        if schema_type:
            itemtype = schema_type.get('itemtype', '')
            if 'Article' in itemtype:
                return 'article'
            elif 'Product' in itemtype:
                return 'product'
            elif 'Person' in itemtype:
                return 'profile'
        
        # Heuristic detection
        if soup.find('article'):
            return 'article'
        elif soup.find(attrs={'class': re.compile(r'product|item', re.I)}):
            return 'product'
        elif soup.find('time') or soup.find(attrs={'class': re.compile(r'post|entry', re.I)}):
            return 'blog'
        elif soup.find('form'):
            return 'form'
        
        return 'generic'

    def _extract_json_ld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract JSON-LD structured data"""
        structured_data = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        return structured_data

    def close(self):
        self.session.close()
        if self.playwright_browser:
            # Playwright cleanup would go here if we maintain a persistent browser
            pass
