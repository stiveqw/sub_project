import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from flask import Flask, request, redirect, url_for, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from config import Config
from models import db
from routes import notice as notice_blueprint

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(notice_blueprint)

@app.before_request
def before_request():
    if request.endpoint and request.endpoint != 'static':
        try:
            verify_jwt_in_request()
            logger.debug(f"JWT verified for request to {request.endpoint}")
        except Exception as e:
            logger.error(f"JWT verification failed for request to {request.endpoint}: {str(e)}")
            if request.is_json:
                return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('notice.login', _external=True)}), 401
            return render_template('auth_required.html')

@app.errorhandler(401)
@app.errorhandler(422)
def handle_auth_error(error):
    logger.error(f"Authentication error: {str(error)}")
    return render_template('auth_required.html')

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {str(error)}")
    return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)

