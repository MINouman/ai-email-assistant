from telegram import Bot
from telegram.error import TelegramError
from app.config import settings
import logging
from typing import Optional
import asyncio
import httpx

logger = logging.getLogger(__name__)


class TelegramService:
    """Telegram notification service"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.enabled = settings.TELEGRAM_ENABLED and self.bot_token
    
    def _get_bot(self):
        """Create new bot instance for each request"""
        if not self.enabled:
            return None
        return Bot(token=self.bot_token)
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send message using httpx (avoids connection pool issues)"""
        if not self.enabled:
            logger.warning("Telegram notifications disabled")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            response = httpx.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Telegram message sent")
                return True
            else:
                logger.error(f"Telegram error: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def notify_new_email(self, email_data: dict) -> bool:
        subject = email_data.get("subject", "No Subject")
        sender = email_data.get("sender", "Unknown")
        summary = email_data.get("summary", "")
        priority = email_data.get("priority", "medium")
        intent = email_data.get("intent", "information")
        
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
        intent_emoji = {
            "meeting": "📅", "urgent": "⚡", "task": "✅",
            "follow_up": "🔄", "information": "ℹ️", "social": "💬"
        }.get(intent, "📧")
        
        message = f"""
{priority_emoji} <b>New Email</b> {intent_emoji}

<b>From:</b> {sender}
<b>Subject:</b> {subject}
<b>Priority:</b> {priority.upper()}
<b>Type:</b> {intent.replace('_', ' ').title()}

<b>Summary:</b>
{summary[:300]}{"..." if len(summary) > 300 else ""}
        """
        
        return self.send_message(message.strip())
    
    def notify_high_priority(self, email_data: dict) -> bool:
        subject = email_data.get("subject", "No Subject")
        sender = email_data.get("sender", "Unknown")
        summary = email_data.get("summary", "")
        
        message = f"""
🚨 <b>HIGH PRIORITY EMAIL</b> 🚨

<b>From:</b> {sender}
<b>Subject:</b> {subject}

<b>Summary:</b>
{summary[:250]}

⚠️ <i>Requires immediate attention</i>
        """
        
        return self.send_message(message.strip())
    
    def notify_meeting_detected(self, email_data: dict, meeting_info: dict) -> bool:
        subject = email_data.get("subject", "No Subject")
        sender = email_data.get("sender", "Unknown")
        dates = meeting_info.get("dates", [])
        date_str = ", ".join(dates) if dates else "Not specified"
        
        message = f"""
📅 <b>MEETING INVITATION DETECTED</b>

<b>From:</b> {sender}
<b>Subject:</b> {subject}
<b>Date/Time:</b> {date_str}

<i>Check your calendar for details</i>
        """
        
        return self.send_message(message.strip())
    
    def notify_daily_summary(self, stats: dict) -> bool:
        total = stats.get("total", 0)
        unread = stats.get("unread", 0)
        high_priority = stats.get("high_priority", 0)
        by_intent = stats.get("by_intent", {})
        
        intents_str = "\n".join([
            f"  • {intent.replace('_', ' ').title()}: {count}"
            for intent, count in by_intent.items()
        ])
        
        message = f"""
📊 <b>Daily Email Summary</b>

<b>Total Emails:</b> {total}
<b>Unread:</b> {unread}
<b>High Priority:</b> {high_priority}

<b>By Type:</b>
{intents_str if intents_str else "  No data"}

Have a productive day! 🚀
        """
        
        return self.send_message(message.strip())
    
    def test_connection(self) -> dict:
        if not self.enabled:
            return {"status": "disabled", "message": "Telegram notifications disabled"}
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = httpx.get(url, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()["result"]
                
                test_msg = "🤖 <b>Test Message</b>\n\nTelegram bot is working correctly!"
                self.send_message(test_msg)
                
                return {
                    "status": "success",
                    "bot_username": bot_info["username"],
                    "bot_name": bot_info["first_name"],
                    "chat_id": self.chat_id
                }
            else:
                return {"status": "error", "message": response.text}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}


telegram_service = TelegramService()