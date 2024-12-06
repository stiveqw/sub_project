from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Festival(db.Model):
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
            'date': self.date,
            'created_at': self.created_at
        }

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    festival_key = db.Column(db.String(50), db.ForeignKey('festivals.festival_key'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Reserved')
    reservation_time = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('festival_key', 'seat_number', name='uix_1'),)

