# Placement Portal Application (PPA)

A role-based web application for managing campus recruitment activities between **institutes, companies, and students**.  
The system allows institutes to manage placement drives, companies to recruit students, and students to apply for job opportunities through a centralized platform.

The application is built using **Flask for backend APIs**, **VueJS for frontend UI**, and **Redis + Celery for background jobs**.

---

# Features

## Role Based Access

The system supports three types of users:

- **Admin (Institute Placement Cell)**
- **Company**
- **Student**

Each role has a dedicated dashboard and permissions.

---

# Admin Functionalities

Admin manages the entire platform.

- View dashboard statistics
  - Total students
  - Total companies
  - Total placement drives
- Approve or reject company registrations
- Approve or reject placement drives
- View all student applications
- Search students and companies
- Blacklist or deactivate users
- Monitor placement activity

Admin is **created programmatically when the database is initialized**.

---

# Company Functionalities

Companies can conduct recruitment drives.

- Register company profile
- Wait for admin approval
- Create placement drives
- View applicants
- Shortlist candidates
- Update application status
- Schedule interviews
- Mark final selections

---

# Student Functionalities

Students can participate in placement drives.

- Register and login
- Update student profile
- Upload resume
- View available placement drives
- Apply for drives
- Track application status
- View placement history

---

# Background Jobs (Celery + Redis)

The system uses Celery and Redis for asynchronous and scheduled tasks.

### Daily Reminder Job

Runs daily to notify students about:

- Upcoming application deadlines
- Active placement drives

Notifications can be sent via:

- Email
- SMS
- Google Chat Webhook

---

### Monthly Activity Report

Runs on the **first day of every month**.

The report includes:

- Total placement drives conducted
- Total applications
- Students selected

The report is generated as **HTML** and sent to the admin via email.

---

### Export Applications (Async Job)

Students can export their placement history.

The exported CSV includes:

- Student ID
- Company Name
- Drive Title
- Application Status
- Application Date

The export is handled asynchronously using Celery.

---

# Tech Stack

### Backend

- Flask
- SQLAlchemy
- Redis
- Celery

### Frontend

- VueJS
- Bootstrap
- Vite

### Database

- SQLite

---

# Project Structure

```
placement_portal_v2/
│
├── backend/
│   ├── routes/
│   ├── utils/
│   ├── uploads/
│   ├── exports/
│   ├── app.py
│   ├── models.py
│   ├── tasks.py
│   ├── celery_worker.py
│   ├── config.py
│   ├── init_db.py
│   ├── seed_db.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
│
├── frontend-cli/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vue.config.js
│
├── venv/
│
├── dump_schema.py
├── migrate.py
├── test_broadcast.py
└── run.txt
```

---

# Installation

Clone the repository

```
git clone https://github.com/yourusername/placement-portal.git
cd placement-portal
```

Create a virtual environment

```
python -m venv venv
```

Activate environment

Windows

```
venv\Scripts\activate
```

Install backend dependencies

```
pip install -r backend/requirements.txt
```

Install frontend dependencies

```
cd frontend
npm install
```

---

# Running the Application

### Start Redis

```
redis-server
```

### Start Celery Worker

```
celery -A backend.celery_worker.celery worker --loglevel=info
```

### Start Celery Beat Scheduler

```
celery -A backend.celery_worker.celery beat --loglevel=info
```

### Run Flask Backend

```
python backend/app.py
```

### Run Vue Frontend

```
cd frontend
npm run dev
```

---



