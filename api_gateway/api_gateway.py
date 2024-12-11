import logging
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, redirect, send_from_directory
from flask_cors import CORS
import requests
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request, get_csrf_token
from config import Config

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# CORS 설정
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"], "supports_credentials": True}})

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# JWT 설정
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_COOKIE_SECURE'] = True  # HTTPS를 사용하는 경우에만 True로 설정
app.config['JWT_COOKIE_SAMESITE'] = 'Strict'
jwt = JWTManager(app)

SERVICES = {
    'login': os.getenv('LOGIN_SERVICE_URL', 'http://localhost:5006'),
    'course': os.getenv('COURSE_SERVICE_URL', 'http://localhost:5001'),
    'festival': os.getenv('FESTIVAL_SERVICE_URL', 'http://localhost:5002'),
    'notice': os.getenv('NOTICE_SERVICE_URL', 'http://localhost:5004'),
    'main': os.getenv('MAIN_SERVICE_URL', 'http://localhost:5003')
}

@app.before_request
def before_request():
    if request.endpoint and request.endpoint not in ['static', 'favicon']:
        try:
            verify_jwt_in_request()
            logger.debug(f"JWT verified for request to {request.endpoint}")
            
            # CSRF 토큰 검증 (POST, PUT, PATCH, DELETE 요청에 대해)
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                csrf_token = request.headers.get('X-CSRF-TOKEN')
                if not csrf_token or csrf_token != get_csrf_token():
                    logger.error("CSRF token verification failed")
                    return jsonify({"error": "CSRF 토큰이 유효하지 않습니다."}), 400
        except Exception as e:
            logger.error(f"JWT verification failed for request to {request.endpoint}: {str(e)}")
            return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": SERVICES['login'] + '/login'}), 401

@app.route('/')
def index():
    try:
        verify_jwt_in_request()
        logger.debug("JWT verified, redirecting to main service")
        return redirect(SERVICES['main'])
    except:
        logger.debug("JWT verification failed, redirecting to login")
        return redirect(SERVICES['login'] + '/login')

@app.route('/<service>/', defaults={'path': ''})
@app.route('/<service>/<path:path>')
def proxy(service, path):
    if service not in SERVICES:
        return jsonify({"error": "Service not found"}), 404

    if service not in ['login']:
        try:
            verify_jwt_in_request()
            logger.debug(f"JWT verified for service: {service}")
        except:
            logger.debug(f"JWT verification failed for service: {service}")
            return redirect(SERVICES['login'] + '/login')

    url = f"{SERVICES[service]}/{path}"
    logger.debug(f"Proxying request to: {url}")
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = app.response_class(resp.content, resp.status_code, headers)
    return response

@app.errorhandler(401)
@app.errorhandler(422)
def unauthorized(error):
    logger.error(f"Unauthorized access: {str(error)}")
    return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": SERVICES['login'] + '/login'}), 401

@app.errorhandler(400)
def handle_csrf_error(error):
    logger.error(f"CSRF error: {str(error)}")
    return jsonify({"error": "CSRF 토큰이 유효하지 않습니다."}), 400

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"Not found error: {str(error)}")
    return jsonify({"error": "요청한 리소스를 찾을 수 없습니다."}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {str(error)}")
    return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/refresh-csrf', methods=['GET'])
@jwt_required()
def refresh_csrf():
    csrf_token = get_csrf_token()
    response = jsonify({'csrf_token': csrf_token})
    response.set_cookie('csrf_access_token', csrf_token, secure=True, httponly=True, samesite='Strict')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

