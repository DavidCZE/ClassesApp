"""
Analytics routes for the GroupProject Flask app.
Handles attendance analytics dashboard for admin and teachers.
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import User, Student, Class, Attendance
import datetime

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def analytics():
    """
    Attendance analytics dashboard for admin and teachers.
    Shows class and student attendance statistics.
    """
    now = datetime.datetime.now()
    if current_user.is_admin:
        class_stats = []
        for c in Class.select():
            total = Attendance.select().where(Attendance.class_ref == c).count()
            attended = Attendance.select().where((Attendance.class_ref == c) & (Attendance.attend == True)).count()
            is_future = c.datetime >= now
            class_stats.append({
                'title': c.title,
                'date': c.datetime.strftime('%Y-%m-%d'),
                'teacher': c.user.username,
                'total': total,
                'attended': attended,
                'is_future': is_future
            })
        student_stats = []
        for s in Student.select():
            attended = Attendance.select().where((Attendance.student == s) & (Attendance.attend == True)).count()
            student_stats.append({
                'name': s.name,
                'email': s.email,
                'attended': attended,
                'student_id': s.student_id
            })
        return render_template('analytics.html', class_stats=class_stats, student_stats=student_stats)
    else:
        class_stats = []
        for c in Class.select().where(Class.user == current_user.user_id):
            total = Attendance.select().where(Attendance.class_ref == c).count()
            attended = Attendance.select().where((Attendance.class_ref == c) & (Attendance.attend == True)).count()
            is_future = c.datetime >= now
            class_stats.append({
                'title': c.title,
                'date': c.datetime.strftime('%Y-%m-%d'),
                'total': total,
                'attended': attended,
                'is_future': is_future
            })
        student_stats = []
        for s in Student.select():
            attended = Attendance.select().join(Class).where((Attendance.student == s) & (Attendance.attend == True) & (Class.user == current_user.user_id)).count()
            student_stats.append({
                'name': s.name,
                'email': s.email,
                'attended': attended,
                'student_id': s.student_id
            })
        return render_template('analytics.html', class_stats=class_stats, student_stats=student_stats)
