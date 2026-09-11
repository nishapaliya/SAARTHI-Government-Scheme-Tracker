# SAARTHI – Government Scheme & Citizen Benefit Tracker

> **An integrated platform for discovering, checking eligibility for, applying to, and tracking government schemes.**

🏆 **2nd Prize – Software Development Competition**  
Organized by the Department of Computer Science

---

## 📌 About the Project

**SAARTHI** is a Flask and MySQL-based web platform designed to simplify access to government welfare schemes and citizen benefits.

Government schemes often involve complicated application procedures, repeated document submission, lengthy verification processes, and limited visibility into application status.

SAARTHI brings these activities together into a single platform where citizens can discover suitable schemes, check eligibility, submit applications, manage documents, and track their application progress.

---

## 🎯 Problem Statement

Citizens may face several difficulties while applying for government schemes:

- Complex application procedures
- Difficulty finding suitable government schemes
- Uncertainty about scheme eligibility
- Repeated document submission
- Lengthy verification processes
- Difficulty tracking application status
- Limited transparency during the application process
- Poor communication regarding application updates
- Time-consuming manual document verification

---

## 💡 Proposed Solution

SAARTHI provides an integrated digital platform that allows citizens to:

- 🔎 Discover government schemes
- ✅ Check eligibility
- 📄 Upload and manage required documents
- 🤖 Use AI assistance for scheme-related queries
- 🔍 Perform OCR-based document processing
- 📝 Apply for eligible schemes
- 📊 Track application status
- 🔔 Receive application-related notifications
- 📌 Manage reminders
- 🆘 Submit and manage grievances through the Help Desk

Administrators can manage and monitor the system through a dedicated administration interface.

---

## ✨ Key Features

### 👤 Citizen Portal

- Citizen registration and login
- Personalized citizen dashboard
- Government scheme catalog
- Scheme details and eligibility information
- Online application workflow
- Application status tracking
- Document vault
- Application document management
- Reminders
- Grievance submission
- Help Desk

### 🏛️ Admin Portal

- Secure administrator authentication
- Administrative dashboard
- Application monitoring
- Scheme management
- Analytics
- Citizen/application-related management

### 🤖 AI & Document Processing

- AI-powered chatbot assistant
- OCR-based document text extraction
- Document verification using predefined document rules
- Support for processing documents such as:
  - Aadhaar
  - PAN
  - Bank passbook

### 📧 Notifications

- Application-related notifications
- Email notification support
- Brevo email integration

### 📊 Analytics & Export

- Application and system analytics
- Data visualization
- Export functionality

---

## 🛠️ Technologies Used

### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2 Templates

### Backend

- Python
- Flask
- Flask-Login
- Flask-WTF
- Flask-Babel

### Database

- MySQL
- MySQL Connector / PyMySQL

### AI & OCR

- Groq API
- OCR processing
- Tesseract OCR
- PyTesseract
- Pillow

### Data & Visualization

- Pandas
- NumPy
- Matplotlib

### Email

- Brevo API

### Security & Configuration

- bcrypt
- python-dotenv
- Environment-based configuration

### Testing & Other Tools

- Pytest
- ReportLab
- OpenPyXL
- APScheduler

---

## 🏗️ Project Structure

```text
SAARTHI-Government-Scheme-Tracker/
│
├── ai/
│   ├── __init__.py
│   ├── document_ai.py
│   ├── groq_client.py
│   └── ocr_service.py
│
├── database/
│   ├── db.py
│   ├── schema.sql
│   ├── schemes_upsert.sql
│   └── seeds.sql
│
├── modules/
│   ├── analytics/
│   │   └── routes.py
│   ├── applications/
│   │   └── routes.py
│   ├── auth/
│   │   └── routes.py
│   ├── chatbot/
│   │   └── routes.py
│   ├── documents/
│   │   └── routes.py
│   ├── export/
│   │   └── routes.py
│   ├── helpdesk/
│   │   └── routes.py
│   ├── notifications/
│   │   └── routes.py
│   ├── reminders/
│   │   └── routes.py
│   └── schemes/
│       └── routes.py
│
├── services/
│   └── email_service.py
│
├── static/
│   ├── css/
│   ├── images/
│   └── js/
│
├── templates/
│   ├── admin/
│   ├── applications/
│   ├── auth/
│   ├── citizen/
│   ├── documents/
│   ├── helpdesk/
│   ├── schemes/
│   ├── base.html
│   └── index.html
│
├── tests/
│   └── test_app.py
│
├── app.py
├── config.py
├── generate_hash.py
└── requirements.txt
