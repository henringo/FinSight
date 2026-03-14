from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime


class TickerResponse(BaseModel):
    tickers: List[str]


class PriceResponse(BaseModel):
    id: UUID
    ticker: str
    ts: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    source: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PricesListResponse(BaseModel):
    prices: List[PriceResponse]
    total: int
    limit: int
    offset: int


class IndicatorResponse(BaseModel):
    id: UUID
    ticker: str
    ts: datetime
    ma20: Optional[float] = None
    rsi14: Optional[float] = None
    vol30d: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class IndicatorsListResponse(BaseModel):
    indicators: List[IndicatorResponse]
    total: int
    limit: int
    offset: int


class SummaryResponse(BaseModel):
    id: UUID
    ticker: str
    bucket: str
    summary_text: str
    model_version: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GenerateSummaryRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    bucket: str = Field(..., min_length=1, max_length=10)

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v):
        return v.upper().strip()

    @field_validator("bucket")
    @classmethod
    def validate_bucket(cls, v):
        return v.lower().strip()


class GenerateSummaryResponse(BaseModel):
    job_id: str
    ticker: str
    bucket: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
