# GroupProject: Online Class & Attendance Management System

## Purpose
This web application allows administrators and teachers to manage classes, students, attendance, and grades. It provides dashboards for both roles, analytics, and export features for record-keeping.

## Features
- Admin and teacher login
- Admin dashboard for managing teachers, students, and classes
- Teacher dashboard for managing their own classes and attendance
- Attendance analytics and export (CSV)
- Student progress and per-class grade tracking
- Mobile-friendly responsive design

## Project Structure
- `app.py` – Main Flask app, blueprint registration
- `models.py` – Database models (Peewee ORM)
- `routes/` – Modular route files:
  - `auth.py` – Authentication (login/logout)
  - `admin.py` – Admin dashboard and management
  - `teacher.py` – Teacher dashboard and attendance
  - `student.py` – Student profile and grades
  - `analytics.py` – Analytics dashboard
- `templates/` – HTML templates (Jinja2)
- `static/` – CSS and static files

## Requirements
- Python 3.9+
- pip (Python package manager)
- Install dependencies:
  - Flask
  - Flask-Login
  - peewee
  - werkzeug

## Setup & Running
1. Clone/download the project.
2. Install dependencies:
   ```sh
   pip install flask flask-login peewee werkzeug
   ```
3. Run the app:
   ```sh
   python app.py
   ```
4. Open your browser and go to `http://127.0.0.1:5000/`

## Default Admin Login
- Username: `admin`
- Password: `admin123`

## How to Use
- **Admin:**
  - Log in as admin to add/edit/delete teachers, students, and classes.
  - View analytics and export attendance for all classes.
- **Teacher:**
  - Log in as teacher to view/manage your classes and mark attendance.
  - View analytics and grade students
  - Export attendance for your own classes.


## Notes
- All data is stored in a local SQLite database (`classesApp.db`).
- The app is mobile-friendly and works in modern browsers.
