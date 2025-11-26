from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
import uuid
import json
import os
from datetime import datetime

from .models import ScrapeJobCreate, ScrapeJob, ScrapeResult, JobStatus
from .storage import Storage
from .worker import ScraperWorker
from .exporter import DataExporter

app = FastAPI(
    title="AI Web Scraper",
    description="Intelligent web scraping API with AI-powered filtering and data extraction",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage and worker
storage = Storage()
worker = ScraperWorker()
exporter = DataExporter()


# Serve frontend static files if they exist
dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")
if os.path.exists(dist_path):
    app.mount("/static", StaticFiles(directory=os.path.join(dist_path, "assets")), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend application"""
        index_path = os.path.join(dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {
            "message": "AI Web Scraper API",
            "version": "1.0.0",
            "status": "running"
        }
else:
    @app.get("/")
    async def root():
        return {
            "message": "AI Web Scraper API",
            "version": "1.0.0",
            "status": "running",
            "frontend": "Build the frontend with 'npm run build' to enable the web interface"
        }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/jobs", response_model=ScrapeJob, status_code=201)
async def create_job(job_request: ScrapeJobCreate, background_tasks: BackgroundTasks):
    """Create a new scraping job"""
    try:
        job_id = str(uuid.uuid4())
        job_data = {
            'id': job_id,
            'url': str(job_request.url),
            'status': JobStatus.PENDING.value,
            'filters': job_request.filters,
            'ai_prompt': job_request.ai_prompt,
            'export_format': job_request.export_format or 'json',
            'created_at': datetime.utcnow().isoformat(),
        }
        
        job = await storage.create_job(job_data)
        
        if not job:
            raise HTTPException(status_code=500, detail="Failed to create job")
        
        # Process job in background
        background_tasks.add_task(worker.process_job, job_id)
        
        return job
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating job: {str(e)}")


@app.get("/jobs/{job_id}", response_model=ScrapeJob)
async def get_job(job_id: str):
    """Get job status by ID"""
    job = await storage.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@app.get("/jobs/{job_id}/results", response_model=ScrapeResult)
async def get_job_results(job_id: str):
    """Get scraping results for a job"""
    # Check if job exists
    job = await storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get results
    results = await storage.get_results(job_id)
    
    # Extract data from results
    data = [result.get('data', result) for result in results]
    
    return ScrapeResult(
        job_id=job_id,
        data=data,
        total_items=len(data),
        filtered_items=len(data)
    )


@app.get("/jobs/{job_id}/export")
async def export_job_results(
    job_id: str,
    format: str = Query("json", regex="^(json|csv|excel)$")
):
    """Export job results in specified format"""
    # Check if job exists
    job = await storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.get('status') != JobStatus.COMPLETED.value:
        raise HTTPException(
            status_code=400, 
            detail=f"Job is not completed. Current status: {job.get('status')}"
        )
    
    # Get results
    results = await storage.get_results(job_id)
    data = [result.get('data', result) for result in results]
    
    if not data:
        raise HTTPException(status_code=404, detail="No results found for this job")
    
    # Export based on format
    if format == "json":
        json_str = exporter.to_json(data)
        return JSONResponse(
            content=json.loads(json_str),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=scrape_results_{job_id}.json"}
        )
    elif format == "csv":
        csv_bytes = exporter.to_csv(data)
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=scrape_results_{job_id}.csv"}
        )
    elif format == "excel":
        excel_bytes = exporter.to_excel(data)
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=scrape_results_{job_id}.xlsx"}
        )
