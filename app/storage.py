from supabase import create_client, Client
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class Storage:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found in environment")

        self.client: Client = create_client(supabase_url, supabase_key)

    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new scraping job"""
        response = self.client.table('scrape_jobs').insert(job_data).execute()
        return response.data[0] if response.data else None

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a job by ID"""
        response = self.client.table('scrape_jobs').select('*').eq('id', job_id).maybeSingle().execute()
        return response.data

    async def update_job(self, job_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a job"""
        response = self.client.table('scrape_jobs').update(updates).eq('id', job_id).execute()
        return response.data[0] if response.data else None

    async def save_results(self, job_id: str, results: List[Dict[str, Any]]) -> None:
        """Save scraping results"""
        data = [{'job_id': job_id, 'data': result} for result in results]
        self.client.table('scrape_results').insert(data).execute()

    async def get_results(self, job_id: str) -> List[Dict[str, Any]]:
        """Get results for a job"""
        response = self.client.table('scrape_results').select('*').eq('job_id', job_id).execute()
        return response.data if response.data else []
