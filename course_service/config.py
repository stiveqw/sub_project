import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('API_GATEWAY_SECRET_KEY', 'default-api-gateway-secret')
    SQLALCHEMY_DATABASE_URI = f"mysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret')
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False  # Set to True in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_COOKIE_CSRF_PROTECT = False

class TestConfig(Config):
    JWT_SECRET_KEY = os.getenv('TEST_JWT_SECRET_KEY')
    TESTING = True
    JWT_REQUIRED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = os.getenv('TEST_COURSE_SERVICE_SECRET_KEY')