from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    
class Festival(db.Model):
    __bind_key__ = 'festival_db'
    __tablename__ = 'festivals'
    id = db.Column(db.Integer, primary_key=True)
    festival_key = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'festival_key': self.festival_key,
            'title': self.title,
            'total_seats': self.total_seats,
            'capacity': self.capacity,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat()
        }