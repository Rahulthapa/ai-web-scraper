from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScrapeJobCreate(BaseModel):
    url: Optional[HttpUrl] = None  # Optional for crawl mode
    search_query: Optional[str] = None  # For web crawling mode
    crawl_mode: Optional[bool] = False  # Enable web crawling
    max_pages: Optional[int] = 10  # Max pages to crawl
    max_depth: Optional[int] = 2  # Max crawl depth
    same_domain: Optional[bool] = True  # Only crawl same domain
    filters: Optional[Dict[str, Any]] = None
    ai_prompt: Optional[str] = None
    export_format: Optional[str] = "json"
    use_javascript: Optional[bool] = False  # Use Playwright for JS-rendered pages


class ScrapeJob(BaseModel):
    id: str
    url: str
    status: JobStatus
    filters: Optional[Dict[str, Any]] = None
    ai_prompt: Optional[str] = None
    export_format: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class ScrapeResult(BaseModel):
    job_id: str
    data: List[Dict[str, Any]]
    total_items: int
    filtered_items: int
