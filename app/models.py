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
    url: HttpUrl
    filters: Optional[Dict[str, Any]] = None
    ai_prompt: Optional[str] = None
    export_format: Optional[str] = "json"


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
