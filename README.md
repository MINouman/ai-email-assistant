# AI Email Assistant

An intelligent email management system with AI-powered automation, notifications, and calendar integration.

## Architecture Overview

```mermaid
graph TB
    A[Gmail/Outlook Account] -->|OAuth2| B[FastAPI Backend]
    B -->|Fetch Emails| A
    B -->|Process| C[AI Pipeline]
    C -->|LangChain + Groq| D[LLM Processing]
    D -->|Summarize| E[Email Analysis]
    D -->|Extract| F[Entities & Intent]
    D -->|Classify| G[Priority Detection]
    
    E --> H[(PostgreSQL)]
    F --> H
    G --> H
    
    B -->|Cache| I[(Redis)]
    
    H -->|Trigger| J[Notification Service]
    J -->|Send| K[Telegram Bot]
    
    H -->|Detect Meetings| L[Calendar Service]
    L -->|Create Events| M[Google Calendar]
    
    B -->|Serve| N[REST API]
    N -->|Future| O[Streamlit Dashboard]
    
    P[Background Scheduler] -->|Daily 9AM| J
    P -->|Periodic| B
```

## System Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Cache as Redis
    participant AI as Groq LLM
    participant TG as Telegram
    participant CAL as Google Calendar
    
    U->>API: POST /emails/sync
    API->>Cache: Check last sync
    API->>U: Fetch via OAuth
    U-->>API: New emails
    
    loop For each email
        API->>Cache: Check if processed
        alt Not in cache
            API->>AI: Process email
            AI-->>API: Summary + Intent + Priority + NER
            API->>DB: Store results
            API->>Cache: Cache results
            
            alt High Priority
                API->>TG: Send urgent notification
            end
            
            alt Meeting detected
                API->>CAL: Create calendar event
                CAL-->>API: Event created
                API->>TG: Send meeting alert
            end
        end
    end
    
    API-->>U: Sync complete
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend Framework | FastAPI | REST API server |
| Database | PostgreSQL 15 | Persistent storage |
| Cache/Queue | Redis 7 | Caching & task queue |
| AI Framework | LangChain | LLM orchestration |
| LLM Provider | Groq (Llama 3) | Free AI processing |
| Auth | Google OAuth2 | Gmail access |
| Notifications | python-telegram-bot | Real-time alerts |
| Calendar | Google Calendar API | Event management |
| Scheduler | APScheduler | Background tasks |
| Containerization | Docker Compose | Deployment |

## Key Features

### Backend (Implemented)

**Email Processing**
- OAuth2 authentication for Gmail/Outlook
- Background email fetching with rate limiting
- Duplicate detection via Redis caching
- Metadata storage in PostgreSQL

**AI Pipeline**
- Email summarization using Groq Llama 3
- Intent classification (meeting, urgent, task, follow-up)
- Priority detection (high, medium, low)
- Named Entity Recognition (people, dates, locations)
- AI-powered reply suggestions

**Notifications**
- Telegram bot integration
- Priority-based alerting
- Daily email summaries (scheduled 9 AM)
- Meeting reminders
- Custom notification templates

**Calendar Integration**
- Automatic meeting detection in emails
- Natural language date/time parsing
- Google Calendar event creation
- Event reminders via Telegram

**API Endpoints**
- Email management (sync, list, filter, statistics)
- AI processing (summarize, analyze, classify)
- Notification controls
- Calendar operations
- System health and cache management

### Frontend (Upcoming)

**Streamlit Dashboard**
- Email inbox visualization
- Analytics and statistics
- Task timeline view
- High-priority email highlights
- AI chat interface
- Semantic search
- Notification preferences
- Calendar integration view

## Database Schema

```mermaid
erDiagram
    USERS ||--o{ EMAILS : has
    USERS {
        string id PK
        string email
        json credentials
        timestamp created_at
    }
    
    EMAILS ||--o{ AI_ANALYSIS : has
    EMAILS {
        string id PK
        string user_id FK
        string gmail_id
        string subject
        string sender
        text body
        timestamp date
        boolean is_read
        timestamp processed_at
    }
    
    AI_ANALYSIS {
        string id PK
        string email_id FK
        text summary
        string intent
        string priority
        json entities
        json reply_suggestions
        timestamp created_at
    }
    
    CALENDAR_EVENTS {
        string id PK
        string email_id FK
        string calendar_event_id
        string title
        timestamp start_time
        timestamp end_time
        json attendees
    }
```

## Quick Start

### Prerequisites
```bash
# Required
- Docker & Docker Compose
- Gmail account
- Groq API key (free tier)
- Telegram account
```

### Setup

1. Clone and configure
```bash
git clone <repository-url>
cd ai-email-assistant
cp .env.example .env
```

2. Get API credentials
- Gmail OAuth: https://console.cloud.google.com/
- Groq API: https://console.groq.com/
- Telegram: Message @BotFather on Telegram

3. Update .env with credentials

4. Deploy
```bash
docker compose up -d
```

5. Authenticate
```bash
# Start OAuth flow
curl http://localhost:8000/auth/login

# Test system
curl -X POST http://localhost:8000/emails/sync?max_results=5
```

## API Endpoints

### Authentication
- `GET /auth/login` - Initiate Gmail OAuth flow
- `GET /auth/callback` - OAuth callback handler

### Email Management
- `POST /emails/sync` - Fetch and process new emails
- `GET /emails/list` - List emails with filters
- `GET /emails/{id}` - Get email details
- `GET /emails/statistics` - Email analytics
- `PATCH /emails/{id}/read` - Mark as read
- `GET /emails/filter/{type}` - Filter by high-priority/urgent/meetings

### AI Processing
- `POST /ai/summarize` - Summarize email text
- `POST /ai/process-email` - Full AI analysis pipeline

### Notifications
- `GET /notifications/test` - Test Telegram connection
- `POST /notifications/send` - Send custom notification
- `GET /notifications/daily-summary` - Generate daily summary

### Calendar
- `GET /calendar/events` - List upcoming events
- `POST /calendar/create-event` - Create calendar event

### System
- `GET /health` - Health check
- `GET /cache/stats` - Redis statistics
- `DELETE /cache/clear` - Clear cache

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/email_assistant
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-here

# Google Services
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
GOOGLE_CALENDAR_ENABLED=True

# AI
GROQ_API_KEY=your-groq-api-key

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
TELEGRAM_ENABLED=True
```

## Project Structure

```
ai-email-assistant/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Config, auth
│   │   ├── models/        # Database models
│   │   ├── services/      # Business logic
│   │   │   ├── ai_service.py
│   │   │   ├── email_service.py
│   │   │   ├── notification_service.py
│   │   │   └── calendar_service.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## Testing

```bash
# Test notifications
docker compose exec backend python test_notifications.py

# Test AI processing
docker compose exec backend python test_ai.py

# Full integration test
docker compose exec backend python test_complete.py
```

## Development Roadmap

- Phase 1: Foundation & Git setup - COMPLETED
- Phase 2: Backend core (FastAPI + PostgreSQL) - COMPLETED
- Phase 3: Docker containerization - COMPLETED
- Phase 4: AI processing pipeline - COMPLETED
- Phase 5: Notifications & calendar integration - COMPLETED
- Phase 6: Streamlit dashboard - IN PROGRESS
- Phase 7: Production deployment - PLANNED

## License

MIT License