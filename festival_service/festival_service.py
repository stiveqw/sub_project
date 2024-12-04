from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes import festival as festival_blueprint

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

# 블루프린트 등록 시 url_prefix를 제거
app.register_blueprint(festival_blueprint)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5002, debug=True)

