## This is tool used to identify the Phishing in Gmail

## How to use?
---
## 🛠️ Setup Instructions

### 1. 🔑 Enable Gmail API & Get Credentials

1. Go to [Google Developers Console](https://console.developers.google.com/)
2. Create a project → Enable **Gmail API**
3. Go to **Credentials → OAuth Client ID**
4. Choose **Desktop App** → Download `credentials.json`
5. Place it in your project folder

---

### 2. 🧪 Local Development (Python App)

```bash
# Step 1: Clone or extract project
cd phishing-detector-desktop

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Run the app (admin rights required)
python gmail_gui_app.py
```
### 3. Build .EXE (Windows Desktop App)
```
pip install pyinstaller
```

## Build executable
```
pyinstaller --onefile --windowed gmail_gui_app.py
```

## 🔐 Security & Privacy
Uses Google's secure OAuth 2.0 flow

No emails are stored or read outside your system

No 3rd-party APIs or servers involved

Token is stored locally only using token.json

You control the access — can revoke at Google Security Settings

## 📦 Dependencies
```
joblib
scikit-learn
pandas
tkinter
google-api-python-client
google-auth
google-auth-oauthlib
```
## Screenhots

![Image](https://github.com/user-attachments/assets/978a573d-bba0-4abe-b6d7-5c7f70caac7b)

![Image](https://github.com/user-attachments/assets/21a0d25e-d1e7-4084-aab2-88410e7dacee)
