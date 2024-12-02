import os

class Config:
    SECRET_KEY = os.environ.get('ERROR_SERVICE_SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

