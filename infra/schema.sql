-- FinSight AI Database Schema
-- Compatible with PostgreSQL and Supabase
-- Requires pgvector extension for vector similarity search

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- PRICES TABLE
-- Stores historical price data for financial instruments
-- ============================================================================
CREATE TABLE prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume NUMERIC,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index: Optimized for time-series queries by ticker
-- Most common query pattern: "Get prices for ticker X ordered by time descending"
-- Composite index on (ticker, ts DESC) allows efficient range scans and sorting
CREATE INDEX idx_prices_ticker_ts ON prices(ticker, ts DESC);

COMMENT ON INDEX idx_prices_ticker_ts IS 'Enables fast time-series queries by ticker with descending time order. Supports queries like "latest prices for AAPL" without sorting.';

-- ============================================================================
-- INDICATORS TABLE
-- Stores calculated technical indicators (moving averages, RSI, etc.)
-- ============================================================================
CREATE TABLE indicators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    ma20 NUMERIC,
    rsi14 NUMERIC,
    vol30d NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index: Optimized for time-series queries by ticker
-- Similar to prices table - most queries fetch latest indicators for a ticker
CREATE INDEX idx_indicators_ticker_ts ON indicators(ticker, ts DESC);

COMMENT ON INDEX idx_indicators_ticker_ts IS 'Enables fast retrieval of latest technical indicators by ticker. Supports queries like "current RSI for AAPL" with efficient time-based filtering.';

-- ============================================================================
-- AI_SUMMARIES TABLE
-- Stores AI-generated summaries organized by time buckets (daily, weekly, etc.)
-- ============================================================================
CREATE TABLE ai_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker TEXT NOT NULL,
    bucket TEXT NOT NULL,
    summary_text TEXT NOT NULL,
    model_version TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, bucket)
);

-- Index: Optimized for lookups by ticker and bucket
-- Unique constraint already creates an index, but explicit index ensures optimal query plans
-- Most common query: "Get summary for ticker X in bucket Y"
CREATE INDEX idx_ai_summaries_ticker_bucket ON ai_summaries(ticker, bucket);

COMMENT ON INDEX idx_ai_summaries_ticker_bucket IS 'Enables fast lookups of summaries by ticker and time bucket. The unique constraint prevents duplicate summaries for the same ticker/bucket combination.';

-- ============================================================================
-- DOCUMENTS TABLE
-- Stores documents with vector embeddings for semantic search
-- ============================================================================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_type TEXT,
    title TEXT,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index: IVFFlat index for vector similarity search
-- IVFFlat is optimized for approximate nearest neighbor search on embeddings
-- Required for semantic search queries like "find documents similar to this embedding"
-- Note: Requires sufficient data for optimal performance (typically 1000+ vectors)
CREATE INDEX idx_documents_embedding ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

COMMENT ON INDEX idx_documents_embedding IS 'IVFFlat index enables fast approximate vector similarity search using cosine distance. Essential for semantic search queries on document embeddings. Lists parameter balances accuracy vs speed.';

-- Index: GIN index for JSONB metadata queries
-- GIN (Generalized Inverted Index) is optimal for JSONB containment and key-value queries
-- Supports queries like "find documents where metadata->tags contains 'earnings'"
CREATE INDEX idx_documents_metadata ON documents USING gin (metadata);

COMMENT ON INDEX idx_documents_metadata IS 'GIN index enables fast queries on JSONB metadata fields. Supports containment operators (@>, ?), key existence checks, and efficient filtering on nested JSON properties.';

-- ============================================================================
-- QA_CACHE TABLE
-- Caches question-answer pairs to avoid redundant AI API calls
-- ============================================================================
CREATE TABLE qa_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_hash TEXT UNIQUE NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

-- Index: Optimized for hash lookups and expiration cleanup
-- Unique constraint on question_hash already creates an index for fast lookups
-- Additional index on expires_at enables efficient cleanup of expired entries
CREATE INDEX idx_qa_cache_expires_at ON qa_cache(expires_at);

COMMENT ON INDEX idx_qa_cache_expires_at IS 'Enables efficient cleanup of expired cache entries. Supports queries like "delete all entries where expires_at < now()" for cache maintenance jobs.';

COMMENT ON TABLE qa_cache IS 'Caches AI-generated answers keyed by question hash. The unique constraint on question_hash ensures one answer per question and enables O(1) lookups.';
