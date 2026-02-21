# FinSight AI

A full-stack AI-powered financial insights platform built as a mono-repo.

## Structure

- **backend**: API server and core business logic
- **worker**: Background job processing and async tasks
- **frontend**: Web application interface
- **infra**: Infrastructure as code and deployment configurations

## Getting Started

1. Copy `.env.example` to `.env` and fill in your service credentials
2. Run `docker-compose up` to start Redis, backend, and worker
3. To include local PostgreSQL: `docker-compose --profile local-db up`
4. Follow individual service READMEs for specific setup instructions

## Services

- **Backend**: REST API and GraphQL endpoints
- **Worker**: Background job processing
- **Frontend**: React/Next.js application
- **PostgreSQL**: Primary database (optional local instance)
- **Redis**: Caching and job queue
