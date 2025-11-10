from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship 
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(Text)
    is_active = Column(Boolean, default= True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    google_access_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime(timezone=True), nullable=True)

    emails = relationship("Email", back_populates="user")


class Email(Base):
    __tablename__ = "email"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    #Email
    message_id = Column(String, unique=True, index=True)
    thread_id = Column(String, index=True)
    subject = Column(String)
    sender = Column(String)
    recipient = Column(String)
    body_text = Column(Text)
    received_at = Column(DateTime(timezone=True))

    #AI Processing
    summary = Column(Text, nullable=True)
    intent = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    entities = Column(JSON, nullable=True)
    reply_suggestions = Column(JSON, nullable=True)
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    #Metadata
    is_read = Column(Boolean, default=False)
    is_important = Column(Boolean, default=False)
    labels = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    #Foreign
    user = relationship("User", back_populates="emails")