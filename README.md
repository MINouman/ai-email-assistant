# AI Email Assistant

An intelligent email management system with AI-powered automation using LangChain.

## Key Features

### ✅ Implemented (Phase 1-4)

- **Gmail Integration**: OAuth2 authentication and email fetching
- **AI Email Processing**: 
  - Automatic summarization using LangChain + Groq
  - Intent detection (meeting, urgent, task, follow-up)
  - Priority classification (high, medium, low)
  - Named Entity Recognition (people, dates, locations, organizations)
  - AI-powered reply suggestions
- **Smart Caching**: Redis-based caching for fast responses
- **Database Storage**: PostgreSQL with full email history and AI insights
- **RESTful API**: Comprehensive endpoints for email management
- **Docker Deployment**: Fully containerized with docker-compose

### 🚧 Coming Soon (Phase 5-7)

- Calendar integration for automatic meeting scheduling
- Telegram bot for instant notifications
- Streamlit dashboard for visualization
- Background task processing with Celery
- Email search with semantic understanding

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Gmail account
- Groq API key (free tier)

### Setup

1. **Clone repository**
```bash
   git clone https://github.com/YOUR-USERNAME/ai-email-assistant.git
   cd ai-email-assistant
```

2. **Get API Keys**
   - Gmail OAuth: https://console.cloud.google.com/
   - Groq API: https://console.groq.com/ (free)

3. **Configure environment**
```bash
   cp .env.example .env
   # Edit .env with your credentials
```

4. **Start application**
```bash
   docker compose up -d
```

5. **Authenticate & Sync**
   - Visit: http://localhost:8000/auth/login
   - Complete OAuth flow
   - Sync emails: `curl -X POST http://localhost:8000/emails/sync`

## API Endpoints

### Authentication
- `GET /auth/login` - Initiate Gmail OAuth
- `GET /auth/callback` - OAuth callback handler

### Email Management
- `POST /emails/sync` - Fetch and process emails with AI
- `GET /emails/list` - List all emails with filtering
- `GET /emails/{id}` - Get specific email details
- `GET /emails/statistics` - Get email analytics
- `PATCH /emails/{id}/read` - Mark email as read

### AI Processing
- `POST /ai/summarize` - Quick email summarization
- `POST /ai/process-email` - Full AI analysis
- `GET /emails/filter/high-priority` - High priority emails
- `GET /emails/filter/meetings` - Meeting emails
- `GET /emails/filter/urgent` - Urgent emails

### System
- `GET /health` - Health check
- `GET /cache/stats` - Redis cache statistics
- `DELETE /cache/clear` - Clear cache

## Testing
```bash
# Health check
curl http://localhost:8000/health

# Sync emails
curl -X POST "http://localhost:8000/emails/sync?max_results=10"

# View statistics
curl http://localhost:8000/emails/statistics

# Run tests
docker compose exec backend python test_complete.py
```

##  Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **AI Framework**: LangChain
- **LLM**: Groq (Llama 3)
- **Containers**: Docker & Docker Compose
- **ORM**: SQLAlchemy
- **Migrations**: Alembic

## Development Progress

- Phase 1: Foundation & Git Setup
- Phase 2: Backend Core (FastAPI + PostgreSQL)
- Phase 3: Docker & Containerization
- Phase 4: AI Processing Pipeline (LangChain)
- Phase 5: Notifications & Calendar
- Phase 6: Frontend Dashboard (Streamlit)
- Phase 7: Production Deployment

## Environment Variables
```env
DATABASE_URL=postgresql://username:password@postgres:5432/email_assistant
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GROQ_API_KEY=your-groq-api-key
```
