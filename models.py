# Models for the GroupProject Flask app
# Using Peewee ORM for SQLite database

from peewee import *
from flask_login import UserMixin
import datetime

# Database connection
# This will create/use 'classesApp.db' SQLite database

db = SqliteDatabase('classesApp.db')

# Base model to set the database for all models
class BaseModel(Model):
    class Meta:
        database = db

# User model for teachers and admins
class User(UserMixin, BaseModel):
    user_id = AutoField(unique=True)  # Primary key
    username = CharField(unique=True)  # Login username
    password = CharField()  # Hashed password
    is_admin = BooleanField(default=False)  # True for admin, False for teacher

    def get_id(self):
        # Required by Flask-Login
        return str(self.user_id)

# Student model
class Student(BaseModel):
    student_id = AutoField(unique=True)  # Primary key
    name = CharField()  # Student's name
    email = CharField(unique=True)  # Student's email
    grade = CharField(null=True)  # Overall progress/grade

# Class model (represents a class session)
class Class(BaseModel):
    class_id = AutoField(unique=True)  # Primary key
    user = ForeignKeyField(User, backref='classes')  # Teacher for the class
    title = CharField()  # Class title
    datetime = DateTimeField()  # Date and time of the class

# Attendance model (links students to classes and tracks attendance)
class Attendance(BaseModel):
    attendance_id = AutoField(unique=True)  # Primary key
    class_ref = ForeignKeyField(Class, backref='attendances')  # The class
    student = ForeignKeyField(Student, backref='attendances')  # The student
    attend = BooleanField(default=False)  # True if attended
    class_grade = CharField(null=True)  # Grade for this class
