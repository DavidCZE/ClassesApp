from peewee import *
from flask_login import UserMixin
import datetime

db = SqliteDatabase('school.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(UserMixin, BaseModel):
    username = CharField(unique=True)
    password = CharField()
    role = CharField()  # 'admin' or 'teacher'

class Student(BaseModel):
    name = CharField()
    email = CharField(unique=True)
    created_at = DateTimeField(default=datetime.datetime.now)

class Class(BaseModel):
    subject = CharField()
    datetime = DateTimeField()
    teacher = ForeignKeyField(User, backref='classes')

class Attendance(BaseModel):
    class_ref = ForeignKeyField(Class, backref='attendances')
    student = ForeignKeyField(Student, backref='attendances')
    present = BooleanField(default=False)
