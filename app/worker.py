import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from .scraper import WebScraper
from .crawler import WebCrawler
from .ai_filter import AIFilter
from .storage import Storage
from .models import JobStatus

logger = logging.getLogger(__name__)


class ScraperWorker:
    def __init__(self, storage_instance=None):
        self.scraper = WebScraper()
        self.ai_filter = AIFilter()
        self.storage = storage_instance or Storage()

    async def process_job(self, job_id: str) -> None:
        """Process a scraping job"""
        logger.info(f"Starting to process job {job_id}")
        errors = []
        
        try:
            # Update job status to running
            await self.storage.update_job(job_id, {'status': JobStatus.RUNNING.value})

            # Get job details
            job = await self.storage.get_job(job_id)
            if not job:
                raise Exception(f"Job {job_id} not found")
            
            logger.info(f"Job: mode={'crawl' if job.get('crawl_mode') else 'single'}, url={job.get('url')}, query={job.get('search_query')}")

            filtered_data = []
            use_javascript = job.get('use_javascript', False)

            # Check if this is a crawl job or single URL job
            if job.get('crawl_mode'):
                filtered_data = await self._process_crawl_job(job, errors)
            else:
                filtered_data = await self._process_single_url_job(job, errors)

            # If no data scraped, report the errors
            if not filtered_data:
                error_msg = "No data could be scraped. "
                if errors:
                    error_msg += "Errors: " + "; ".join(errors[:3])  # First 3 errors
                else:
                    error_msg += "The target site may be blocking automated access."
                
                await self.storage.update_job(job_id, {
                    'status': JobStatus.FAILED.value,
                    'error': error_msg
                })
                return

            # Apply AI filtering if prompt provided
            if job.get('ai_prompt') and filtered_data:
                filtered_data = await self._apply_ai_filter(filtered_data, job['ai_prompt'], errors)

            # Save results
            logger.info(f"Saving {len(filtered_data)} results for job {job_id}")
            await self.storage.save_results(job_id, filtered_data)

            # Update job status to completed
            await self.storage.update_job(job_id, {
                'status': JobStatus.COMPLETED.value,
                'completed_at': datetime.utcnow().isoformat()
            })
            logger.info(f"Job {job_id} completed with {len(filtered_data)} results")

        except Exception as e:
            error_msg = str(e)
            if errors:
                error_msg += " | Additional errors: " + "; ".join(errors[:2])
            
            logger.error(f"Job {job_id} failed: {error_msg}", exc_info=True)
            
            try:
                await self.storage.update_job(job_id, {
                    'status': JobStatus.FAILED.value,
                    'error': error_msg[:500]  # Limit error length
                })
            except Exception as update_error:
                logger.error(f"Failed to update job status: {update_error}")

    async def _process_crawl_job(self, job: Dict, errors: List[str]) -> List[Dict]:
        """Process a crawl mode job"""
        crawler = WebCrawler(
            max_pages=job.get('max_pages', 10),
            max_depth=job.get('max_depth', 2),
            same_domain=job.get('same_domain', True)
        )
        
        use_javascript = job.get('use_javascript', False)
        search_query = job.get('search_query')
        
        try:
            if search_query:
                logger.info(f"Crawling from search: {search_query}")
                
                # First try with JavaScript if enabled
                if use_javascript:
                    try:
                        return await crawler.crawl_from_search(
                            search_query=search_query,
                            max_pages=job.get('max_pages', 10),
                            use_javascript=True
                        )
                    except Exception as e:
                        errors.append(f"JS crawl failed: {str(e)[:100]}")
                        logger.warning(f"JavaScript crawl failed, trying without: {e}")
                
                # Try without JavaScript
                return await crawler.crawl_from_search(
                    search_query=search_query,
                    max_pages=job.get('max_pages', 10),
                    use_javascript=False
                )
            else:
                # Crawl from URL
                start_urls = [job['url']] if job.get('url') else []
                if not start_urls:
                    raise Exception("No URL or search query provided")
                
                return await crawler.crawl(
                    start_urls=start_urls,
                    use_javascript=use_javascript
                )
        except Exception as e:
            errors.append(str(e)[:200])
            logger.error(f"Crawl failed: {e}")
            return []

    async def _process_single_url_job(self, job: Dict, errors: List[str]) -> List[Dict]:
        """Process a single URL scrape job"""
        if not job.get('url'):
            raise Exception("URL is required for single page scraping")
        
        url = job['url']
        use_javascript = job.get('use_javascript', False)
        
        logger.info(f"Scraping: {url} (JS: {use_javascript})")
        
        # Check for special site handling
        if 'opentable.com' in url.lower():
            use_javascript = True  # OpenTable always needs JS
            logger.info("Detected OpenTable - using JavaScript rendering")
        
        try:
            # Try with JavaScript first if enabled
            if use_javascript:
                try:
                    data = await self.scraper.scrape(url, use_javascript=True)
                    return [data]
                except Exception as e:
                    errors.append(f"JS scrape failed: {str(e)[:100]}")
                    logger.warning(f"JavaScript scraping failed, trying static: {e}")
            
            # Try static scraping
            data = await self.scraper.scrape(url, use_javascript=False)
            return [data]
            
        except Exception as e:
            errors.append(str(e)[:200])
            logger.error(f"Scraping failed for {url}: {e}")
            return []

    async def _apply_ai_filter(self, data: List[Dict], prompt: str, errors: List[str]) -> List[Dict]:
        """Apply AI filtering to scraped data"""
        logger.info(f"Applying AI filter to {len(data)} items")
        
        ai_filtered = []
        for idx, page_data in enumerate(data):
            try:
                result = await self.ai_filter.filter_and_structure(page_data, prompt)
                if isinstance(result, list):
                    ai_filtered.extend(result)
                else:
                    ai_filtered.append(result)
            except Exception as e:
                errors.append(f"AI filter error on item {idx+1}: {str(e)[:50]}")
                logger.warning(f"AI filtering failed for item {idx + 1}: {e}")
                # Include original data if AI fails
                ai_filtered.append(page_data)
        
        logger.info(f"AI filtering complete: {len(ai_filtered)} items")
        return ai_filtered if ai_filtered else data
