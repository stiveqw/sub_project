from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)

