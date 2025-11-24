# 🚀 AI Email Classification System  
Automation Engineer Assignment – Swapnil Kadam

## 📌 Overview
This project is built as part of the **Automation Engineer Assessment**.  
I selected **Challenge 2 – AI Email Categorization**, which focuses on reducing manual effort for support teams by automatically understanding, categorizing, and processing incoming emails.

My system uses **Flask**, **Google OAuth (Gmail API)**, and **Google Gemini AI** to automatically fetch emails, classify them, and export the results into CSV format.

---

## 🎯 Features

### ✔ Gmail Login
Users can authenticate using Google OAuth to fetch their inbox emails securely.

### ✔ Date Range Filter
Choose start and end dates to load emails only from the selected range.

### ✔ AI Email Categorization
Emails are automatically classified into:
- Technical Email  
- Formal Email  
- Informal Email  
- Request Email  
- Reply Email  
- Follow-Up Email  
- Professional Email  
- Unknown  

### ✔ AI-Powered Understanding
Uses **Gemini 2.5 Flash** model to extract the meaning of the email and assign categories.

### ✔ Dashboard
A clean, modern interface showing:
- Sender  
- Receiver  
- Date  
- Email Body  
- Category (auto-classified)  

Includes:
- Filtering by category  
- Pagination  
- Real-time loader animation  

### ✔ CSV Export
Download all processed emails with:
- Sender  
- Receiver  
- Date  
- Message  
- Category  

---

## 🛠 Tech Stack

| Component | Technology |
|----------|-----------|
| Backend  | Flask (Python) |
| AI Model | Google Gemini 2.5 Flash |
| Email Fetching | Gmail API |
| UI | HTML, CSS, Inline Styling |
| Data Export | CSV |

---

## 📂 Project Structure


---

## ▶ How It Works

1. User logs in via Google OAuth  
2. Selects a date range  
3. System fetches emails using Gmail API  
4. Extracts subject + body  
5. Uses Gemini AI to classify the email meaning  
6. Displays results on dashboard  
7. User can filter by category  
8. User can export results as CSV  

---
