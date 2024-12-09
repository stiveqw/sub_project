import logging
import os
from flask import Flask, request, redirect, url_for, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity, get_csrf_token
from config import Config
from models import db
from routes import notice as notice_blueprint

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_COOKIE_CSRF_PROTECT'] = True

db.init_app(app)
jwt = JWTManager(app)

# JWT 설정 추가
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # 개발 환경에서는 False, 프로덕션에서는 True로 설정
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'  # 개발 환경에서는 'Lax', 프로덕션에서는 'Strict'로 설정

app.register_blueprint(notice_blueprint)

@app.before_request
def before_request():
    if request.endpoint and request.endpoint != 'static':
        try:
            verify_jwt_in_request()
            logger.debug(f"JWT verified for request to {request.endpoint}")
            
            # CSRF 토큰 검증 (POST, PUT, PATCH, DELETE 요청에 대해)
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                csrf_token = request.headers.get('X-CSRF-TOKEN')
                if not csrf_token or csrf_token != get_csrf_token():
                    logger.error("CSRF token verification failed")
                    return jsonify({"error": "CSRF 토큰이 유효하지 않습니다.", "code": "INVALID_CSRF"}), 400
            
        except Exception as e:
            logger.error(f"JWT verification failed for request to {request.endpoint}: {str(e)}")
            return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('notice.login', _external=True), "code": "AUTH_REQUIRED"}), 401

@app.errorhandler(400)
def bad_request(error):
    logger.error(f"Bad request: {str(error)}")
    return jsonify({"error": "잘못된 요청입니다."}), 400

@app.errorhandler(401)
def unauthorized(error):
    logger.error(f"Unauthorized access: {str(error)}")
    return jsonify({"error": "인증되지 않은 접근입니다."}), 401

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"Not found error: {str(error)}")
    return jsonify({"error": "요청한 페이지를 찾을 수 없습니다."}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {str(error)}")
    return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

@app.route('/refresh-csrf', methods=['GET'])
def refresh_csrf():
    csrf_token = get_csrf_token()
    response = jsonify({'csrf_token': csrf_token})
    response.set_cookie('csrf_access_token', csrf_token, secure=False, httponly=False, samesite='Lax')
    return response

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)

