import os

class Config:
    SECRET_KEY = os.environ.get('MAIN_SERVICE_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f"mysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

