# 📚 PDF Vocabulary Reader

## 🔗 Live Demo
👉 https://file-opener-with-word-meaning-display.streamlit.app/

---

## 📌 Project Overview
PDF Vocabulary Reader is an AI-powered web application that allows users to upload PDF files and instantly view word meanings while reading.  
It helps students improve vocabulary and comprehension by making difficult words understandable in real-time without leaving the document.

---

## 🚀 Key Features
- 📄 Upload any PDF file  
- 🔍 Click on words to get instant meaning  
- 🤖 AI-based vocabulary assistance  
- ⚡ Fast and lightweight Streamlit interface  
- 🌐 Deployed on Streamlit Cloud  
- 📱 Simple and user-friendly UI  

---

## 🧠 Problem It Solves
While reading PDFs (books, notes, research papers), students often struggle with difficult vocabulary and constantly switch apps or search engines to check meanings.  
This project solves that problem by providing instant word meanings inside the document reader itself, improving focus, reading speed, and learning efficiency.

---

## 🛠️ Tech Stack
- Python  
- Streamlit  
- PyMuPDF (PDF Processing)  
- NLP / Dictionary API  
- HTML & CSS (UI Styling)  

---

## 🏗️ How It Works (System Workflow)
1. User uploads a PDF file  
2. The application extracts text from the PDF using PyMuPDF  
3. User clicks on any word in the document  
4. The system processes the selected word  
5. Meaning is fetched using NLP/Dictionary API  
6. Instant output is displayed on the web interface  

---

## 💻 Installation (Run Locally)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/TejasAntalDoon/PDF-Vocabulary-Reader.git
cd PDF-Vocabulary-Reader
pip install -r requirements.txt
streamlit run app.py
