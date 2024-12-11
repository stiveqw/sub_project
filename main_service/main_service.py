
import os
from flask import Flask, request, redirect, url_for, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from config import Config
from routes import main as main_blueprint
from models import db


app = Flask(__name__)
app.config.from_object(Config)



# JWT 설정
jwt = JWTManager(app)
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']  # JWT 토큰 위치 설정


db.init_app(app)

app.register_blueprint(main_blueprint)

@app.route('/')
def index():
    try:
        verify_jwt_in_request()
        return redirect(url_for('main.index'))
    except Exception as e:
        return render_template('auth_required.html'), 401

@app.before_request
def before_request():
    if request.endpoint and request.endpoint not in ['static', 'main.logout']:
        try:
            verify_jwt_in_request()
        except Exception as e:
            if request.is_json:
                return jsonify({"error": "Authentication required"}), 401
            return render_template('auth_required.html'), 401

@app.errorhandler(400)
def bad_request(error):
    if request.is_json:
        return jsonify({"error": "잘못된 요청입니다."}), 400
    return render_template('error.html', error_message="잘못된 요청입니다."), 400

@app.errorhandler(401)
@app.errorhandler(422)
def handle_auth_error(error):
    if request.is_json:
        return jsonify({"error": "Authentication required"}), 401
    return render_template('auth_required.html'), 401

@app.errorhandler(404)
def not_found_error(error):
    if request.is_json:
        return jsonify({"error": "요청한 페이지를 찾을 수 없습니다."}), 404
    return render_template('error.html', error_message="요청한 페이지를 찾을 수 없습니다."), 404

@app.errorhandler(500)
def internal_error(error):
    if request.is_json:
        return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500
    return render_template('error.html', error_message="서버 내부 오류가 발생했습니다."), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)

