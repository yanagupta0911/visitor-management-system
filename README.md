# Visitor Management System

A web-based Visitor Management System built with Python and FastAPI to manage visitor registration, check-in, check-out, and visitor records efficiently.

## 📌 Project Overview

The Visitor Management System is designed to digitize and simplify the process of managing visitors.

It provides a centralized web application where visitor information can be recorded, managed, and tracked. The system helps reduce manual record keeping and provides an organized way to handle visitor data.

## ✨ Features

- 👤 Visitor registration
- 📝 Capture visitor details
- 🕐 Visitor check-in management
- 🚪 Visitor check-out management
- 📋 View visitor records
- ✏️ Update visitor information
- 🗑️ Delete visitor records
- 📷 Check-in and check-out photo support
- 🌐 Web-based interface
- ⚡ FastAPI backend
- 🗄️ Database integration
- 🔐 Environment-based configuration
- 🔎 Visitor record management

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn

### Frontend
- HTML
- CSS
- JavaScript
- Jinja2 Templates

### Database
- SQLite

### Tools
- Git
- GitHub
- Python Virtual Environment
- Docker



⚙️ Installation
1. Clone the repository
git clone https://github.com/yanagupta0911/visitor-management-system.git
2. Open the project folder
cd visitor-management-system
3. Create a virtual environment
python -m venv venv
4. Activate the virtual environment

For Windows PowerShell:

.\venv\Scripts\Activate.ps1
5. Install dependencies
pip install -r requirements.txt
🔐 Environment Configuration

Create a .env file in the project root.

You can use .env.example as a reference.

Example:

SECRET_KEY=your-secret-key

Do not upload your actual .env file or secret keys to GitHub.

▶️ How to Run

Make sure the virtual environment is activated.

Run:

python -m uvicorn main:app --reload

The application will start at:

http://127.0.0.1:8000

Open the URL in your browser to access the application.

🔄 Application Workflow
Visitor
   ↓
Visitor Registration
   ↓
Visitor Check-In
   ↓
Visitor Information Stored
   ↓
Visitor Visit
   ↓
Visitor Check-Out
   ↓
Visit Record Completed

## 📂 Project Structure

```text
visitor-management-system/
│
├── app/
│   └── ...
│
├── frontend/
│   └── ...
│
├── checkin_photos/
├── checkout_photos/
├── tests/
│
├── main.py
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
└── README.md
