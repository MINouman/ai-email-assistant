from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dateutil import parser
import pytz
from typing import Optional, Dict, List
import logging
import re

logger = logging.getLogger(__name__)


class CalendarService:
    
    def __init__(self):
        self.service = None
    
    def initialize_service(self, access_token: str, refresh_token: str = None):
        try:
            from app.config import settings
            
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET
            )
            
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("Calendar service initialized")
            return True
        except Exception as e:
            logger.error(f"Calendar initialization failed: {e}")
        return False
    
    def extract_meeting_info(self, email_body: str, entities: dict) -> Optional[Dict]:
        if not entities:
            return None
        
        dates = entities.get("dates", [])
        people = entities.get("people", [])
        locations = entities.get("locations", [])
        
        if not dates:
            time_patterns = [
                r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))',
                r'(\d{1,2}\s*(?:AM|PM|am|pm))',
                r'(tomorrow|today|next \w+)',
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, email_body, re.IGNORECASE)
                if match:
                    dates.append(match.group(1))
        
        if not dates:
            return None
        
        return {
            "dates": dates,
            "attendees": people,
            "location": locations[0] if locations else None,
            "has_meeting": True
        }
    
    def parse_date_string(self, date_str: str) -> Optional[datetime]:
        try:
            dt = parser.parse(date_str, fuzzy=True)
            
            if dt.hour == 0 and dt.minute == 0:
                dt = dt.replace(hour=9, minute=0)
            
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)
            
            return dt
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {e}")
            return None
    
    def create_event(
        self,
        summary: str,
        description: str,
        start_time: datetime,
        duration_minutes: int = 60,
        attendees: List[str] = None,
        location: str = None
    ) -> Optional[Dict]:

        if not self.service:
            logger.error("Calendar service not initialized")
            return None
        
        try:
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            if location:
                event['location'] = location
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendNotifications=True
            ).execute()
            
            logger.info(f"Calendar event created: {created_event.get('id')}")
            
            return {
                "event_id": created_event.get("id"),
                "event_link": created_event.get("htmlLink"),
                "status": "created"
            }
        
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return None
    
    def create_event_from_email(
        self,
        email_data: dict,
        meeting_info: dict
    ) -> Optional[Dict]:        
        subject = email_data.get("subject", "Meeting")
        sender = email_data.get("sender", "")
        body = email_data.get("body", "")[:500] 
        
        dates = meeting_info.get("dates", [])
        if not dates:
            return None
        
        start_time = self.parse_date_string(dates[0])
        if not start_time:
            return None
        
        now = datetime.now(pytz.UTC)
        if start_time < now:
            days_to_add = 1
            start_time = start_time + timedelta(days=days_to_add)
        
        attendees = meeting_info.get("attendees", [])
        location = meeting_info.get("location")
        
        return self.create_event(
            summary=subject,
            description=f"From: {sender}\n\n{body}",
            start_time=start_time,
            duration_minutes=60,
            attendees=attendees,
            location=location
        )
    
    def list_upcoming_events(self, max_results: int = 10) -> List[Dict]:
        if not self.service:
            logger.error("Calendar service not initialized")
            return []
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return [
                {
                    "id": event.get("id"),
                    "summary": event.get("summary"),
                    "start": event.get("start", {}).get("dateTime"),
                    "end": event.get("end", {}).get("dateTime"),
                    "link": event.get("htmlLink")
                }
                for event in events
            ]
        
        except Exception as e:
            logger.error(f"Error listing events: {e}")
            return []

calendar_service = CalendarService()