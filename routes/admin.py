"""
Admin routes for the GroupProject Flask app.
Handles admin dashboard, class, teacher, student management, and attendance export.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file
from flask_login import login_required, current_user
from models import db, User, Student, Class, Attendance
from werkzeug.security import generate_password_hash
import datetime
import io
import csv

# Blueprint for admin routes
admin_bp = Blueprint('admin', __name__)

# =============================
# Admin Dashboard
# =============================
@admin_bp.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    """
    Admin dashboard: manage classes, teachers, and students.
    Handles adding new classes, teachers, and students via POST.
    Shows lists of classes, teachers, and students.
    """
    if not current_user.is_admin:
        abort(403)
    # Add class
    if request.method == 'POST' and 'title' in request.form:
        try:
            dt = datetime.datetime.strptime(request.form['datetime'], '%Y-%m-%dT%H:%M')
            Class.create(title=request.form['title'], datetime=dt, user=request.form['teacher_id'])
            flash('Class added!')
        except Exception as e:
            flash('Error: ' + str(e))
    # Add teacher
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'is_teacher' in request.form:
        try:
            hashed_pw = generate_password_hash(request.form['password'])
            User.create(username=request.form['username'], password=hashed_pw, is_admin=False)
            flash('Teacher added!')
        except Exception as e:
            flash('Error: ' + str(e))
    # Add student
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'is_student' in request.form:
        try:
            Student.create(name=request.form['name'], email=request.form['email'])
            flash('Student added!')
        except Exception as e:
            flash('Error: ' + str(e))
    now = datetime.datetime.now()
    classes_past = Class.select().where(Class.datetime < now).order_by(Class.datetime.desc())
    classes_future = Class.select().where(Class.datetime >= now).order_by(Class.datetime.asc())
    teachers = User.select().where(User.is_admin == False)
    students = Student.select()
    total_classes_upcoming = classes_future.count()
    total_classes_past = classes_past.count()
    total_teachers = teachers.count()
    total_students = students.count()
    return render_template('admin.html', classes_past=classes_past, classes_future=classes_future, teachers=teachers, students=students, total_classes_upcoming=total_classes_upcoming, total_classes_past=total_classes_past, total_teachers=total_teachers, total_students=total_students)

# =============================
# Class Management
# =============================
@admin_bp.route('/admin/class/<int:class_id>')
@login_required
def admin_class_detail(class_id):
    """
    Show details and attendance for a class.
    """
    if not current_user.is_admin:
        abort(403)
    class_obj = Class.get_or_none(Class.class_id == class_id)
    if not class_obj:
        abort(404)
    attendances = (Attendance.select(Attendance, Student).join(Student).where(Attendance.class_ref == class_obj))
    return render_template('admin_class_detail.html', class_obj=class_obj, attendances=attendances)

@admin_bp.route('/admin/class/<int:class_id>/delete', methods=['POST'])
@login_required
def admin_delete_class(class_id):
    """
    Delete a class (admin only).
    """
    if not current_user.is_admin:
        abort(403)
    class_obj = Class.get_or_none(Class.class_id == class_id)
    if class_obj:
        class_obj.delete_instance()
        flash('Class deleted!')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/class/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_class(class_id):
    """
    Edit a class (admin only).
    """
    if not current_user.is_admin:
        abort(403)
    class_obj = Class.get_or_none(Class.class_id == class_id)
    if not class_obj:
        abort(404)
    if request.method == 'POST':
        try:
            class_obj.title = request.form['title']
            class_obj.datetime = datetime.datetime.strptime(request.form['datetime'], '%Y-%m-%dT%H:%M')
            class_obj.user = request.form['teacher_id']
            class_obj.save()
            flash('Class updated!')
            return redirect(url_for('admin.admin_dashboard'))
        except Exception as e:
            flash('Error: ' + str(e))
    teachers = User.select().where(User.is_admin == False)
    return render_template('edit_class.html', class_obj=class_obj, teachers=teachers)

# =============================
# Student Management
# =============================
@admin_bp.route('/admin/student/<int:student_id>/delete', methods=['POST'])
@login_required
def admin_delete_student(student_id):
    """
    Delete a student (admin only).
    """
    if not current_user.is_admin:
        abort(403)
    student = Student.get_or_none(Student.student_id == student_id)
    if student:
        student.delete_instance()
        flash('Student deleted!')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/student/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_student(student_id):
    """
    Edit a student (admin only).
    """
    if not current_user.is_admin:
        abort(403)
    student = Student.get_or_none(Student.student_id == student_id)
    if not student:
        abort(404)
    if request.method == 'POST':
        try:
            student.name = request.form['name']
            student.email = request.form['email']
            student.save()
            flash('Student updated!')
            return redirect(url_for('admin.admin_dashboard'))
        except Exception as e:
            flash('Error: ' + str(e))
    return render_template('edit_student.html', student=student)

# =============================
# Teacher Management
# =============================
@admin_bp.route('/admin/teacher/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_teacher(user_id):
    """
    Delete a teacher (admin only).
    """
    if not current_user.is_admin:
        abort(403)
    teacher = User.get_or_none(User.user_id == user_id, User.is_admin == False)
    if teacher:
        teacher.delete_instance()
        flash('Teacher deleted!')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/teacher/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_teacher(user_id):
    """
    Edit a teacher (admin only).
    """
    if not current_user.is_admin:
        abort(403)
    teacher = User.get_or_none(User.user_id == user_id, User.is_admin == False)
    if not teacher:
        abort(404)
    if request.method == 'POST':
        try:
            teacher.username = request.form['username']
            if request.form['password']:
                teacher.password = generate_password_hash(request.form['password'])
            teacher.save()
            flash('Teacher updated!')
            return redirect(url_for('admin.admin_dashboard'))
        except Exception as e:
            flash('Error: ' + str(e))
    return render_template('edit_teacher.html', teacher=teacher)

# =============================
# Attendance Export
# =============================
@admin_bp.route('/admin/export_attendance/csv')
@login_required
def export_attendance_csv():
    """
    Export all class attendance as CSV for all teachers.
    Columns: Class Title, Date, Teacher, Attendance Count, Attended Students (comma-separated).
    """
    if not current_user.is_admin:
        abort(403)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Class Title', 'Date', 'Teacher', 'Attendance Count', 'Attended Students'])
    # Sort classes by date
    classes_sorted = Class.select().order_by(Class.datetime)
    for c in classes_sorted:
        attended = Attendance.select().where((Attendance.class_ref == c) & (Attendance.attend == True))
        names = ', '.join([a.student.name for a in attended])
        writer.writerow([
            c.title,
            c.datetime.strftime('%Y-%m-%d %H:%M'),
            c.user.username,
            attended.count(),
            names
        ])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='attendance_report.csv')
