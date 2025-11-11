import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"


def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def test_telegram_connection():
    print_header("TEST 1: Telegram Bot Connection")
    
    response = requests.get(f"{BASE_URL}/notifications/test")
    data = response.json()
    
    print(json.dumps(data, indent=2))
    
    if data.get("status") == "success":
        print("\nTelegram bot is connected!")
        print(f"   Bot: @{data.get('bot_username')}")
        print("   Check your Telegram for test message!")
    else:
        print(f"\nTelegram connection failed: {data.get('message')}")
    
    time.sleep(2)


def test_custom_notification():
    print_header("TEST 2: Custom Notification")
    
    message = "This is a test notification from the API!"
    
    response = requests.post(
        f"{BASE_URL}/notifications/send",
        params={"message": message}
    )
    
    print(json.dumps(response.json(), indent=2))
    print("\nCheck Telegram for custom message!")
    
    time.sleep(2)


def test_daily_summary():
    print_header("TEST 3: Daily Summary Notification")
    
    response = requests.get(f"{BASE_URL}/notifications/daily-summary")
    print(json.dumps(response.json(), indent=2))
    
    print("\nCheck Telegram for daily summary!")
    
    time.sleep(2)


def test_email_sync_with_notifications():
    print_header("TEST 4: Email Sync with Notifications")
    
    print("Syncing emails... (this will send notifications)")
    
    response = requests.post(f"{BASE_URL}/emails/sync?max_results=2")
    data = response.json()
    
    print(json.dumps(data, indent=2))
    print(f"\nSynced {data.get('count')} emails")
    print("   Check Telegram for email notifications!")
    
    time.sleep(3)


def test_calendar_list():
    print_header("TEST 5: List Calendar Events")
    
    try:
        response = requests.get(f"{BASE_URL}/calendar/events?max_results=5")
        data = response.json()
        
        print(f"Upcoming events: {data.get('count')}")
        
        for event in data.get('events', []):
            print(f"\n{event.get('summary')}")
            print(f"   Start: {event.get('start')}")
            print(f"   Link: {event.get('link')}")
    
    except Exception as e:
        print(f"Error: {e}")


def test_calendar_create():
    print_header("TEST 6: Create Calendar Event")
    
    # Create event for tomorrow at 10 AM
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    data = {
        "summary": "API Test Meeting",
        "description": "This event was created by the AI Email Assistant API test",
        "start_time": start_time.isoformat(),
        "duration_minutes": 30
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/calendar/create-event",
            json=data
        )
        result = response.json()
        
        print(json.dumps(result, indent=2))
        print("\nEvent created! Check your Google Calendar!")
    
    except Exception as e:
        print(f"Error: {e}")


def test_email_with_meeting():
    print_header("TEST 7: Process Email with Meeting Detection")
    
    # Simulate email with meeting
    email_data = {
        "message_id": "test_meeting_123",
        "subject": "Project Review Meeting",
        "body": """
        Hi team,
        
        Let's schedule our project review meeting for tomorrow at 2:00 PM.
        We'll discuss the Q4 roadmap and address any blockers.
        
        Location: Conference Room A
        Duration: 1 hour
        
        Please confirm your attendance.
        
        Best,
        Manager
        """,
        "sender": "manager@company.com"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/process-email",
            params=email_data
        )
        result = response.json()
        
        print(f"Intent: {result['data']['intent']}")
        print(f"Priority: {result['data']['priority']}")
        print(f"\nSummary: {result['data']['summary']}")
        
        if result['data'].get('meeting_info'):
            print(f"\nMeeting detected!")
            print(f"   Dates: {result['data']['meeting_info'].get('dates')}")
        
        if result['data'].get('calendar_event'):
            print(f"\nCalendar event created!")
            print(f"   Event ID: {result['data']['calendar_event'].get('event_id')}")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\nNotification & Calendar Integration Test Suite")
    print("="*70)
    print("Make sure you have:")
    print("  1. Telegram bot configured in .env")
    print("  2. Google Calendar API enabled")
    print("  3. Completed Gmail OAuth")
    print("="*70)
    
    input("\nPress Enter to start tests...")
    
    try:
        test_telegram_connection()
        test_custom_notification()
        test_daily_summary()
        test_email_sync_with_notifications()
        test_calendar_list()
        test_calendar_create()
        test_email_with_meeting()
        
        print("\n" + "="*70)
        print("ALL TESTS COMPLETED!")
        print("="*70)
        print("\nCheck your:")
        print("  • Telegram for notifications")
        print("  • Google Calendar for events")
        print("="*70 + "\n")
    
    except Exception as e:
        print(f"\nTEST SUITE FAILED: {e}\n")