from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from app.config import settings
from app.middleware import RateLimitMiddleware, LoggingMiddleware
from app.routes import health, tickers, prices, indicators, summary, jobs
from app.logging_config import logger
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting FinSight Backend API")
    yield
    # Shutdown
    logger.info("Shutting down FinSight Backend API")
    from app.redis_client import RedisClient
    await RedisClient.close()


app = FastAPI(
    title="FinSight AI API",
    description="Financial insights and AI-powered analysis API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware (order matters - last added is first executed)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(tickers.router, tags=["tickers"])
app.include_router(prices.router, tags=["prices"])
app.include_router(indicators.router, tags=["indicators"])
app.include_router(summary.router, tags=["summary"])
app.include_router(jobs.router, tags=["jobs"])


@app.get("/")
async def root():
    return {
        "service": "FinSight AI Backend",
        "version": "1.0.0",
        "docs": "/docs",
    }
