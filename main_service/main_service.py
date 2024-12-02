import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies
from config import Config
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# JWT 설정 추가
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            logger.debug("JWT verified successfully")
        except Exception as e:
            logger.error(f"JWT verification failed: {str(e)}")
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper

@app.route('/')
@jwt_required_custom
def index():
    try:
        current_user = get_jwt_identity()
        logger.info(f"User {current_user} accessed the main page")
        return render_template('index.html', username=current_user)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return "Internal Server Error", 500

@app.route('/home')
@jwt_required_custom
def home():
    return redirect(url_for('index'))

@app.route('/festival')
@jwt_required_custom
def festival():
    return redirect('http://localhost:5002/')  # festival_service의 주소로 리다이렉트

@app.route('/news')
@jwt_required_custom
def news():
    return redirect('http://localhost:5004/news')  # notice_service의 news 페이지로 리다이렉트

@app.route('/course_registration')
@jwt_required_custom
def course_registration():
    # 수강신청 페이지 로직 구현
    return "Course Registration Page"



@app.route('/logout', methods=['GET', 'POST'])
@jwt_required_custom
def logout():
    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    logger.info("User logged out and JWT cookies unset")
    return response

@app.before_request
def before_request():
    if request.endpoint and request.endpoint != 'static':
        try:
            verify_jwt_in_request()
            logger.debug(f"JWT verified for request to {request.endpoint}")
        except Exception as e:
            logger.error(f"JWT verification failed for request to {request.endpoint}: {str(e)}")
            return redirect(url_for('login'))

@app.errorhandler(401)
@app.errorhandler(422)
def handle_auth_error(error):
    logger.error(f"Authentication error: {str(error)}")
    return redirect(url_for('login'))

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {str(error)}")
    return "Internal Server Error", 500

@app.route('/api/user_info')
@jwt_required_custom
def user_info():
    current_user = get_jwt_identity()
    logger.info(f"User info requested for user {current_user}")
    # 여기에 사용자 정보를 가져오는 로직을 추가하세요
    return jsonify({"user_id": current_user, "username": "Example User"})


@app.route('/test')
def test():
    return "Main service is running", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)

