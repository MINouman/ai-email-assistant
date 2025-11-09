from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db, engine, Base
from app.models.models import User
from datetime import datetime
from fastapi.responses import RedirectResponse
from app.services.gmail_auth import get_google_auth_url, exchange_code_for_token

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
        db.execute("SELECT 1")
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
        
        return {
            "status": "success",
            "message": "Authentication successful!",
            "user_email": user.email
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
