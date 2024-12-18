from flask import Flask, request, jsonify, render_template, url_for
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from config import Config
from config import TestConfig
from models import db
from routes import festival as festival_blueprint
import os

app = Flask(__name__)
env = os.environ.get('FLASK_ENV')

if env == 'testing':
    app.config.from_object(TestConfig)
    app.config['TESTING'] = True
else:
    app.config.from_object(Config)
    app.config['TESTING'] = os.environ.get('FLASK_TESTING', 'False') == 'True'

jwt = JWTManager(app)
db.init_app(app)


@app.before_request
def before_request():
    if app.config['TESTING']or not app.config.get('JWT_REQUIRED', True):
        return  # 테스트 환경이거나 JWT가 필요하지 않으면 JWT 검증 건너뛰기

    if request.endpoint and request.endpoint != 'static':
        try:
            verify_jwt_in_request()
            
        except Exception as e:
           
            if request.is_json:
                return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('festival.login', _external=True)}), 401
            return render_template('auth_required.html')

@app.errorhandler(401)
@app.errorhandler(422)
def handle_auth_error(error):
   
    return render_template('auth_required.html')

# 블루프린트 등록 시 url_prefix를 제거
app.register_blueprint(festival_blueprint)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5002, debug=True)