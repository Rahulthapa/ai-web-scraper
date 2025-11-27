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
        try:
            # Update job status to running
            logger.info(f"Updating job {job_id} status to running")
            await self.storage.update_job(job_id, {
                'status': JobStatus.RUNNING.value
            })

            # Get job details
            logger.info(f"Fetching job details for {job_id}")
            job = await self.storage.get_job(job_id)
            if not job:
                raise Exception(f"Job {job_id} not found")
            
            logger.info(f"Job details: mode={'crawl' if job.get('crawl_mode') else 'single'}, url={job.get('url')}, search_query={job.get('search_query')}")

            # Check if this is a crawl job or single URL job
            if job.get('crawl_mode'):
                # Web crawling mode
                logger.info(f"Starting crawl mode for job {job_id}")
                crawler = WebCrawler(
                    max_pages=job.get('max_pages', 10),
                    max_depth=job.get('max_depth', 2),
                    same_domain=job.get('same_domain', True)
                )
                
                use_javascript = job.get('use_javascript', False)
                search_query = job.get('search_query')
                
                if search_query:
                    # Crawl from search query
                    logger.info(f"Crawling from search query: {search_query}")
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
                    
                    logger.info(f"Crawling from URL(s): {start_urls}")
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
                logger.info(f"Crawl completed, found {len(filtered_data)} pages")
            else:
                # Single URL scraping mode
                if not job.get('url'):
                    raise Exception("URL is required for single page scraping")
                
                logger.info(f"Scraping single URL: {job['url']}")
                use_javascript = job.get('use_javascript', False)
                scraped_data = await self.scraper.scrape(job['url'], use_javascript=use_javascript)
                filtered_data = [scraped_data]
                logger.info(f"Scraping completed for {job['url']}")

            # Apply AI filtering if prompt provided
            # Note: filtered_data is already set above based on crawl_mode
            if job.get('ai_prompt') and filtered_data:
                logger.info(f"Applying AI filtering to {len(filtered_data)} pages")
                # Apply AI filtering to each page in the results
                ai_filtered = []
                for idx, page_data in enumerate(filtered_data):
                    try:
                        logger.info(f"Filtering page {idx + 1}/{len(filtered_data)}")
                        result = await self.ai_filter.filter_and_structure(
                            page_data,
                            job['ai_prompt']
                        )
                        ai_filtered.extend(result if isinstance(result, list) else [result])
                    except Exception as e:
                        logger.warning(f"AI filtering failed for page {idx + 1}: {str(e)}")
                        # If AI filtering fails for a page, include original data
                        ai_filtered.append(page_data)
                filtered_data = ai_filtered
                logger.info(f"AI filtering completed, {len(filtered_data)} items after filtering")

            # Save results
            logger.info(f"Saving {len(filtered_data)} results for job {job_id}")
            await self.storage.save_results(job_id, filtered_data)

            # Update job status to completed
            logger.info(f"Marking job {job_id} as completed")
            await self.storage.update_job(job_id, {
                'status': JobStatus.COMPLETED.value,
                'completed_at': datetime.utcnow().isoformat()
            })
            logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            # Update job status to failed
            logger.error(f"Job {job_id} failed with error: {str(e)}", exc_info=True)
            try:
                await self.storage.update_job(job_id, {
                    'status': JobStatus.FAILED.value,
                    'error': str(e)
                })
            except Exception as update_error:
                logger.error(f"Failed to update job status to failed: {str(update_error)}")
            raise
