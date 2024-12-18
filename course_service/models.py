from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_key = db.Column(db.String(50), unique=True, nullable=False)
    course_name = db.Column(db.String(255), nullable=False)
    professor = db.Column(db.String(255), nullable=False)
    max_students = db.Column(db.Integer, nullable=False)
    current_students = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(100))
    year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
 

class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    course_key = db.Column(db.String(50), db.ForeignKey('courses.course_key'), nullable=False)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'), nullable=False)
    registration_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('Applied', 'Cancelled'), default='Applied')

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
