import streamlit as st
import joblib
import re

# Load model & vectorizer
model = joblib.load("saved_model/phishing_model.pkl")
vectorizer = joblib.load("saved_model/vectorizer.pkl")

# Clean function
basic_stopwords = set([
    'a', 'an', 'the', 'and', 'or', 'is', 'are', 'was', 'were', 'in', 'on',
    'at', 'by', 'for', 'to', 'with', 'of', 'that', 'this', 'it', 'from',
    'as', 'be', 'have', 'has', 'had', 'not', 'but', 'your', 'you'
])

def clean_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = text.lower()
    tokens = text.split()
    return ' '.join([word for word in tokens if word not in basic_stopwords])

# Streamlit App
st.title("📧 AI Email Phishing Detector")

subject = st.text_input("Email Subject")
body = st.text_area("Email Body")

if st.button("Analyze"):
    full_text = subject + " " + body
    cleaned = clean_text(full_text)
    vectorized = vectorizer.transform([cleaned])
    result = model.predict(vectorized)[0]

    if result == 1:
        st.error("⚠️ Warning: This email is likely a PHISHING attempt.")
    else:
        st.success("✅ This email seems LEGITIMATE.")
