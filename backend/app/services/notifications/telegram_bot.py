from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from app.config import settings
from app.database import SessionLocal
from app.models.models import User, Email
from app.services.email_service import get_email_statistics, get_user_emails
from sqlalchemy import desc
import logging

logger = logging.getLogger(__name__)


class TelegramBotHandler:
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.enabled = settings.TELEGRAM_ENABLED and self.bot_token
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 <b>Welcome to AI Email Assistant!</b>

Available commands:

📊 <b>General</b>
/start - Show this help message
/status - Show email statistics
/summary - Get summary of recent emails

📧 <b>Email Filtering</b>
/urgent - List urgent emails
/high - List high priority emails
/meeting - List meeting invitations
/unread - List unread emails
/recent - Last 5 emails

📅 <b>Calendar</b>
/today - Today's meetings
/tomorrow - Tomorrow's meetings

⚙️ <b>Actions</b>
/sync - Sync new emails from Gmail
/clear - Clear notification cache

Type any command to get started!
        """
        await update.message.reply_text(welcome_message, parse_mode="HTML")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        db = SessionLocal()
        try:
            user = db.query(User).first()
            if not user:
                await update.message.reply_text("❌ No user authenticated")
                return
            
            stats = get_email_statistics(db, user.id)
            
            message = f"""
📊 <b>Email Statistics</b>

📧 <b>Total Emails:</b> {stats['total']}
✅ <b>Processed:</b> {stats['processed']}
🔴 <b>High Priority:</b> {stats['high_priority']}
👁️ <b>Unread:</b> {stats['unread']}

<b>By Type:</b>
"""
            for intent, count in stats['by_intent'].items():
                emoji = {
                    'meeting': '📅',
                    'urgent': '⚡',
                    'task': '✅',
                    'follow_up': '🔄',
                    'information': 'ℹ️',
                    'social': '💬'
                }.get(intent, '📧')
                message += f"{emoji} {intent.replace('_', ' ').title()}: {count}\n"
            
            await update.message.reply_text(message, parse_mode="HTML")
        finally:
            db.close()
    
    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = SessionLocal()
        try:
            user = db.query(User).first()
            if not user:
                await update.message.reply_text("❌ No user authenticated")
                return
            
            emails = get_user_emails(db, user.id, limit=5)
            
            if not emails:
                await update.message.reply_text("📭 No emails found")
                return
            
            message = "📬 <b>Recent Email Summaries</b>\n\n"
            
            for i, email in enumerate(emails, 1):
                priority_emoji = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(email.priority, '⚪')
                
                message += f"{i}. {priority_emoji} <b>{email.subject[:50]}</b>\n"
                message += f"   From: {email.sender}\n"
                message += f"   {email.summary[:150]}...\n\n"
            
            await update.message.reply_text(message, parse_mode="HTML")
        finally:
            db.close()
    
    async def urgent_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = SessionLocal()
        try:
            user = db.query(User).first()
            if not user:
                await update.message.reply_text("❌ No user authenticated")
                return
            
            emails = get_user_emails(db, user.id, intent="urgent", limit=10)
            
            if not emails:
                await update.message.reply_text("✅ No urgent emails!")
                return
            
            message = f"⚡ <b>Urgent Emails ({len(emails)})</b>\n\n"
            
            for i, email in enumerate(emails, 1):
                message += f"{i}. <b>{email.subject[:50]}</b>\n"
                message += f"   From: {email.sender}\n"
                message += f"   📝 {email.summary[:120]}...\n\n"
            
            await update.message.reply_text(message, parse_mode="HTML")
        finally:
            db.close()
    
    async def high_priority_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = SessionLocal()
        try:
            user = db.query(User).first()
            if not user:
                await update.message.reply_text("❌ No user authenticated")
                return
            
            emails = get_user_emails(db, user.id, priority="high", limit=10)
            
            if not emails:
                await update.message.reply_text("✅ No high priority emails!")
                return
            
            message = f"🔴 <b>High Priority Emails ({len(emails)})</b>\n\n"
            
            for i, email in enumerate(emails, 1):
                message += f"{i}. <b>{email.subject[:50]}</b>\n"
                message += f"   From: {email.sender}\n"
                message += f"   Type: {email.intent}\n"
                message += f"   📝 {email.summary[:100]}...\n\n"
            
            await update.message.reply_text(message, parse_mode="HTML")
        finally:
            db.close()
    
    async def meeting_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = SessionLocal()
        try:
            user = db.query(User).first()
            if not user:
                await update.message.reply_text("❌ No user authenticated")
                return
            
            emails = get_user_emails(db, user.id, intent="meeting", limit=10)
            
            if not emails:
                await update.message.reply_text("📅 No meeting invitations found")
                return
            
            message = f"📅 <b>Meeting Invitations ({len(emails)})</b>\n\n"
            
            for i, email in enumerate(emails, 1):
                message += f"{i}. <b>{email.subject}</b>\n"
                message += f"   From: {email.sender}\n"
                
                if email.entities and isinstance(email.entities, dict):
                    dates = email.entities.get('dates', [])
                    if dates:
                        message += f"   🕐 {', '.join(dates)}\n"
                    
                    location = email.entities.get('locations', [])
                    if location:
                        message += f"   📍 {location[0]}\n"
                
                message += f"   📝 {email.summary[:100]}...\n\n"
            
            await update.message.reply_text(message, parse_mode="HTML")
        finally:
            db.close()
    
    async def unread_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = SessionLocal()
        try:
            user = db.query(User).first()
            if not user:
                await update.message.reply_text("❌ No user authenticated")
                return
            
            emails = db.query(Email).filter(
                Email.user_id == user.id,
                Email.is_read == False
            ).order_by(desc(Email.received_at)).limit(10).all()
            
            if not emails:
                await update.message.reply_text("✅ All emails read!")
                return
            
            message = f"👁️ <b>Unread Emails ({len(emails)})</b>\n\n"
            
            for i, email in enumerate(emails, 1):
                priority_emoji = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(email.priority, '⚪')
                
                message += f"{i}. {priority_emoji} <b>{email.subject[:50]}</b>\n"
                message += f"   From: {email.sender}\n"
                message += f"   📝 {email.summary[:100] if email.summary else 'No summary'}...\n\n"
            
            await update.message.reply_text(message, parse_mode="HTML")
        finally:
            db.close()
    
    async def recent_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = SessionLocal()
        try:
            user = db.query(User).first()
            if not user:
                await update.message.reply_text("❌ No user authenticated")
                return
            
            emails = get_user_emails(db, user.id, limit=5)
            
            if not emails:
                await update.message.reply_text("📭 No emails found")
                return
            
            message = "📨 <b>Last 5 Emails</b>\n\n"
            
            for i, email in enumerate(emails, 1):
                priority_emoji = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(email.priority, '⚪')
                
                intent_emoji = {
                    'meeting': '📅',
                    'urgent': '⚡',
                    'task': '✅',
                    'follow_up': '🔄',
                    'information': 'ℹ️',
                    'social': '💬'
                }.get(email.intent, '📧')
                
                message += f"{i}. {priority_emoji} {intent_emoji} <b>{email.subject}</b>\n"
                message += f"   From: {email.sender}\n"
                message += f"   {email.summary[:120] if email.summary else 'No summary'}...\n\n"
            
            await update.message.reply_text(message, parse_mode="HTML")
        finally:
            db.close()
    
    async def sync_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sync command"""
        await update.message.reply_text("🔄 Syncing emails from Gmail...")
        
        db = SessionLocal()
        try:
            from app.services.email_service import fetch_and_save_emails
            
            user = db.query(User).first()
            if not user or not user.google_access_token:
                await update.message.reply_text("❌ User not authenticated with Gmail")
                return
            
            emails = fetch_and_save_emails(db, user, max_results=10)
            
            message = f"✅ Synced {len(emails)} new emails!"
            await update.message.reply_text(message)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Sync failed: {str(e)}")
        finally:
            db.close()
    
    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = SessionLocal()
        try:
            from app.services.calendar_service import calendar_service
            
            user = db.query(User).first()
            if not user or not user.google_access_token:
                await update.message.reply_text("❌ User not authenticated")
                return
            
            if not calendar_service.initialize_service(user.google_access_token, user.google_refresh_token):
                await update.message.reply_text("❌ Failed to connect to calendar")
                return
            
            events = calendar_service.list_upcoming_events(max_results=10)
            
            from datetime import datetime, date
            today = date.today()
            today_events = []
            
            for event in events:
                if event.get('start'):
                    event_date = datetime.fromisoformat(event['start'].replace('Z', '+00:00')).date()
                    if event_date == today:
                        today_events.append(event)
            
            if not today_events:
                await update.message.reply_text("📅 No meetings scheduled for today")
                return
            
            message = f"📅 <b>Today's Meetings ({len(today_events)})</b>\n\n"
            
            for i, event in enumerate(today_events, 1):
                time = datetime.fromisoformat(event['start'].replace('Z', '+00:00')).strftime('%I:%M %p')
                message += f"{i}. <b>{event.get('summary', 'No title')}</b>\n"
                message += f"   🕐 {time}\n"
                message += f"   🔗 <a href='{event.get('link')}'>Open</a>\n\n"
            
            await update.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            db.close()
    
    async def tomorrow_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = SessionLocal()
        try:
            from app.services.calendar_service import calendar_service
            
            user = db.query(User).first()
            if not user or not user.google_access_token:
                await update.message.reply_text("❌ User not authenticated")
                return
            
            if not calendar_service.initialize_service(user.google_access_token, user.google_refresh_token):
                await update.message.reply_text("❌ Failed to connect to calendar")
                return
            
            events = calendar_service.list_upcoming_events(max_results=10)
            
            from datetime import datetime, date, timedelta
            tomorrow = date.today() + timedelta(days=1)
            tomorrow_events = []
            
            for event in events:
                if event.get('start'):
                    event_date = datetime.fromisoformat(event['start'].replace('Z', '+00:00')).date()
                    if event_date == tomorrow:
                        tomorrow_events.append(event)
            
            if not tomorrow_events:
                await update.message.reply_text("📅 No meetings scheduled for tomorrow")
                return
            
            message = f"📅 <b>Tomorrow's Meetings ({len(tomorrow_events)})</b>\n\n"
            
            for i, event in enumerate(tomorrow_events, 1):
                time = datetime.fromisoformat(event['start'].replace('Z', '+00:00')).strftime('%I:%M %p')
                message += f"{i}. <b>{event.get('summary', 'No title')}</b>\n"
                message += f"   🕐 {time}\n"
                message += f"   🔗 <a href='{event.get('link')}'>Open</a>\n\n"
            
            await update.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)
        
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")
        finally:
            db.close()
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            from app.redis_client import redis_client
            redis_client.flush_all()
            await update.message.reply_text("Notification cache cleared!")
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")
    
    def start_bot(self):
        if not self.enabled:
            logger.warning("Telegram bot disabled")
            return
        
        try:
            self.application = Application.builder().token(self.bot_token).build()
            
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("summary", self.summary_command))
            self.application.add_handler(CommandHandler("urgent", self.urgent_command))
            self.application.add_handler(CommandHandler("high", self.high_priority_command))
            self.application.add_handler(CommandHandler("meeting", self.meeting_command))
            self.application.add_handler(CommandHandler("unread", self.unread_command))
            self.application.add_handler(CommandHandler("recent", self.recent_command))
            self.application.add_handler(CommandHandler("sync", self.sync_command))
            self.application.add_handler(CommandHandler("today", self.today_command))
            self.application.add_handler(CommandHandler("tomorrow", self.tomorrow_command))
            self.application.add_handler(CommandHandler("clear", self.clear_command))
            
            logger.info("Telegram bot handlers registered")
            
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")


telegram_bot_handler = TelegramBotHandler()