from flask import Flask, request, redirect, url_for, jsonify, render_template, send_from_directory, abort
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from config import Config, TestConfig
from models import db
from routes import course as course_blueprint
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
env = os.environ.get('FLASK_ENV')

if env == 'testing':
    app.config.from_object(TestConfig)
    app.config['TESTING'] = True
else:
    app.config.from_object(Config)
    app.config['TESTING'] = os.environ.get('FLASK_TESTING', 'False') == 'True'

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(course_blueprint)

# JWT configuration
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # Set to True in production
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'  # Set to 'Strict' in production
app.config['JWT_ERROR_MESSAGE_KEY'] = 'error'
app.config['JWT_EXEMPT_ROUTES'] = ['/api/dropdown_options']


@app.before_request
def before_request():
    logger.info(f"Received request: {request.method} {request.path}")
    
    if app.config['TESTING']:
        logger.debug("Testing environment detected, skipping JWT verification")
        return
    
    if not app.config.get('JWT_REQUIRED', True):
        logger.debug("JWT verification is not required, skipping")
        return
    
    if request.endpoint and request.endpoint != 'course.get_dropdown_options':
        logger.debug(f"Processing request for endpoint: {request.endpoint}")
        try:
            verify_jwt_in_request()
            logger.info("JWT verification successful")
        except Exception as e:
            logger.error(f"JWT verification failed: {str(e)}")
            if request.is_json:
                logger.info("Returning JSON response for authentication failure")
                return jsonify({
                    "error": "로그인이 필요한 서비스입니다.", 
                    "redirect": url_for('course.login', _external=True)
                }), 401
            logger.info("Rendering auth_required template")
            return render_template('auth_required.html')
    else:
        logger.debug("Skipping JWT verification for static endpoint")


@app.route('/')
def index():
    return redirect(url_for('course_registration'))

@app.route('/course_registration')
def course_registration():
    try:
        verify_jwt_in_request()
        return render_template('course_service.html')
    except Exception as e:
       return render_template('auth_required.html'), 401


@app.errorhandler(400)
def bad_request(error):
    
    return jsonify({"error": "잘못된 요청입니다."}), 400

@app.errorhandler(401)
@app.errorhandler(422)
def handle_auth_error(error):
    
    return render_template('auth_required.html'), 401

@app.errorhandler(404)
def not_found_error(error):
    
    return jsonify({"error": "요청한 페이지를 찾을 수 없습니다."}), 404

@app.errorhandler(500)
def internal_error(error):
    
    return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

