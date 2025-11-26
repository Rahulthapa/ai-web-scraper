import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import httpx


class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    async def scrape(self, url: str) -> Dict[str, Any]:
        """
        Scrape a URL and return structured data
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract basic page information
            data = {
                'url': url,
                'title': soup.title.string if soup.title else None,
                'text_content': soup.get_text(strip=True, separator=' ')[:5000],
                'links': [a.get('href') for a in soup.find_all('a', href=True)][:100],
                'images': [img.get('src') for img in soup.find_all('img', src=True)][:50],
            }

            return data

        except Exception as e:
            raise Exception(f"Scraping failed: {str(e)}")

    def close(self):
        self.session.close()
