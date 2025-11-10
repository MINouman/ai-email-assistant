from app.services.ai.llm_service import llm_service
from app.redis_client import redis_client
from typing import Dict, Optional
import hashlib
import logging

logger = logging.getLogger(__name__)

class EmailProcessor:
    def __init__(self):
        self.llm = llm_service
        self.cache = redis_client

    def _generate_cache_key(self, email_id: str, operation: str) -> str:
        return f"email: {email_id}:{operation}"
    
    def process_email(self, email_data: Dict) -> Dict:
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

        result = {
            "message_id": message_id,
            "summary": summary or "unable to generate summary",
            "intent": intent_data.get("intent", "information"),
            "priority": intent_data.get("priority", "medium"),
            "reasoning": intent_data.get("reasoning", ""),
            "entities": entities or {}, 
            "reply_suggestions": replies or [],
            "processed": True 
        }

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
    
    def batch_process_emails(self, emails: list) -> list:
        results = []
        for email in emails:
            try: 
                result = self.process_email(email)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing email {email.get('message_id')}: {e}")
                results.append ({
                    "message_id": email.get("message_id"),
                    "error": str(e),
                    "processed": False
                })
            return results
        
email_processor = EmailProcessor()