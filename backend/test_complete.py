import requests
import json
import time

BASE_URL = "http://localhost:8000"


def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def test_health():
    print_header("TEST 1: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 200


def test_cache():
    print_header("TEST 2: Cache Statistics")
    response = requests.get(f"{BASE_URL}/cache/stats")
    print(json.dumps(response.json(), indent=2))


def test_ai_summarization():
    print_header("TEST 3: AI Email Summarization")
    
    data = {
        "subject": "Project Update Meeting",
        "body": """
        Hi Team,
        
        I wanted to give you a quick update on the project status.
        We've completed 80% of the development work and are on track
        to meet our November 30th deadline.
        
        However, we need to schedule a meeting this week to discuss
        the final deployment strategy and address any remaining concerns.
        
        Please let me know your availability for Thursday or Friday.
        
        Best regards,
        Project Manager
        """
    }
    
    response = requests.post(f"{BASE_URL}/ai/summarize", json=data)
    print(json.dumps(response.json(), indent=2))


def test_sync_emails():
    print_header("TEST 4: Sync Emails from Gmail")
    
    response = requests.post(f"{BASE_URL}/emails/sync?max_results=3")
    print(json.dumps(response.json(), indent=2))
    
    time.sleep(2)


def test_statistics():
    print_header("TEST 5: Email Statistics")
    
    response = requests.get(f"{BASE_URL}/emails/statistics")
    print(json.dumps(response.json(), indent=2))


def test_list_emails():
    print_header("TEST 6: List All Emails")
    
    response = requests.get(f"{BASE_URL}/emails/list?limit=5")
    data = response.json()
    
    print(f"Total emails: {data['count']}")
    
    for email in data['emails'][:3]:
        print(f"\nEmail ID: {email['id']}")
        print(f"   Subject: {email['subject']}")
        print(f"   From: {email['sender']}")
        print(f"   Priority: {email['priority']}")
        print(f"   Intent: {email['intent']}")
        print(f"   Summary: {email['summary'][:100]}...")


def test_filter_high_priority():
    print_header("TEST 7: Filter High Priority Emails")
    
    response = requests.get(f"{BASE_URL}/emails/filter/high-priority")
    data = response.json()
    
    print(f"High priority emails: {data['count']}")
    
    for email in data['emails']:
        print(f"\n⚡ {email['subject']}")
        print(f"   Priority: {email['priority']}")
        print(f"   Summary: {email['summary'][:80]}...")


def test_filter_meetings():
    print_header("TEST 8: Filter Meeting Emails")
    
    response = requests.get(f"{BASE_URL}/emails/filter/meetings")
    data = response.json()
    
    print(f"Meeting emails: {data['count']}")
    
    for email in data['emails']:
        print(f"\n{email['subject']}")
        print(f"   Intent: {email['intent']}")
        if email.get('entities'):
            print(f"   Dates: {email['entities'].get('dates', [])}")


def test_email_details():
    print_header("TEST 9: Get Email Details")
    
    response = requests.get(f"{BASE_URL}/emails/list?limit=1")
    emails = response.json().get('emails', [])
    
    if emails:
        email_id = emails[0]['id']
        response = requests.get(f"{BASE_URL}/emails/{email_id}")
        print(json.dumps(response.json(), indent=2))
    else:
        print("No emails found")


def test_mark_as_read():
    print_header("TEST 10: Mark Email as Read")
    
    response = requests.get(f"{BASE_URL}/emails/list?limit=1")
    emails = response.json().get('emails', [])
    
    if emails:
        email_id = emails[0]['id']
        response = requests.patch(f"{BASE_URL}/emails/{email_id}/read")
        print(json.dumps(response.json(), indent=2))
    else:
        print("No emails found")


if __name__ == "__main__":
    print("\nAI Email Assistant - Complete Integration Test")
    print("="*70)
    
    try:
        test_health()
        test_cache()
        test_ai_summarization()
        test_sync_emails()
        test_statistics()
        test_list_emails()
        test_filter_high_priority()
        test_filter_meetings()
        test_email_details()
        test_mark_as_read()
        
        print("\n" + "="*70)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("="*70 + "\n")
    
    except Exception as e:
        print(f"\nTEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
