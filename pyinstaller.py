# gmail_gui_app.py

import tkinter as tk
from tkinter import messagebox, scrolledtext
import os, re, email, joblib
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from base64 import urlsafe_b64decode
import ctypes
import os
import sys

# ⬆️ Ask for Admin access
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # Re-run script as admin
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()

from tkinter import messagebox

messagebox.showinfo("Gmail Login Required", 
    "You will be redirected to Gmail login in a secure window.\n"
    "This app does not collect or store your data.\n"
    "Your token will only be saved locally.")



# === Load model & vectorizer ===
model = joblib.load("saved_model/phishing_model.pkl")
vectorizer = joblib.load("saved_model/vectorizer.pkl")

# === Clean Function ===
stopwords = set(['a', 'an', 'the', 'and', 'or', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'by', 'for', 'to', 'with', 'of', 'that', 'this', 'it', 'from', 'as', 'be', 'have', 'has', 'had', 'not', 'but', 'your', 'you'])

def clean_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = text.lower()
    return ' '.join([word for word in text.split() if word not in stopwords])

# === Gmail OAuth Setup ===
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

# === Scan Emails ===
def scan_emails_gui():
    try:
        service = get_service()
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=5).execute()
        messages = results.get('messages', [])
        output_text.delete(1.0, tk.END)

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

            combined = clean_text(subject + " " + body)
            vector = vectorizer.transform([combined])
            pred = model.predict(vector)[0]

            result = "⚠️ PHISHING" if pred == 1 else "✅ LEGITIMATE"
            output_text.insert(tk.END, f"Subject: {subject}\nStatus: {result}\n{'-'*50}\n")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# === Tkinter GUI ===
app = tk.Tk()
app.title("AI Email Phishing Detector (Gmail Scanner)")
app.geometry("700x500")

tk.Label(app, text="Click to scan your Gmail inbox:", font=("Arial", 14)).pack(pady=10)
tk.Button(app, text="📩 Scan Gmail Inbox", command=scan_emails_gui, font=("Arial", 12), bg="blue", fg="white").pack(pady=5)

output_text = scrolledtext.ScrolledText(app, width=80, height=20)
output_text.pack(pady=10)

app.mainloop()
