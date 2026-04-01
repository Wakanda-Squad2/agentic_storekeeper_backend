# Agentic Storekeeper Backend

FastAPI backend for intelligent document and transaction management system.

## Features

- **Document Management**: Upload, store, and manage financial documents
- **Transaction Tracking**: Record and categorize income/expense transactions
- **AI-Powered Analytics**: Chat interface for querying financial data
- **Multi-tenancy**: Built-in tenant isolation for SaaS deployment
- **Dashboard**: Visual analytics and trend analysis

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── database.py          # SQLAlchemy database setup
├── models/              # SQLAlchemy models
│   ├── document.py
│   ├── transaction.py
│   ├── vendor.py
│   └── category.py
├── schemas/             # Pydantic schemas
│   ├── document.py
│   └── transaction.py
├── api/                 # API route handlers
│   ├── documents.py     # Document CRUD endpoints
│   ├── transactions.py  # Transaction CRUD endpoints
│   ├── dashboard.py     # Analytics endpoints
│   └── chat.py          # AI chat endpoints
├── agents/              # AI agents directory
├── mcp_tools/           # MCP tools directory
└── services/            # Business logic services
```

## Technologies

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **UUID** - File naming and identification

## Models

### Document
- id, tenant_id, filename, file_path, file_type
- document_type, status (pending/processing/completed/failed)
- created_at, updated_at

### Transaction
- id, tenant_id, document_id (FK)
- date, description, amount, currency (default: NGN)
- type (income/expense), category, vendor, reference
- confidence (AI extraction score), created_at

### Vendor
- id, tenant_id, name, created_at

### Category
- id, name, type (income/expense)

## API Endpoints

### Documents
- `POST /api/v1/documents/` - Upload document
- `GET /api/v1/documents/` - List documents (with pagination)
- `GET /api/v1/documents/{id}` - Get document details
- `PATCH /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document

### Transactions
- `POST /api/v1/transactions/` - Create transaction
- `GET /api/v1/transactions/` - List transactions (with filters)
- `GET /api/v1/transactions/{id}` - Get transaction details
- `PATCH /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction
- `GET /api/v1/transactions/summary/dashboard` - Get summary statistics

### Dashboard
- `GET /api/v1/dashboard/summary` - Comprehensive dashboard data
- `GET /api/v1/dashboard/category-breakdown` - Category analytics
- `GET /api/v1/dashboard/trend-data` - Trend visualization data

### Chat (AI Assistant)
- `POST /api/v1/chat/` - Chat with AI about financial data
- `POST /api/v1/chat/ask-about-document` - Ask about specific document
- `POST /api/v1/chat/analyze-trends` - AI trend analysis
- `GET /api/v1/chat/conversation-history` - Chat history

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure database in `.env`:
   ```
   database_url=postgresql://user:password@localhost/storekeeper_db
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Database

Alembic migrations are provided in the `migrations/` directory:
- `migrations/versions/001_initial_migration_add_all_models.py` - Initial schema

Run migrations:
```bash
alembic upgrade head
```

## Multi-tenancy

All models include `tenant_id` for multi-tenant isolation. The current implementation uses a placeholder tenant_id (set to 1) which should be replaced with authentication-based tenant extraction in production.
