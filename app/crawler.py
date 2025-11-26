import asyncio
from typing import Dict, Any, List, Set, Optional
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque
import re
from .scraper import WebScraper


class WebCrawler:
    """
    General-purpose web crawler that can discover and scrape multiple pages
    """
    
    def __init__(self, max_pages: int = 10, max_depth: int = 2, same_domain: bool = True):
        self.scraper = WebScraper()
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.same_domain = same_domain
        self.visited_urls: Set[str] = set()
        self.results: List[Dict[str, Any]] = []
        
    async def crawl(
        self, 
        start_urls: List[str], 
        use_javascript: bool = False,
        keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl the web starting from seed URLs
        
        Args:
            start_urls: List of URLs to start crawling from
            use_javascript: Whether to use Playwright for JS-rendered pages
            keywords: Optional keywords to filter pages (only crawl pages containing these)
        
        Returns:
            List of scraped page data
        """
        self.visited_urls.clear()
        self.results.clear()
        
        # Normalize and validate start URLs
        seed_urls = []
        for url in start_urls:
            normalized = self._normalize_url(url)
            if normalized and normalized not in self.visited_urls:
                seed_urls.append(normalized)
                self.visited_urls.add(normalized)
        
        if not seed_urls:
            raise ValueError("No valid starting URLs provided")
        
        # Crawl queue: (url, depth)
        queue = deque([(url, 0) for url in seed_urls])
        
        while queue and len(self.results) < self.max_pages:
            url, depth = queue.popleft()
            
            if depth > self.max_depth:
                continue
            
            try:
                # Scrape the page
                page_data = await self.scraper.scrape(url, use_javascript=use_javascript)
                
                # Filter by keywords if provided
                if keywords:
                    page_text = page_data.get('text_content', '').lower()
                    if not any(keyword.lower() in page_text for keyword in keywords):
                        continue
                
                # Add to results
                self.results.append({
                    **page_data,
                    'crawl_depth': depth,
                    'discovered_from': url if depth > 0 else None
                })
                
                # Extract links for further crawling
                if depth < self.max_depth and len(self.results) < self.max_pages:
                    links = page_data.get('links', [])
                    base_domain = self._get_domain(url)
                    
                    for link_info in links:
                        link_url = link_info.get('href') if isinstance(link_info, dict) else link_info
                        
                        if not link_url:
                            continue
                        
                        # Resolve relative URLs
                        full_url = urljoin(url, link_url)
                        normalized = self._normalize_url(full_url)
                        
                        if not normalized:
                            continue
                        
                        # Check if we should follow this link
                        if self._should_follow_link(normalized, base_domain):
                            if normalized not in self.visited_urls:
                                self.visited_urls.add(normalized)
                                queue.append((normalized, depth + 1))
                
                # Small delay to be respectful
                await asyncio.sleep(1)
                
            except Exception as e:
                # Log error but continue crawling
                print(f"Error crawling {url}: {str(e)}")
                continue
        
        return self.results
    
    async def crawl_from_search(
        self,
        search_query: str,
        max_pages: int = 10,
        use_javascript: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Crawl the web based on a search query
        Uses DuckDuckGo or similar to find relevant pages
        
        Args:
            search_query: Search query string
            max_pages: Maximum number of pages to crawl
            use_javascript: Whether to use Playwright
        
        Returns:
            List of scraped page data
        """
        # For now, we'll use a simple approach:
        # Try to construct search URLs and extract results
        # In production, you'd use a search API
        
        # Try DuckDuckGo HTML search
        search_url = f"https://html.duckduckgo.com/html/?q={search_query.replace(' ', '+')}"
        
        try:
            # Scrape search results page
            search_results = await self.scraper.scrape(search_url, use_javascript=False)
            
            # Extract result URLs from the search page
            # This is a simplified approach - in production use a proper search API
            links = search_results.get('links', [])
            result_urls = []
            
            for link in links[:max_pages]:
                href = link.get('href') if isinstance(link, dict) else link
                if href and self._is_valid_url(href):
                    result_urls.append(href)
            
            if not result_urls:
                # Fallback: try to construct a Google search URL (may not work due to anti-bot)
                # Or use a search API service
                raise ValueError("Could not extract search results. Consider using a search API.")
            
            # Crawl the discovered URLs
            self.max_pages = max_pages
            return await self.crawl(result_urls, use_javascript=use_javascript, keywords=[search_query])
            
        except Exception as e:
            raise Exception(f"Search-based crawling failed: {str(e)}. Try providing specific URLs instead.")
    
    def _normalize_url(self, url: str) -> Optional[str]:
        """Normalize and validate URL"""
        if not url:
            return None
        
        # Remove fragments
        if '#' in url:
            url = url.split('#')[0]
        
        # Remove common tracking parameters
        url = re.sub(r'[?&](utm_[^&]*|ref=[^&]*|source=[^&]*)', '', url)
        
        # Validate URL format
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return None
        
        # Only allow http/https
        if parsed.scheme not in ['http', 'https']:
            return None
        
        # Reconstruct URL
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path or '/',
            parsed.params,
            parsed.query,
            ''  # Remove fragment
        ))
        
        return normalized
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc.lower()
    
    def _should_follow_link(self, url: str, base_domain: str) -> bool:
        """Determine if we should follow a link"""
        if not self._is_valid_url(url):
            return False
        
        # Skip common non-content URLs
        skip_patterns = [
            r'\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|tar|gz)$',
            r'\.(jpg|jpeg|png|gif|svg|webp|ico)$',
            r'\.(mp4|avi|mov|wmv|flv)$',
            r'\.(mp3|wav|ogg)$',
            r'mailto:',
            r'javascript:',
            r'#',
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # Domain filtering
        if self.same_domain:
            link_domain = self._get_domain(url)
            if link_domain != base_domain:
                return False
        
        return True
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for crawling"""
        if not url:
            return False
        
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

