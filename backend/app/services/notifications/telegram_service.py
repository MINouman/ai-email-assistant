from telegram import Bot
from telegram.error import TelegramError
from app.config import settings
import logging
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)

class TelegramService:

    def __init__(self):
        self.bot = None
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.enabled = settings.TELEGRAM_ENABLED

        if self.enabled and settings.TELEGRAM_BOT_TOKEN:
            try:
                self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                logger.info("Telegram bot initialized")
            except Exception as e:
                logger.error(f"Telegram bot initialization failed; {e}")
                self.enabled = False
            
    
    async def send_message_async(self, text: str, parse_mode: str = "HTML") -> bool:
        if not self.enabled or not self.bot:
            logger.warning("Telegram notifications disables")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode
            )
            logger.info(f"Telegram message sent")
            return True
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.send_message_async(text, parse_mode))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def notify_new_email(self, email_data: dict) -> bool:
        subject = email_data.get("subject", "No Subject")
        sender = email_data.get("sender", "Unknown")
        summary = email_data.get("summary", "")
        priority = email_data.get("priority", "medium")
        intent = email_data.get("intent", "information")
        
        priority_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(priority, "⚪")
        
        intent_emoji = {
            "meeting": "📅",
            "urgent": "⚡",
            "task": "✅",
            "follow_up": "🔄",
            "information": "ℹ️",
            "social": "💬"
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
        """Send urgent notification for high priority email"""
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
        """Send notification for detected meeting"""
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
        """Send daily email summary"""
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
        if not self.enabled or not self.bot:
            return {
                "status": "disabled",
                "message": "Telegram notifications are disabled"
            }
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            me = loop.run_until_complete(self.bot.get_me())
            
            test_msg = "🤖 <b>Test Message</b>\n\nTelegram bot is working correctly!"
            loop.run_until_complete(self.send_message_async(test_msg))
            
            loop.close()
            
            return {
                "status": "success",
                "bot_username": me.username,
                "bot_name": me.first_name,
                "chat_id": self.chat_id
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


telegram_service = TelegramService()