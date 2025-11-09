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
    