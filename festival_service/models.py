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
            'title': self.title,
            'capacity': self.capacity,
            'date': self.date,
        }

