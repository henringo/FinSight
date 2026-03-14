from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.database import get_db
from app.models import Indicator
from app.schemas import IndicatorsListResponse, IndicatorResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/indicators", response_model=IndicatorsListResponse)
async def get_indicators(
    ticker: str = Query(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db),
):
    """Get technical indicators for a ticker"""
    try:
        # Count total
        count_stmt = select(func.count()).where(Indicator.ticker == ticker.upper())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # Get indicators
        stmt = (
            select(Indicator)
            .where(Indicator.ticker == ticker.upper())
            .order_by(Indicator.ts.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await db.execute(stmt)
        indicators = result.scalars().all()
        
        return IndicatorsListResponse(
            indicators=[IndicatorResponse.model_validate(i) for i in indicators],
            total=total,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.error(f"Error fetching indicators: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch indicators",
        )
