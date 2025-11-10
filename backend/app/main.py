from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db, engine, Base
from app.models.models import User
from datetime import datetime
from fastapi.responses import RedirectResponse
from app.services.gmail_auth import get_google_auth_url, exchange_code_for_token
from app.services.gmail_service import fetch_emails, get_user_profile
from sqlalchemy import text

from app.services.ai.email_processor import email_processor
from app.redis_client import redis_client

from app.services.email_service import (
    fetch_and_save_emails,
    get_user_emails, 
    get_email_statistics
)
from app.models.models import Email

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME, 
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {
        "message": "AI Email Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status":"unhealthy",
            "database":"disconnected",
            "error":str(e)
        }
    
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"total":len(users), "users": users}


@app.get("/auth/login")
def login():
    auth_url = get_google_auth_url()
    return {"auth_url": auth_url}

@app.get("/auth/callback")
def auth_callback(code: str, db: Session = Depends(get_db)):
    try:
        tokens = exchange_code_for_token(code)
        user = User(
            email="test@example.com",
            full_name="Test User",
            google_access_token=tokens["access_token"],
            google_refresh_token=tokens["refresh_token"],
            token_expiry=tokens["token_expiry"]
        )

        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            existing_user.google_access_token = tokens["access_token"]
            existing_user.google_refresh_token = tokens["refresh_token"]
            existing_user.token_expiry = tokens["token_expiry"]
        
        else: 
            db.add(user)
        
        db.commit()
        db.refresh(user)

        return {
            "status": "success",
            "message": "Authentication successful!",
            "user_email": user.email
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.get("/emails/fetch")
def fetch_user_emails(db: Session = Depends(get_db)):
    user = db.query(User).first()

    if not user or not user.google_access_token:
        raise HTTPException(status_code=401, detail = "User not Authenticated")
    
    try:
        emails = fetch_emails(user.google_access_token, max_results=5)
        return {
            "status": "success",
            "count": len(emails),
            "emails": emails
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail = str(e))
    

@app.get("/email/profile")
def get_gmail_profile(db: Session = Depends(get_db)):
    user = db.query(User).first()

    if not user or not user.google_access_token:
        raise HTTPException(status_code=401, detail= "User not authenticated")
    try:
        profile = get_user_profile(user.google_access_token)
        return profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/ai/process-email")
def process_email_ai(
    message_id: str,
    subject: str,
    body: str,
    sender: str
):
    try: 
        email_data = {
            "message_id": message_id,
            "subject": subject, 
            "body": body,
            "sender": sender
        }

        result = email_processor.process_email(email_data)

        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/ai/summarize")
def summarize_email(subject: str, body: str):
    try:
        email_data = {
            "message_id": "quick",
            "subject": subject, 
            "body": body
        }
        summary = email_processor.get_summary_only(email_data)

        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/emails/fetch-and-process")
def fetch_and_process_emails(db: Session = Depends(get_db)):
    user = db.query(User).first()

    if not user or not user.google_access_token:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    try: 
        emails = fetch_emails(user.google_access_token, max_results=5)
        processed = email_processor.batch_process_emails(emails)

        return {
            "status": "success",
            "count": len(processed),
            "emails": processed
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/cache/stats")
def cache_statistics():
    try:
        info = redis_client.redis.info()
        return {
            "status": "healthy",
            "connected": True,
            "used_memory_human": info.get("used_memory_human"),
            "total_keys": redis_client.redis.dbsize(),
            "connected_clients": info.get("connected_clients")
        }
    except Exception as e:
        return {
            "status": "error",
            "connected": False, 
            "error": str(e)
        }

@app.delete("/cache/clear")
def clear_cache():
    try:
        redis_client.flush_all()
        return {
            "status":"success",
            "message": "Cache Cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/emails/sync")
def sync_emails(max_results: int=10, db: Session = Depends(get_db)):
    user = db.query(User).first()

    if not user or not user.google_access_token:
        raise HTTPException(status_code=401, detail="User not Authorized")
    
    try:
        emails = fetch_and_save_emails(db, user, max_results)

        return {
            "status": "success",
            "message": f"Synced and processed {len(emails)} emails",
            "count": len(emails)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emails/list")
def list_emails(
    skip: int = 0,
    limit: int = 20, 
    priority: str = None,
    intent: str = None,
    db: Session = Depends(get_db)
):
    user = db.query(User).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    emails = get_user_emails(db, user.id, skip, limit, priority, intent)

    email_list = []
    for email in emails:
        email_list.append({
            "id": email.id,
            "message_id": email.message_id,
            "subject": email.subject,
            "sender": email.sender,
            "summary": email.summary,
            "intent": email.intent,
            "priority": email.priority,
            "entities": email.entities,
            "reply_suggestions": email.reply_suggestions,
            "is_read": email.is_read,
            "is_important": email.is_important,
            "received_at": email.received_at,
            "processed_at": email.processed_at
        })
    
    return {
        "status": "success",
        "count": len(email_list),
        "emails": email_list
    }

@app.get("/email/statistics")
def email_statistics(db: Session = Depends(get_db)):
    user = db.query(User).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    stats = get_email_statistics(db, user.id)

    return {
        "status": "success",
        "statistics": stats
    }

@app.get("/emails/{email_id}")
def get_email_details(email_id: int, db: Session = Depends(get_db)):
    user = db.query(User).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    email = db.query(Email).filter(
        Email.id == email_id, 
        Email.user_id == user.id
    ).first()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return {
        "status": "success",
        "email": {
            "id": email.id,
            "message_id": email.message_id,
            "thread_id": email.thread_id,
            "subject": email.subject,
            "sender": email.sender,
            "body": email.body_text,
            "summary": email.summary,
            "intent": email.intent,
            "priority": email.priority,
            "entities": email.entities,
            "reply_suggestions": email.reply_suggestions,
            "is_read": email.is_read,
            "is_important": email.is_important,
            "received_at": email.received_at,
            "processed_at": email.processed_at
        }
    }

@app.patch("email/{email_id}/read")
def mark_email_as_read(email_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter()

    if not user:
        raise HTTPException(status_code=404, detail="User Not authenticated")
    
    email = db.query(Email).filter(
        Email.id == email_id,
        Email.user_id == user.id
    ).first()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email.is_read = True
    db.commit()

    return{
        "status": "success",
        "message":"email marked as read"
    }

@app.get("/emails/filter/high-priority")
def get_high_priority_emails(db: Session = Depends(get_db)):
    return list_emails(priority="high", db=db)

@app.get("/emails/filter/meetings")
def get_meeting_emails(db: Session = Depends(get_db)):
    return list_emails(intent="meeting", db=db)

@app.get("/email/filter/urgent")
def get_urgent_emails(db: Session = Depends(get_db)):
    return list_emails(intent="urgent", db=db)
