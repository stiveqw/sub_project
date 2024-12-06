from flask import Flask, request, jsonify, render_template, url_for
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from config import Config
from models import db
from routes import festival as festival_blueprint

app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

db.init_app(app)
jwt = JWTManager(app)

@app.before_request
def before_request():
    if request.endpoint and request.endpoint != 'static':
        try:
            verify_jwt_in_request()
            app.logger.debug(f"JWT verified for request to {request.endpoint}")
        except Exception as e:
            app.logger.error(f"JWT verification failed for request to {request.endpoint}: {str(e)}")
            if request.is_json:
                return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('festival.login', _external=True)}), 401
            return render_template('auth_required.html')

@app.errorhandler(401)
@app.errorhandler(422)
def handle_auth_error(error):
    app.logger.error(f"Authentication error: {str(error)}")
    return render_template('auth_required.html')

# 블루프린트 등록 시 url_prefix를 제거
app.register_blueprint(festival_blueprint)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5002, debug=True)

