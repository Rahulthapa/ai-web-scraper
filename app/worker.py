import asyncio
from typing import Dict, Any, List
from datetime import datetime
from .scraper import WebScraper
from .crawler import WebCrawler
from .ai_filter import AIFilter
from .storage import Storage
from .models import JobStatus


class ScraperWorker:
    def __init__(self, storage_instance=None):
        self.scraper = WebScraper()
        self.ai_filter = AIFilter()
        self.storage = storage_instance or Storage()

    async def process_job(self, job_id: str) -> None:
        """Process a scraping job"""
        try:
            # Update job status to running
            await self.storage.update_job(job_id, {
                'status': JobStatus.RUNNING.value
            })

            # Get job details
            job = await self.storage.get_job(job_id)
            if not job:
                raise Exception(f"Job {job_id} not found")

            # Check if this is a crawl job or single URL job
            if job.get('crawl_mode'):
                # Web crawling mode
                crawler = WebCrawler(
                    max_pages=job.get('max_pages', 10),
                    max_depth=job.get('max_depth', 2),
                    same_domain=job.get('same_domain', True)
                )
                
                use_javascript = job.get('use_javascript', False)
                search_query = job.get('search_query')
                
                if search_query:
                    # Crawl from search query
                    scraped_pages = await crawler.crawl_from_search(
                        search_query=search_query,
                        max_pages=job.get('max_pages', 10),
                        use_javascript=use_javascript
                    )
                else:
                    # Crawl from starting URL(s)
                    start_urls = [job['url']] if job.get('url') else []
                    if not start_urls:
                        raise Exception("No URL or search query provided for crawling")
                    
                    keywords = None
                    if job.get('ai_prompt'):
                        # Extract keywords from AI prompt for filtering
                        keywords = [job['ai_prompt']]
                    
                    scraped_pages = await crawler.crawl(
                        start_urls=start_urls,
                        use_javascript=use_javascript,
                        keywords=keywords
                    )
                
                # Convert list of pages to list format for consistency
                filtered_data = scraped_pages if scraped_pages else []
            else:
                # Single URL scraping mode
                if not job.get('url'):
                    raise Exception("URL is required for single page scraping")
                
                use_javascript = job.get('use_javascript', False)
                scraped_data = await self.scraper.scrape(job['url'], use_javascript=use_javascript)
                filtered_data = [scraped_data]

            # Apply AI filtering if prompt provided
            # Note: filtered_data is already set above based on crawl_mode
            if job.get('ai_prompt') and filtered_data:
                # Apply AI filtering to each page in the results
                ai_filtered = []
                for page_data in filtered_data:
                    try:
                        result = await self.ai_filter.filter_and_structure(
                            page_data,
                            job['ai_prompt']
                        )
                        ai_filtered.extend(result if isinstance(result, list) else [result])
                    except Exception as e:
                        # If AI filtering fails for a page, include original data
                        ai_filtered.append(page_data)
                filtered_data = ai_filtered

            # Save results
            await self.storage.save_results(job_id, filtered_data)

            # Update job status to completed
            await self.storage.update_job(job_id, {
                'status': JobStatus.COMPLETED.value,
                'completed_at': datetime.utcnow().isoformat()
            })

        except Exception as e:
            # Update job status to failed
            await self.storage.update_job(job_id, {
                'status': JobStatus.FAILED.value,
                'error': str(e)
            })
            raise
