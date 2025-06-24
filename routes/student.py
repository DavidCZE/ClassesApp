"""
Student profile routes for the GroupProject Flask app.
Handles viewing and updating student progress and per-class grades.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import Student, Attendance, Class

student_bp = Blueprint('student', __name__)

@student_bp.route('/student/<int:student_id>', methods=['GET', 'POST'])
def student_profile(student_id):
    """
    Student profile page for viewing and updating overall and per-class grades.

    Args:
        student_id (int): The student's unique ID.
    Returns:
        Response: Rendered template for student profile or redirect after POST.
    Raises:
        404: If student does not exist.
    """
    student = Student.get_or_none(Student.student_id == student_id)
    if not student:
        abort(404)
    # Get all attended classes for this student
    attended_classes = (Attendance.select(Attendance, Class)
        .join(Class)
        .where((Attendance.student == student) & (Attendance.attend == True)))
    if request.method == 'POST':
        # Update overall grade
        student.grade = request.form.get('grade')
        student.save()
        # Update grades for attended classes
        for att in attended_classes:
            class_grade = request.form.get(f'class_grade_{att.class_ref.class_id}')
            if class_grade is not None:
                att.class_grade = class_grade
                att.save()
        flash('Student progress updated!')
        return redirect(url_for('student.student_profile', student_id=student_id))
    return render_template('student_profile.html', student=student, attended_classes=attended_classes)
