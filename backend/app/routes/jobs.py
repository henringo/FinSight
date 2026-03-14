from fastapi import APIRouter, HTTPException, Path, status
from app.schemas import JobStatusResponse
from app.celery_app import celery_app
from celery.result import AsyncResult
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str = Path(..., description="Celery job ID")):
    """Get status of a Celery job"""
    try:
        task_result = AsyncResult(job_id, app=celery_app)
        
        if task_result.state == "PENDING":
            status_str = "pending"
            result = None
            error = None
        elif task_result.state == "PROGRESS":
            status_str = "in_progress"
            result = task_result.info
            error = None
        elif task_result.state == "SUCCESS":
            status_str = "completed"
            result = task_result.result
            error = None
        elif task_result.state == "FAILURE":
            status_str = "failed"
            result = None
            error = str(task_result.info)
        else:
            status_str = task_result.state.lower()
            result = task_result.info if task_result.info else None
            error = None
        
        return JobStatusResponse(
            job_id=job_id,
            status=status_str,
            result=result,
            error=error,
        )
    except Exception as e:
        logger.error(f"Error fetching job status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch job status",
        )
