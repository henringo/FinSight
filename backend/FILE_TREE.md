# Backend File Structure

```
backend/
├── .dockerignore
├── Dockerfile
├── requirements.txt
├── run.py
└── app/
    ├── __init__.py
    ├── main.py                 # FastAPI application entry point
    ├── config.py               # Configuration and settings
    ├── database.py             # SQLAlchemy async setup
    ├── models.py               # SQLAlchemy ORM models
    ├── schemas.py              # Pydantic response/request models
    ├── redis_client.py         # Redis client and cache helpers
    ├── logging_config.py       # Structured JSON logging setup
    ├── middleware.py           # Rate limiting and logging middleware
    ├── celery_app.py           # Celery configuration
    ├── tasks.py                # Celery background tasks
    └── routes/
        ├── __init__.py
        ├── health.py           # GET /health
        ├── tickers.py          # GET /tickers
        ├── prices.py           # GET /prices
        ├── indicators.py       # GET /indicators
        ├── summary.py          # GET /summary, POST /summary/generate
        └── jobs.py             # GET /jobs/{job_id}
```

## Key Features Implemented

✅ **FastAPI** with async/await support
✅ **SQLAlchemy 2.0** async with asyncpg
✅ **Redis** for caching and rate limiting
✅ **Celery** for background job processing
✅ **Gzip** compression middleware
✅ **Structured JSON** logging
✅ **Token bucket** rate limiting (60 req/min per IP)
✅ **Pydantic v2** models for validation
✅ **Organized routes** in separate modules
✅ **Error handling** and input validation
✅ **Docker** support with Python 3.11
