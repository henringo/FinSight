from app.celery_app import celery_app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.models import AISummary, Price, Indicator
from app.config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create async engine for Celery tasks
engine = create_async_engine(
    settings.SUPABASE_DB_URL,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@celery_app.task(name="generate_summary", bind=True)
def generate_summary_task(self, ticker: str, bucket: str):
    """
    Generate AI summary for a ticker and bucket.
    This is a placeholder - implement actual AI generation logic here.
    """
    import asyncio
    
    async def _generate():
        try:
            # Update task state
            self.update_state(state="PROGRESS", meta={"progress": 10, "message": "Fetching data"})
            
            # Fetch recent prices and indicators
            async with AsyncSessionLocal() as session:
                # Get latest prices
                prices_stmt = (
                    select(Price)
                    .where(Price.ticker == ticker)
                    .order_by(Price.ts.desc())
                    .limit(100)
                )
                prices_result = await session.execute(prices_stmt)
                prices = prices_result.scalars().all()
                
                self.update_state(state="PROGRESS", meta={"progress": 50, "message": "Analyzing data"})
                
                # Get latest indicators
                indicators_stmt = (
                    select(Indicator)
                    .where(Indicator.ticker == ticker)
                    .order_by(Indicator.ts.desc())
                    .limit(10)
                )
                indicators_result = await session.execute(indicators_stmt)
                indicators = indicators_result.scalars().all()
                
                self.update_state(state="PROGRESS", meta={"progress": 80, "message": "Generating summary"})
                
                # TODO: Implement actual AI summary generation
                # For now, create a placeholder summary
                summary_text = f"Summary for {ticker} ({bucket}): Analysis of {len(prices)} price points and {len(indicators)} indicators. [AI generation placeholder]"
                
                # Check if summary already exists
                existing_stmt = select(AISummary).where(
                    AISummary.ticker == ticker,
                    AISummary.bucket == bucket,
                )
                existing_result = await session.execute(existing_stmt)
                existing = existing_result.scalar_one_or_none()
                
                if existing:
                    # Update existing
                    existing.summary_text = summary_text
                    existing.model_version = "v1.0"
                else:
                    # Create new
                    new_summary = AISummary(
                        ticker=ticker,
                        bucket=bucket,
                        summary_text=summary_text,
                        model_version="v1.0",
                    )
                    session.add(new_summary)
                
                await session.commit()
                
                self.update_state(state="PROGRESS", meta={"progress": 100, "message": "Complete"})
                
                return {
                    "ticker": ticker,
                    "bucket": bucket,
                    "summary_generated": True,
                    "message": "Summary generated successfully",
                }
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            raise
    
    # Run async function in sync context
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_generate())
