"""
Authentication routes for the GroupProject Flask app.
Handles login and logout for all users.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from werkzeug.security import check_password_hash

# Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# =============================
# Login Route
# =============================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page for all users (admin and teacher).
    Authenticates user and redirects to the appropriate dashboard.
    """
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_or_none(User.username == username)
        if not user:
            error = 'User does not exist.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'
        else:
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('teacher.teacher_dashboard'))
    return render_template('auth.html', error=error)

# =============================
# Logout Route
# =============================
@auth_bp.route('/logout')
@login_required
def logout():
    """
    Logout the current user and redirect to login page.
    """
    logout_user()
    return redirect(url_for('auth.login'))
