from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime
import base64
from email.mime.text import MIMEText

def fetch_emails(access_token: str, max_results: int = 10):
    credentials = Credentials(token=access_token)
    service = build('gmail', 'v1', credentials=credentials)

    results = service.users().messages().list(    
        userId = 'me',
        maxResults=max_results,
        lableIds=['INBOX']
    ).execute()

    messages = results.get('messages', [])
    emails =[]

    for msg in messages:
        message = service.users().messages().get(
            userId = 'me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

        body =''
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
            
        elif 'body' in message['payload']:
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

        emails.append({
            'message_id' : message['id'],
            'thread_id': message['threadId'],
            'subject': subject,
            'sender': sender, 
            'body': body[:500],
            'date': date
        })

    return emails

def get_user_profile(access_token: str):
    credentials = Credentials(token=access_token)
    service = build('gmail', 'v1', credentials=credentials)

    profile = service.users().getProfile(userId='me').execute()
    return {
        'email': profile['emailAddress'],
        'messages_total': profile['messagesTotal'],
        'threads_total': profile['threadsTotal']
    }