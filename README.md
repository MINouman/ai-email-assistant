 # AI Email Assistant

An intelligent email management system with AI-powered automation.

## Quick Start with Docker

### Prerequisites
- Docker & Docker Compose installed
- Gmail OAuth credentials

### Setup

1. **Clone the repository**
```bash
   git clone https://github.com/YOUR-USERNAME/ai-email-assistant.git
   cd ai-email-assistant
```

2. **Configure environment**
```bash
   cp .env.example .env
   # Edit .env and add your Google OAuth credentials
```

3. **Start the application**
```bash
   docker compose up -d
```

4. **Access the application**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Commands
```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f backend

# Stop services
docker compose down

# Rebuild after code changes
docker compose up -d --build

# Database management
docker compose exec backend python manage_db.py stats
```

## Development Status

Phase 1: Foundation & Git Setup - Complete  
Phase 2: Backend Core (FastAPI + PostgreSQL) - Complete  
Phase 3: Docker & Containerization - Complete  
Phase 4: AI Processing Pipeline - In Progress  

##  Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Cache:** Redis (coming soon)
- **AI:** Hugging Face / Groq
- **Frontend:** Streamlit (coming soon)
- **Deployment:** Docker

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /auth/login` - Initiate Gmail OAuth
- `GET /auth/callback` - OAuth callback
- `GET /emails/fetch` - Fetch recent emails
- `GET /emails/profile` - Get Gmail profile

## Environment Variables
```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/email_assistant
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
```

## Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Guide](https://www.postgresql.org/docs/)

## License

MIT License
