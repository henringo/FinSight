from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import AISummary
from app.schemas import SummaryResponse, GenerateSummaryRequest, GenerateSummaryResponse
from app.redis_client import get_cache, set_cache
from app.config import settings
from app.celery_app import generate_summary_task
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/summary", response_model=SummaryResponse)
async def get_summary(
    ticker: str = Query(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    bucket: str = Query(..., min_length=1, max_length=10, description="Time bucket (e.g., 1h, 1d)"),
    db: AsyncSession = Depends(get_db),
):
    """Get AI summary for a ticker and bucket. Cached in Redis with 300s TTL."""
    try:
        ticker_upper = ticker.upper()
        bucket_lower = bucket.lower()
        
        # Check cache first
        cache_key = f"summary:{ticker_upper}:{bucket_lower}"
        cached = await get_cache(cache_key)
        if cached:
            logger.info(f"Cache hit for summary: {ticker_upper}:{bucket_lower}")
            return SummaryResponse(**cached)
        
        # Query database
        stmt = select(AISummary).where(
            AISummary.ticker == ticker_upper,
            AISummary.bucket == bucket_lower,
        )
        result = await db.execute(stmt)
        summary = result.scalar_one_or_none()
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Summary not found for ticker {ticker_upper} and bucket {bucket_lower}",
            )
        
        # Convert to response model
        summary_response = SummaryResponse.model_validate(summary)
        
        # Cache the result
        await set_cache(
            cache_key,
            summary_response.model_dump(),
            settings.SUMMARY_CACHE_TTL,
        )
        
        return summary_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch summary",
        )


@router.post("/summary/generate", response_model=GenerateSummaryResponse)
async def generate_summary(
    ticker: str = Query(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    bucket: str = Query(..., min_length=1, max_length=10, description="Time bucket (e.g., 1h, 1d)"),
):
    """Enqueue a Celery job to generate AI summary. Returns job_id for status tracking."""
    try:
        ticker_upper = ticker.upper()
        bucket_lower = bucket.lower()
        
        # Enqueue Celery task
        task = generate_summary_task.delay(ticker_upper, bucket_lower)
        
        logger.info(f"Enqueued summary generation job: {task.id} for {ticker_upper}:{bucket_lower}")
        
        return GenerateSummaryResponse(
            job_id=task.id,
            ticker=ticker_upper,
            bucket=bucket_lower,
            message="Summary generation job enqueued",
        )
    except Exception as e:
        logger.error(f"Error enqueuing summary generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enqueue summary generation job",
        )
