import asyncio
from typing import Dict, Any
from datetime import datetime
from .scraper import WebScraper
from .ai_filter import AIFilter
from .storage import Storage
from .models import JobStatus


class ScraperWorker:
    def __init__(self):
        self.scraper = WebScraper()
        self.ai_filter = AIFilter()
        self.storage = Storage()

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

            # Scrape the URL
            scraped_data = await self.scraper.scrape(job['url'])

            # Apply AI filtering if prompt provided
            if job.get('ai_prompt'):
                filtered_data = await self.ai_filter.filter_and_structure(
                    scraped_data,
                    job['ai_prompt']
                )
            else:
                filtered_data = [scraped_data]

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
