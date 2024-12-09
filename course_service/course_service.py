from flask import Flask, request, redirect, url_for, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from config import Config
from models import db
from routes import course as course_blueprint
from extensions import socketio
import os
import logging

app = Flask(__name__)
app.config.from_object(Config)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
socketio.init_app(app, cors_allowed_origins="*")

# Register blueprints
app.register_blueprint(course_blueprint)

# JWT configuration
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # Set to True in production
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # CSRF protection disabled
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'  # Set to 'Strict' in production

@app.before_request
def before_request():
    if request.endpoint and request.endpoint != 'static':
        try:
            verify_jwt_in_request()
            logger.debug(f"JWT verified for request to {request.endpoint}")
        except Exception as e:
            logger.error(f"JWT verification failed for request to {request.endpoint}: {str(e)}")
            return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('course.login', _external=True)}), 401

@app.route('/course_registration')
def course_registration():
    logger.info(f"Accessed course registration page")
    return render_template('course_service.html')

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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    # Log registered routes
    app.logger.debug('Registered routes:')
    for rule in app.url_map.iter_rules():
        app.logger.debug(f"{rule.endpoint}: {rule.rule}")
    
    app.run(host='0.0.0.0', port=5001, debug=True)

