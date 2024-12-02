from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# 여기에 모델 import
from models import Course, Registration, Student

# 여기에 라우트 및 기타 설정 추가

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

