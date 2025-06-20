"""
Main Flask app for the GroupProject.
Handles app setup, blueprint registration, analytics, and student profile.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Student, Class, Attendance
from werkzeug.security import check_password_hash, generate_password_hash
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.teacher import teacher_bp
from routes.analytics import analytics_bp
from routes.student import student_bp
import datetime

# =============================
# Flask App and Login Manager
# =============================

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Secret key for session management

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated

# =============================
# User Loader for Flask-Login
# =============================
@login_manager.user_loader
def load_user(user_id):
    """
    Load a user by user_id for Flask-Login.
    """
    return User.get_or_none(User.user_id == user_id)

# =============================
# Database Connection Handlers
# =============================
@app.before_request
def before_request():
    """
    Ensure the database is connected before each request.
    """
    if db.is_closed():
        db.connect()

@app.teardown_request
def teardown_request(exception):
    """
    Close the database connection after each request.
    """
    if not db.is_closed():
        db.close()

# =============================
# Register Blueprints
# =============================
# Import and register all blueprints for modular routing
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(student_bp)

# =============================
# Home Route
# =============================
@app.route('/')
def index():
    """
    Redirect to the appropriate dashboard based on user role.
    """
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))
    else:
        return redirect(url_for('teacher.teacher_dashboard'))


# =============================
# App Entry Point
# =============================
if __name__ == '__main__':
    db.connect()
    db.create_tables([User, Student, Class, Attendance], safe=True)
    # Ensure at least one admin exists
    if not User.select().where(User.is_admin == True).exists():
        User.create(username='admin', password=generate_password_hash('admin123'), is_admin=True)
        print('Default admin created: username=admin, password=admin123')
    app.run(debug=True)
