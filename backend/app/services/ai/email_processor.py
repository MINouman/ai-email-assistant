from app.services.ai.llm_service import llm_service
from app.redis_client import redis_client
from app.services.notifications.telegram_service import telegram_service
from app.services.calendar_service import calendar_service
from app.config import settings
from typing import Dict, Optional
import hashlib
import logging

logger = logging.getLogger(__name__)

class EmailProcessor:
    def __init__(self):
        self.llm = llm_service
        self.cache = redis_client
        self.telegram = telegram_service
        self.calendar = calendar_service

    def _generate_cache_key(self, email_id: str, operation: str) -> str:
        return f"email: {email_id}:{operation}"
    
    def process_email(self, email_data: Dict, send_notification: bool = True, user_access_token: str = None) -> Dict:
        message_id = email_data.get("message_id", "")
        subject = email_data.get("subject", "")
        body = email_data.get("body", "")

        cache_key = self._generate_cache_key(message_id, "full_analysis")
        cached = self.cache.get(cache_key)

        if cached:
            logger.info("Cache hit for email {message_id}")
            return cached
        
        logger.info(f"Processing email {message_id}")
        summary = self.llm.summarize_email(body, subject)
        intent_data = self.llm.detect_intent(body, subject)
        entities = self.llm.extract_entities(body)
        replies = self.llm.generate_reply_suggestions(body, subject)

        meeting_info = None
        calendar_event = None

        if intent_data.get("intent") == "meeting":
            meeting_info = self.calendar.extract_meeting_info(body, entities)
            
            if meeting_info and settings.GOOGLE_CALENDAR_ENABLED and user_access_token:
                if self.calendar.initialize_service(user_access_token):
                    calendar_event = self.calendar.create_event_from_email(
                        email_data,
                        meeting_info
                    )

                    if calendar_event:
                        logger.info(f"Calendar event created for email {message_id}")

                        if send_notification:
                            self.telegram.notify_meeting_detected(email_data, meeting_info)
        result = {
            "message_id": message_id,
            "summary": summary or "unable to generate summary",
            "intent": intent_data.get("intent", "information"),
            "priority": intent_data.get("priority", "medium"),
            "reasoning": intent_data.get("reasoning", ""),
            "entities": entities or {}, 
            "reply_suggestions": replies or [],
            "meeting_info": meeting_info,
            "calendar_event": calendar_event,
            "processed": True 
        }

        if send_notification and settings.TELEGRAM_ENABLED:
            if result["priority"] == "high":
                self.telegram.notify_new_email(result)
            else:
                self.telegram.notify_new_email(result)

        self.cache.set(cache_key, result, ttl=3600)

        return result
    
    def get_summary_only(self, email_data: Dict) -> str:
        message_id = email_data.get("message_id", "")
        cache_key = self._generate_cache_key(message_id, "summary")

        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        summary = self.llm.summarize_email(
            email_data.get("body", ""),
            email_data.get("subject", "")
        )

        if summary:
            self.cache.set(cache_key, summary, ttl=3600)
        
        return summary or "Unable to generate summary"
    
    def batch_process_emails(self, emails: list, send_notifications: bool = True, user_access_token: str = None) -> list:
        results = []

        for email in emails:
            try:
                result = self.process_email(
                    email,
                    send_notification=send_notifications,
                    user_access_token=user_access_token
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing email {email.get('message_id')}: {e}")
                results.append({
                    "message_id": email.get("message_id"),
                    "error": str(e),
                    "processed": False
                })
            return results
        
email_processor = EmailProcessor()