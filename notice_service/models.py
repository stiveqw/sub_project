from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Notice(db.Model):
    __tablename__ = 'notices'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)