from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Student, Class, Attendance
from werkzeug.security import check_password_hash
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get_or_none(User.id == user_id)

@app.before_request
def before_request():
    if db.is_closed():
        db.connect()

@app.teardown_request
def teardown_request(exception):
    if not db.is_closed():
        db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_or_none(User.username == username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('teacher_dashboard'))
        flash('Invalid credentials')
    return render_template('auth.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)
    # Add class
    if request.method == 'POST' and 'subject' in request.form:
        try:
            dt = datetime.datetime.strptime(request.form['datetime'], '%Y-%m-%dT%H:%M')
            Class.create(subject=request.form['subject'], datetime=dt, teacher=request.form['teacher_id'])
            flash('Class added!')
        except Exception as e:
            flash('Error: ' + str(e))
    # Add teacher
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        try:
            User.create(username=request.form['username'], password=request.form['password'], role='teacher')
            flash('Teacher added!')
        except Exception as e:
            flash('Error: ' + str(e))
    # Add student
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form:
        try:
            Student.create(name=request.form['name'], email=request.form['email'])
            flash('Student added!')
        except Exception as e:
            flash('Error: ' + str(e))
    classes = Class.select()
    teachers = User.select().where(User.role == 'teacher')
    students = Student.select()
    return render_template('admin.html', classes=classes, teachers=teachers, students=students)

@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        abort(403)
    classes = Class.select().where(Class.teacher == current_user.id)
    return render_template('teachers.html', classes=classes)

@app.route('/teacher/attendance/<int:class_id>', methods=['GET', 'POST'])
@login_required
def mark_attendance(class_id):
    if current_user.role != 'teacher':
        abort(403)
    class_obj = Class.get_or_none(Class.id == class_id, Class.teacher == current_user.id)
    if not class_obj:
        abort(404)
    students = Student.select()
    if request.method == 'POST':
        for student in students:
            present = f'present_{student.id}' in request.form
            att, created = Attendance.get_or_create(class_ref=class_obj, student=student)
            att.present = present
            att.save()
        flash('Attendance updated!')
        return redirect(url_for('teacher_dashboard'))
    attendance = {att.student.id: att.present for att in Attendance.select().where(Attendance.class_ref == class_id)}
    return render_template('teachers.html', class_obj=class_obj, students=students, attendance=attendance)

if __name__ == '__main__':
    db.connect()
    db.create_tables([User, Student, Class, Attendance], safe=True)
    app.run(debug=True)
