from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from typing import Optional
import uuid
import json
import os
import logging
from datetime import datetime

from .models import ScrapeJobCreate, ScrapeJob, ScrapeResult, JobStatus
from .storage import Storage
from .worker import ScraperWorker
from .exporter import DataExporter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Global exception handler to ensure all errors return JSON
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions and return JSON responses"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {str(exc)}"
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and return JSON responses"""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors()
        }
    )

# Initialize storage and worker (lazy initialization to handle missing credentials gracefully)
storage = None
worker = None
exporter = DataExporter()

def get_storage():
    """Get storage instance, initializing if needed"""
    global storage
    if storage is None:
        try:
            storage = Storage()
        except ValueError as e:
            # Re-raise with helpful message
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
    return storage

def get_worker():
    """Get worker instance, initializing if needed"""
    global worker
    if worker is None:
        storage_instance = get_storage()
        worker = ScraperWorker(storage_instance=storage_instance)
    return worker


# Serve frontend static files if they exist
dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")
if os.path.exists(dist_path):
    # Mount assets directory at /assets (Vite's default output path)
    assets_path = os.path.join(dist_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    
    @app.get("/")
    @app.head("/")
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
    @app.head("/")
    async def root():
        return JSONResponse(
            status_code=200,
            content={
                "message": "AI Web Scraper API",
                "version": "1.0.0",
                "status": "running",
                "frontend": "not_built",
                "instructions": {
                    "step1": "Install Node.js from https://nodejs.org/ (version 18+)",
                    "step2": "Run: npm install",
                    "step3": "Run: npm run build",
                    "step4": "Restart the server",
                    "alternative": "Or run 'npm run dev' in a separate terminal for development mode"
                },
                "api_docs": "/docs",
                "health_check": "/health"
            }
        )


@app.get("/health")
@app.head("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Try to initialize storage to check if credentials are set
        get_storage()
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "not_configured",
            "message": "Supabase credentials not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
        }


@app.post("/jobs", response_model=ScrapeJob, status_code=201)
async def create_job(job_request: ScrapeJobCreate, background_tasks: BackgroundTasks):
    """Create a new scraping job"""
    try:
        storage_instance = get_storage()
        worker_instance = get_worker()
        
        job_id = str(uuid.uuid4())
        
        # Build job data - only include fields that exist in the database
        # This handles cases where migration hasn't been applied yet
        job_data = {
            'id': job_id,
            'url': str(job_request.url) if job_request.url else None,
            'status': JobStatus.PENDING.value,
            'filters': job_request.filters,
            'ai_prompt': job_request.ai_prompt,
            'export_format': job_request.export_format or 'json',
            'created_at': datetime.utcnow().isoformat(),
        }
        
        # Add crawl-related fields only if crawl_mode is enabled
        # Note: These fields will cause an error if the database migration hasn't been run
        if job_request.crawl_mode:
            job_data.update({
                'crawl_mode': True,
                'search_query': job_request.search_query,
                'max_pages': job_request.max_pages or 10,
                'max_depth': job_request.max_depth or 2,
                'same_domain': job_request.same_domain if job_request.same_domain is not None else True,
            })
        
        # Add JavaScript rendering field
        # Note: This field will cause an error if the database migration hasn't been run
        if job_request.use_javascript:
            job_data['use_javascript'] = True
        
        # Validate: need either URL or search_query
        if not job_data.get('url') and not job_data.get('search_query'):
            raise HTTPException(
                status_code=400,
                detail="Either 'url' or 'search_query' must be provided"
            )
        
        job = await storage_instance.create_job(job_data)
        
        if not job:
            raise HTTPException(status_code=500, detail="Failed to create job")
        
        # Process job in background with proper error handling
        # FastAPI BackgroundTasks supports async functions directly
        async def process_job_wrapper():
            """Wrapper to ensure background task errors are logged"""
            try:
                await worker_instance.process_job(job_id)
            except Exception as e:
                logger.error(f"Background task failed for job {job_id}: {str(e)}", exc_info=True)
                # Update job status to failed
                try:
                    storage = get_storage()
                    await storage.update_job(job_id, {
                        'status': JobStatus.FAILED.value,
                        'error': str(e)
                    })
                except Exception as update_error:
                    logger.error(f"Failed to update job status: {update_error}")
        
        background_tasks.add_task(process_job_wrapper)
        logger.info(f"Job {job_id} created and queued for processing")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the full error for debugging
        logger.error(f"Error creating job: {str(e)}", exc_info=True)
        
        # Check if it's a database schema error
        error_str = str(e).lower()
        if 'crawl_mode' in error_str or 'pgrst' in error_str or 'column' in error_str:
            raise HTTPException(
                status_code=500,
                detail=f"Database schema error: {str(e)}. Please run the migration SQL in Supabase and refresh the schema cache. See database_migration.sql for details."
            )
        
        raise HTTPException(status_code=500, detail=f"Error creating job: {str(e)}")


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status by ID"""
    try:
        logger.info(f"Fetching job {job_id}")
        storage_instance = get_storage()
        job = await storage_instance.get_job(job_id)
        
        if not job:
            logger.warning(f"Job {job_id} not found")
            raise HTTPException(status_code=404, detail="Job not found")
        
        logger.debug(f"Raw job data: {job}")
        
        # Normalize status to ensure it's a valid JobStatus enum value
        status = job.get('status', 'pending')
        if status not in ['pending', 'running', 'completed', 'failed']:
            logger.warning(f"Invalid status '{status}' for job {job_id}, defaulting to 'pending'")
            status = 'pending'
        
        # Normalize and ensure all fields are present
        normalized_job = {
            'id': str(job.get('id', job_id)),
            'url': job.get('url'),
            'status': status,
            'filters': job.get('filters'),
            'ai_prompt': job.get('ai_prompt'),
            'export_format': job.get('export_format', 'json'),
            'crawl_mode': bool(job.get('crawl_mode', False)) if job.get('crawl_mode') is not None else False,
            'search_query': job.get('search_query'),
            'max_pages': job.get('max_pages'),
            'max_depth': job.get('max_depth'),
            'same_domain': job.get('same_domain'),
            'use_javascript': bool(job.get('use_javascript', False)) if job.get('use_javascript') is not None else False,
            'error': job.get('error'),
        }
        
        # Handle created_at - convert to datetime object
        created_at = job.get('created_at')
        try:
            if created_at:
                if isinstance(created_at, str):
                    # Try multiple datetime formats
                    created_at_clean = created_at.strip()
                    parsed = False
                    
                    # Try dateutil parser first (more flexible)
                    try:
                        from dateutil import parser as date_parser
                        normalized_job['created_at'] = date_parser.parse(created_at_clean)
                        parsed = True
                    except (ImportError, ValueError, AttributeError):
                        pass
                    
                    if not parsed:
                        # Try ISO format
                        try:
                            # Remove timezone info
                            created_at_clean = created_at_clean.replace('Z', '').replace('+00:00', '').strip()
                            if 'T' in created_at_clean:
                                # Remove microseconds if present
                                if '.' in created_at_clean:
                                    parts = created_at_clean.split('.')
                                    created_at_clean = parts[0]
                                normalized_job['created_at'] = datetime.fromisoformat(created_at_clean)
                            else:
                                # Try standard format
                                normalized_job['created_at'] = datetime.strptime(created_at_clean, '%Y-%m-%d %H:%M:%S')
                            parsed = True
                        except (ValueError, AttributeError):
                            logger.warning(f"Could not parse created_at: {created_at}, using current time")
                            normalized_job['created_at'] = datetime.utcnow()
                elif hasattr(created_at, 'isoformat'):
                    normalized_job['created_at'] = created_at
                else:
                    normalized_job['created_at'] = datetime.utcnow()
            else:
                normalized_job['created_at'] = datetime.utcnow()
        except Exception as e:
            logger.warning(f"Error parsing created_at: {e}, using current time")
            normalized_job['created_at'] = datetime.utcnow()
        
        # Handle completed_at
        completed_at = job.get('completed_at')
        try:
            if completed_at:
                if isinstance(completed_at, str):
                    completed_at_clean = completed_at.strip()
                    parsed = False
                    
                    # Try dateutil parser first
                    try:
                        from dateutil import parser as date_parser
                        normalized_job['completed_at'] = date_parser.parse(completed_at_clean)
                        parsed = True
                    except (ImportError, ValueError, AttributeError):
                        pass
                    
                    if not parsed:
                        try:
                            completed_at_clean = completed_at_clean.replace('Z', '').replace('+00:00', '').strip()
                            if 'T' in completed_at_clean:
                                if '.' in completed_at_clean:
                                    completed_at_clean = completed_at_clean.split('.')[0]
                                normalized_job['completed_at'] = datetime.fromisoformat(completed_at_clean)
                            else:
                                normalized_job['completed_at'] = datetime.strptime(completed_at_clean, '%Y-%m-%d %H:%M:%S')
                        except (ValueError, AttributeError):
                            normalized_job['completed_at'] = None
                elif hasattr(completed_at, 'isoformat'):
                    normalized_job['completed_at'] = completed_at
                else:
                    normalized_job['completed_at'] = None
            else:
                normalized_job['completed_at'] = None
        except Exception as e:
            logger.warning(f"Error parsing completed_at: {e}")
            normalized_job['completed_at'] = None
        
        # Validate and return using response model
        try:
            result = ScrapeJob(**normalized_job)
            logger.info(f"Successfully fetched job {job_id}")
            return result
        except Exception as model_error:
            logger.error(f"Pydantic validation error for job {job_id}: {model_error}")
            logger.error(f"Model error type: {type(model_error).__name__}")
            logger.error(f"Normalized job keys: {list(normalized_job.keys())}")
            logger.error(f"Normalized job values: {normalized_job}")
            
            # Try to return a simplified version that matches the model
            # Remove None values that might cause issues
            simplified_job = {k: v for k, v in normalized_job.items() if v is not None or k in ['id', 'status', 'created_at', 'export_format']}
            
            try:
                # Try again with simplified data
                result = ScrapeJob(**simplified_job)
                return result
            except Exception as e2:
                logger.error(f"Second validation attempt also failed: {e2}")
                # Last resort: return minimal valid job object
                try:
                    minimal_job = {
                        'id': normalized_job.get('id', job_id),
                        'status': JobStatus.PENDING,
                        'export_format': normalized_job.get('export_format', 'json'),
                        'created_at': normalized_job.get('created_at', datetime.utcnow()),
                        'url': normalized_job.get('url'),
                        'crawl_mode': normalized_job.get('crawl_mode', False),
                        'use_javascript': normalized_job.get('use_javascript', False),
                    }
                    return ScrapeJob(**minimal_job)
                except Exception as e3:
                    logger.error(f"Even minimal job creation failed: {e3}")
                    # Return raw data as JSON (bypass Pydantic)
                    return JSONResponse(
                        status_code=200,
                        content={
                            'id': job_id,
                            'status': status,
                            'url': job.get('url'),
                            'created_at': job.get('created_at'),
                            'error': f'Validation error: {str(model_error)}'
                        }
                    )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {str(e)}", exc_info=True)
        logger.error(f"Exception type: {type(e).__name__}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching job: {str(e)}"
        )


@app.get("/jobs/{job_id}/results", response_model=ScrapeResult)
async def get_job_results(job_id: str):
    """Get scraping results for a job"""
    storage_instance = get_storage()
    
    # Check if job exists
    job = await storage_instance.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get results
    results = await storage_instance.get_results(job_id)
    
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
    storage_instance = get_storage()
    
    # Check if job exists
    job = await storage_instance.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.get('status') != JobStatus.COMPLETED.value:
        raise HTTPException(
            status_code=400, 
            detail=f"Job is not completed. Current status: {job.get('status')}"
        )
    
    # Get results
    results = await storage_instance.get_results(job_id)
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
