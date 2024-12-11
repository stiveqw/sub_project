import logging
import os
from flask import Flask, request, redirect, url_for, jsonify, render_template, send_from_directory
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from config import Config
from routes import main as main_blueprint
from models import db

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

app.config['WTF_CSRF_ENABLED'] = False  # CSRF 보호 비활성화

# JWT 설정
jwt = JWTManager(app)
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']  # JWT 토큰 위치 설정
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # CSRF 보호 비활성화 (개발 환경에서만 사용)

db.init_app(app)

app.register_blueprint(main_blueprint)

@app.route('/')
def index():
    try:
        verify_jwt_in_request()
        logger.info("Accessed main page")
        return redirect(url_for('main.index'))
    except Exception as e:
        logger.error(f"JWT verification failed: {str(e)}")
        return render_template('auth_required.html'), 401

@app.before_request
def before_request():
    if request.endpoint and request.endpoint not in ['static', 'main.logout']:
        try:
            verify_jwt_in_request()
            logger.debug(f"JWT verified for request to {request.endpoint}")
        except Exception as e:
            logger.error(f"JWT verification failed for request to {request.endpoint}: {str(e)}")
            if request.is_json:
                return jsonify({"error": "Authentication required"}), 401
            return render_template('auth_required.html'), 401

@app.errorhandler(400)
def bad_request(error):
    logger.error(f"Bad request: {str(error)}")
    if request.is_json:
        return jsonify({"error": "잘못된 요청입니다."}), 400
    return render_template('error.html', error_message="잘못된 요청입니다."), 400

@app.errorhandler(401)
@app.errorhandler(422)
def handle_auth_error(error):
    app.logger.error(f"Authentication error: {str(error)}")
    if request.is_json:
        return jsonify({"error": "Authentication required"}), 401
    return render_template('auth_required.html'), 401

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"Not found error: {str(error)}")
    if request.is_json:
        return jsonify({"error": "요청한 페이지를 찾을 수 없습니다."}), 404
    return render_template('error.html', error_message="요청한 페이지를 찾을 수 없습니다."), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {str(error)}")
    if request.is_json:
        return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500
    return render_template('error.html', error_message="서버 내부 오류가 발생했습니다."), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)

