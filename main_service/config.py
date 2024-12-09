import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('MAIN_SERVICE_SECRET_KEY', 'default-main-service-secret')
    SQLALCHEMY_DATABASE_URI = f"mysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_BINDS = {
        'festival_db': f"mysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/festival_db"
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret')
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False  # Set to True in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    COURSE_SERVICE_URL = os.getenv('COURSE_SERVICE_URL', 'http://localhost:5001')
    FESTIVAL_SERVICE_URL = os.getenv('FESTIVAL_SERVICE_URL', 'http://localhost:5002')

