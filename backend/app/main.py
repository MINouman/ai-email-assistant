from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db, engine, Base
from app.models.models import User

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

