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
            missing = []
            if not supabase_url:
                missing.append("SUPABASE_URL")
            if not supabase_key:
                missing.append("SUPABASE_ANON_KEY")
            
            error_msg = (
                f"Supabase credentials not found in environment.\n"
                f"Missing variables: {', '.join(missing)}\n\n"
                f"Please set the following environment variables:\n"
                f"  - SUPABASE_URL: Your Supabase project URL\n"
                f"  - SUPABASE_ANON_KEY: Your Supabase anonymous key\n\n"
                f"You can:\n"
                f"  1. Create a .env file in the project root with these variables\n"
                f"  2. Set them as environment variables in your system\n"
                f"  3. Set them in your deployment platform (Render, etc.)\n\n"
                f"Example .env file:\n"
                f"  SUPABASE_URL=https://your-project.supabase.co\n"
                f"  SUPABASE_ANON_KEY=your-anon-key-here"
            )
            raise ValueError(error_msg)

        # Create Supabase client
        # Using positional arguments to avoid any proxy-related issues
        try:
            self.client: Client = create_client(supabase_url, supabase_key)
        except TypeError as e:
            if 'proxy' in str(e).lower():
                # Fallback: try with explicit keyword arguments
                self.client: Client = create_client(
                    supabase_url=supabase_url,
                    supabase_key=supabase_key
                )
            else:
                raise

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
