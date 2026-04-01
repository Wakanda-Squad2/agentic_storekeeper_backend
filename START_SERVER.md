# Running the Agentic Storekeeper Backend Server

This guide provides step-by-step instructions to start the FastAPI server in different environments.

## Quick Start (Development)

### Prerequisites
- Python 3.11 or higher installed
- Dependencies installed: `pip install -r requirements.txt`
- Environment file configured: `.env` (already set up)

### Start the Server
```bash
uvicorn app.main:app --reload
```

The server will start at: **http://localhost:8000**

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

The `--reload` flag automatically restarts the server when code changes.

## Production Setup (PostgreSQL)

### Step 1: PostgreSQL Setup

You have two options:

#### Option A: Using Docker (Recommended)
```bash
# Start PostgreSQL container
docker run --name postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres

# Create database
docker exec -it postgres createdb storekeeper_db -U postgres
```

#### Option B: Local PostgreSQL
Make sure PostgreSQL is installed and running:
```bash
# On macOS with Homebrew
brew services start postgresql

# On Ubuntu/Debian
sudo service postgresql start

# Create database
createdb storekeeper_db
```

### Step 2: Configure Environment

Edit `.env` file:

```bash
# Comment out SQLite line
# database_url=sqlite:///./storekeeper.db

# Uncomment PostgreSQL line
database_url=postgresql://user:password@localhost/storekeeper_db
```

### Step 3: Run Database Migrations

```bash
alembic upgrade head
```

This creates all the necessary tables in the database.

### Step 4: Start the Server

```bash
uvicorn app.main:app --reload
```

## Server Management

### Check if Server is Running
```bash
curl http://localhost:8000/health
```

### Stop the Server
Press `Ctrl+C` in the terminal where the server is running.

### Run in Background
```bash
uvicorn app.main:app > server.log 2>&1 &
tail -f server.log
```

### Use Different Port
```bash
uvicorn app.main:app --reload --port 9000
```

## Troubleshooting

### "Port 8000 already in use"
Use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### "Database connection failed"
- Check if PostgreSQL is running: `pg_isready -h localhost`
- Verify credentials in `.env` file
- Check if database exists: `psql -l | grep storekeeper_db`

### "Module not found" errors
Install dependencies:
```bash
pip install -r requirements.txt
```

### FastAPI version issues
If you encounter version compatibility errors:
```bash
pip install 'fastapi==0.104.1'
```

## API Endpoints

### Documents
- `POST /api/v1/documents/` - Upload document
- `GET /api/v1/documents/` - List documents
- `GET /api/v1/documents/{id}` - Get document by ID
- `PATCH /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document

### Transactions
- `POST /api/v1/transactions/` - Create transaction
- `GET /api/v1/transactions/` - List transactions
- `GET /api/v1/transactions/{id}` - Get transaction by ID
- `PATCH /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction
- `GET /api/v1/transactions/summary/dashboard` - Dashboard summary

### Dashboard
- `GET /api/v1/dashboard/summary` - Complete dashboard data
- `GET /api/v1/dashboard/category-breakdown` - Category analytics
- `GET /api/v1/dashboard/trend-data` - Trend visualization data

### Chat (AI Assistant)
- `POST /api/v1/chat/` - Chat with AI about financial data
- `POST /api/v1/chat/ask-about-document` - Ask about specific document
- `POST /api/v1/chat/analyze-trends` - AI trend analysis
- `GET /api/v1/chat/conversation-history` - Chat history

## Quick Reference

### All-in-one command (Development with SQLite):
```bash
uvicorn app.main:app --reload
```

### All-in-one command (Production with PostgreSQL):
```bash
docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres && \
docker exec -it postgres createdb storekeeper_db -U postgres && \
alembic upgrade head && \
uvicorn app.main:app --reload
```

### Test the API:
```bash
# Health check
curl http://localhost:8000/health

# List documents
curl http://localhost:8000/api/v1/documents/
```
