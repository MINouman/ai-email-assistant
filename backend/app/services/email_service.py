from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Email, User
from app.services.ai.email_processor import email_processor
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def save_email_with_ai_analysis(db: Session, user_id: int, email_data: Dict) -> Email:
    existing = db.query(Email).filter(
        Email.message_id == email_data.get("message_id")
    ).first()

    if existing:
        logger.info(f"Email {email_data.get('message_id')} already exists")
        return existing
    
    ai_results = email_processor.process_email(email_data)
    
    email = Email(
        user_id=user_id,
        message_id=email_data.get("message_id"),
        thread_id=email_data.get("thread_id"),
        subject=email_data.get("subject"),
        sender=email_data.get("sender"),
        body_text=email_data.get("body"),

        summary=ai_results.get("summary"),
        intent=ai_results.get("intent"),
        priority=ai_results.get("priority"),
        entities=ai_results.get("entities"),
        reply_suggestions=ai_results.get("reply_suggestions"),
        is_processed=True,
        processed_at=datetime.utcnow(),

        is_important = (ai_results.get("priority") == "high"),
        received_at=datetime.utcnow()
    )

    db.add(email)
    db.commit()
    db.refresh(email)

    logger.info(f"save email {email.message_id} with AI analysis")
    return email

def fetch_and_save_emails(db: Session, user: User, max_results: int = 10) -> List[Email]:
    from app.services.gmail_service import fetch_emails

    if not user.google_access_token:
        raise ValueError("User not authenticated with Gmail")
    
    gmail_emails = fetch_emails(user.google_access_token, max_results)

    saved_emails = []

    for email_data in gmail_emails:
        try:
            email = save_email_with_ai_analysis(db, user.id, email_data)
            saved_emails.append(email)

        except Exception as e:
            logger.error(f"Error saving email: {e}")
            continue
    return saved_emails

def get_user_emails(
        db: Session, 
        user_id: int,
        # skip: int = 0,
        limit: int = 20,
        priority: str = None, 
        intent: str = None
) -> List[Email]:
    query = db.query(Email).filter(Email.user_id == user_id)
    if priority:
        query = query.filter(Email.priority == priority)
    
    if intent:
        query = query.filter(Email.intent == intent)
    return query.order_by(Email.received_at.desc()).limit(limit).all()

def get_email_statistics(db: Session, user_id: int) -> Dict:
    total = db.query(Email).filter(Email.user_id == user_id).count()
    
    processed = db.query(Email).filter(
        Email.user_id == user_id,
        Email.is_processed == True
    ).count()
    
    high_priority = db.query(Email).filter(
        Email.user_id == user_id,
        Email.priority == "high"
    ).count()

    unread = db.query(Email).filter(
        Email.user_id == user_id,
        Email.is_read == False
    ).count()

    intents = db.query(Email.intent, func.count(Email.id)).filter(
        Email.user_id == user_id
    ).group_by(Email.intent).all()

    return {
        "total": total,
        "processed": processed, 
        "high_priority": high_priority,
        "unread": unread,
        "intents": {intent: count for intent, count in intents if intent}
    }