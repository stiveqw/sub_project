
import os
from flask import Flask, request, redirect, url_for, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from config import Config
from models import db
from routes import notice as notice_blueprint



app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)
jwt = JWTManager(app)

# JWT 설정 추가
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # 개발 환경에서는 False, 프로덕션에서는 True로 설정

app.config['JWT_COOKIE_SAMESITE'] = 'Lax'  # 개발 환경에서는 'Lax', 프로덕션에서는 'Strict'로 설정

app.register_blueprint(notice_blueprint)

@app.route('/')
def index():
    try:
        verify_jwt_in_request()

        return redirect(url_for('notice.index'))
    except Exception as e:

        return render_template('auth_required.html'), 401
@app.before_request
def before_request():
    if request.endpoint and request.endpoint != 'static':
        try:
            verify_jwt_in_request()

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
    app.run(host='0.0.0.0', port=5004, debug=True)

