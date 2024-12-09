from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, get_csrf_token, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.routing import BuildError
from config import Config
from models import db, User
from datetime import timedelta
import logging

app = Flask(__name__)
app.config.from_object(Config)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

db.init_app(app)
jwt = JWTManager(app)

# JWT 설정 추가
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # 개발 환경에서는 False, 프로덕션에서는 True로 설정
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_CSRF_IN_COOKIES'] = True
app.config['JWT_CSRF_METHODS'] = ['POST', 'PUT', 'PATCH', 'DELETE']

def generate_csrf():
    return 'test_csrf' # 실제로는 JWT에서 csrf 토큰을 생성하는 로직이 필요함.

@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.debug('Received request: %s %s', request.method, request.url)
    if request.method == 'POST':
        app.logger.debug(f"Received login request: {request.form}")
        app.logger.debug(f"Request headers: {request.headers}")
        
        try:
            name = request.form.get('username')
            password = request.form.get('password')
            
            app.logger.debug(f"Extracted username: {name}, password: {'*' * len(password) if password else 'None'}")
            
            if not name or not password:
                app.logger.error("Missing username or password")
                return jsonify({"error": "Username and password are required"}), 400
            
            app.logger.debug(f"Login attempt for user: {name}")
            user = User.query.filter_by(name=name).first()
            
            if user and check_password_hash(user.password_hash, password):
                app.logger.debug("Password check successful")
                access_token = create_access_token(identity=str(user.user_id))
                app.logger.debug("Access token created successfully")
                
                redirect_url = 'http://localhost:5003'  # 메인 서비스의 URL로 직접 리다이렉션
                app.logger.debug(f"Redirect URL: {redirect_url}")
                
                csrf_token = generate_csrf()
                response = make_response(jsonify({
                    'success': True,
                    'message': '로그인 성공',
                    'redirect_url': redirect_url,
                    'csrf_token': csrf_token  # CSRF 토큰을 응답에 포함
                }))
                set_access_cookies(response, access_token)
                
                response.set_cookie('csrf_token', csrf_token, secure=False, httponly=False, samesite='Lax', max_age=3600)
                
                app.logger.debug("Access token and CSRF token set in cookies")
                
                return response, 200
            else:
                app.logger.debug("Login failed: Invalid credentials")
                return jsonify({
                    'success': False,
                    'message': '잘못된 사용자 이름 또는 비밀번호입니다.'
                }), 401
        except Exception as e:
            app.logger.error(f"Unexpected error during login: {str(e)}")
            return jsonify({"error": "로그인 처리 중 오류가 발생했습니다."}), 500
    
    app.logger.debug('Rendering login template')
    return render_template('login.html')

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/refresh-csrf', methods=['GET'])
@jwt_required()
def refresh_csrf():
    jwt = get_jwt()
    csrf_token = get_csrf_token(jwt)
    response = jsonify({'csrf_token': csrf_token})
    response.set_cookie('csrf_access_token', csrf_token, secure=False, httponly=False, samesite='Lax', max_age=3600)
    return response

@app.errorhandler(400)
def bad_request(error):
    app.logger.error('Bad request: %s', str(error))
    return jsonify({"error": "잘못된 요청입니다."}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "인증되지 않은 접근입니다."}), 401

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Internal Server Error: %s', str(error))
    return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)

