# gmail_scan.py

import os
import re
import joblib
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from base64 import urlsafe_b64decode
import email

# --- 1. Load Model & Vectorizer ---
model = joblib.load("saved_model/phishing_model.pkl")
vectorizer = joblib.load("saved_model/vectorizer.pkl")

# --- 2. Clean Function ---
stopwords = set(['a', 'an', 'the', 'and', 'or', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'by', 'for', 'to', 'with', 'of', 'that', 'this', 'it', 'from', 'as', 'be', 'have', 'has', 'had', 'not', 'but', 'your', 'you'])

def clean_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = text.lower()
    return ' '.join([word for word in text.split() if word not in stopwords])

# --- 3. Connect to Gmail API ---
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('saved_model/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# --- 4. Fetch Emails & Predict ---
def scan_emails():
    service = get_service()
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
    messages = results.get('messages', [])

    print("\n📥 SCANNING GMAIL INBOX...\n")

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='raw').execute()
        raw_data = urlsafe_b64decode(msg_data['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(raw_data)

        subject = mime_msg['subject'] or ""
        body = ""

        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                if part.get_content_type() == 'text/plain':
                    body += part.get_payload(decode=True).decode(errors='ignore')
        else:
            body = mime_msg.get_payload(decode=True).decode(errors='ignore')

        # Predict
        combined = clean_text(subject + " " + body)
        vector = vectorizer.transform([combined])
        pred = model.predict(vector)[0]

        print(f"📧 Subject: {subject}")
        print("🔍 Status:", "⚠️ PHISHING" if pred == 1 else "✅ Legitimate")
        print("-" * 50)

scan_emails()
