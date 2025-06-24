"""
Models for the GroupProject Flask app.
Defines database schema using Peewee ORM for SQLite.
Includes User, Student, Class, and Attendance models.
"""

from peewee import *
from flask_login import UserMixin
import datetime

# =============================
# Database Connection
# =============================
db = SqliteDatabase('classesApp.db')  # SQLite database for the app

# =============================
# Base Model
# =============================
class BaseModel(Model):
    """
    Base model that sets the database for all derived models.
    """
    class Meta:
        database = db

# =============================
# User Model
# =============================
class User(UserMixin, BaseModel):
    """
    User model for teachers and admins.

    Attributes:
        user_id (int): Primary key.
        username (str): Login username (unique).
        password (str): Hashed password.
        is_admin (bool): True for admin, False for teacher.
    """
    user_id = AutoField(unique=True)
    username = CharField(unique=True)
    password = CharField()
    is_admin = BooleanField(default=False)

    def get_id(self):
        """
        Returns the user ID as a string (required by Flask-Login).

        Returns:
            str: User ID.
        """
        return str(self.user_id)

# =============================
# Student Model
# =============================
class Student(BaseModel):
    """
    Student model.

    Attributes:
        student_id (int): Primary key.
        name (str): Student's name.
        email (str): Student's email (unique).
        grade (str): Overall progress/grade (nullable).
    """
    student_id = AutoField(unique=True)
    name = CharField()
    email = CharField(unique=True)
    grade = CharField(null=True)

# =============================
# Class Model
# =============================
class Class(BaseModel):
    """
    Class model representing a class session.

    Attributes:
        class_id (int): Primary key.
        user (User): Teacher for the class.
        title (str): Class title.
        datetime (datetime): Date and time of the class.
    """
    class_id = AutoField(unique=True)
    user = ForeignKeyField(User, backref='classes')
    title = CharField()
    datetime = DateTimeField()

# =============================
# Attendance Model
# =============================
class Attendance(BaseModel):
    """
    Attendance model linking students to classes and tracking attendance.

    Attributes:
        attendance_id (int): Primary key.
        class_ref (Class): The class.
        student (Student): The student.
        attend (bool): True if attended.
        class_grade (str): Grade for this class (nullable).
    """
    attendance_id = AutoField(unique=True)
    class_ref = ForeignKeyField(Class, backref='attendances')
    student = ForeignKeyField(Student, backref='attendances')
    attend = BooleanField(default=False)
    class_grade = CharField(null=True)
