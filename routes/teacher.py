"""
Teacher routes for the GroupProject Flask app.
Handles teacher dashboard, attendance management, and CSV export.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file
from flask_login import login_required, current_user
from models import User, Student, Class, Attendance
import datetime
import io
import csv

# Blueprint for teacher routes
teacher_bp = Blueprint('teacher', __name__)

# =============================
# Teacher Dashboard
# =============================
@teacher_bp.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    """
    Teacher dashboard: view and manage your classes.
    Shows upcoming and past classes for the logged-in teacher.

    Returns:
        Response: Rendered template for teacher dashboard.
    Raises:
        403: If current user is admin (not a teacher).
    """
    if current_user.is_admin:
        abort(403)  # Only teachers can access this dashboard
    now = datetime.datetime.now()
    # Query upcoming and past classes for this teacher
    classes_upcoming = Class.select().where((Class.user == current_user.user_id) & (Class.datetime >= now)).order_by(Class.datetime.asc())
    classes_past = Class.select().where((Class.user == current_user.user_id) & (Class.datetime < now)).order_by(Class.datetime.desc())
    return render_template('teachers.html', classes_upcoming=classes_upcoming, classes_past=classes_past)

# =============================
# Attendance Management
# =============================
@teacher_bp.route('/teacher/attendance/<int:class_id>', methods=['GET', 'POST'])
@login_required
def mark_attendance(class_id):
    """
    Mark or view attendance for a class (teacher only).
    Allows marking students as present or absent for a specific class.

    Args:
        class_id (int): The class session ID.
    Returns:
        Response: Rendered template for attendance or redirect after POST.
    Raises:
        403: If current user is admin (not a teacher).
        404: If class does not exist or does not belong to teacher.
    """
    if current_user.is_admin:
        abort(403)
    # Ensure the class exists and belongs to the current teacher
    class_obj = Class.get_or_none(Class.class_id == class_id, Class.user == current_user.user_id)
    if not class_obj:
        abort(404)
    students = Student.select()
    if request.method == 'POST':
        # Update attendance for each student
        for student in students:
            attend = f'present_{student.student_id}' in request.form
            att, created = Attendance.get_or_create(class_ref=class_obj, student=student)
            att.attend = attend
            att.save()
        flash('Attendance updated!')
        return redirect(url_for('teacher.teacher_dashboard'))
    # Prepare attendance dictionary for template
    attendance = {att.student.student_id: att.attend for att in Attendance.select().where(Attendance.class_ref == class_id)}
    return render_template('teachers.html', class_obj=class_obj, students=students, attendance=attendance)

# =============================
# Attendance Export (CSV)
# =============================
@teacher_bp.route('/teacher/export_attendance/csv')
@login_required
def teacher_export_attendance_csv():
    """
    Export attendance records as CSV (teacher only).
    Columns: Class Title, Date, Attendance Count, Attended Students (comma-separated).
    Only includes classes for the logged-in teacher.

    Returns:
        Response: CSV file download of attendance report.
    Raises:
        403: If current user is admin (not a teacher).
    """
    if current_user.is_admin:
        abort(403)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Class Title', 'Date', 'Attendance Count', 'Attended Students'])
    # Sort classes by date
    classes_sorted = Class.select().where(Class.user == current_user.user_id).order_by(Class.datetime)
    for c in classes_sorted:
        attended = Attendance.select().where((Attendance.class_ref == c) & (Attendance.attend == True))
        names = ', '.join([a.student.name for a in attended])
        writer.writerow([
            c.title,
            c.datetime.strftime('%Y-%m-%d %H:%M'),
            attended.count(),
            names
        ])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='attendance_report.csv')
