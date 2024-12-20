from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.routing import BuildError
from config import Config
from models import db, User
from datetime import timedelta
from urllib.parse import urlparse
import logging

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

# JWT 설정 추가
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # 개발 환경에서는 False, 프로덕션에서는 True로 설정
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info("Login route accessed")
    if request.method == 'POST':
        logger.info("POST request received for login")
        try:
            student_id = request.form.get('student_id')
            password = request.form.get('password')
            logger.info(f"Login attempt for student_id: {student_id}")
            if not student_id or not password:
                logger.warning("Login failed: Missing student_id or password")
                return jsonify({"error": "Student ID and password are required"}), 400

            user = User.query.filter_by(student_id=student_id).first()
            logger.info(f"User found: {user is not None}")
            if user and check_password_hash(user.password_hash, password):
                logger.info(f"Login successful for student_id: {student_id}")
                access_token = create_access_token(identity=str(user.user_id))
                logger.info(f"Access token set for user: {user.user_id}")
                   # 리디렉션 URL 처리: 요청의 노드 IP를 사용하지만 포트는 30001로 설정
                parsed_url = urlparse(request.host_url)
                node_ip = parsed_url.hostname  # 현재 노드의 IP를 가져옴
                redirect_url = f"http://localhost:5003/main"

                # JWT 토큰을 쿠키에 저장
                response = make_response(jsonify({
                    'success': True,
                    'message': '로그인 성공',
                    'redirect_url': redirect_url
                }))
                set_access_cookies(response, access_token)
                if 'access_token_cookie' in response.headers.get('Set-Cookie', ''):
                    logger.info(f"Access token cookie successfully set for user: {user.user_id}")
                else:
                    logger.warning(f"Failed to set access token cookie for user: {user.user_id}")
                return response, 200
            else:
                logger.warning(f"Login failed for student_id: {student_id}")
                return jsonify({
                    'success': False,
                    'message': '잘못된 사용자 이름 또는 비밀번호입니다.'
                }), 401
        except Exception as e:
            return jsonify({"error": "로그인 처리 중 오류가 발생했습니다."}), 500
    logger.info("GET request received for login page")
    return render_template('login.html')

@app.route('/')
def home():
    return redirect(url_for('/login'))

@app.route('/redirect_to_register')
def redirect_to_register():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        department = request.form.get('department')
        name = request.form.get('name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        
        if User.query.filter_by(student_id=student_id).first():
            return jsonify({"success": False, "message": "이미 등록된 학번입니다."}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "message": "이미 등록된 이메일입니다."}), 400
        
        new_user = User(
            student_id=student_id,
            department=department,
            name=name,
            email=email,
            phone_number=phone_number,
            password_hash=generate_password_hash(password)
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"success": True, "message": "회원가입이 완료되었습니다."}), 201
        except Exception as e:
            db.session.rollback()
        return jsonify('register.html', error="이미 등록된 이메일입니다."), 500
    return render_template('register.html')

@app.errorhandler(400)
def bad_request(error):
   return jsonify({"error": "잘못된 요청입니다."}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "인증되지 않은 접근입니다."}), 401

@app.errorhandler(500)
def internal_server_error(error):
   return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)

