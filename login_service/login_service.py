import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.routing import BuildError
from config import Config
from models import db, User
from datetime import timedelta

app = Flask(__name__)
app.config.from_object(Config)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

db.init_app(app)
jwt = JWTManager(app)

# JWT 설정 추가
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # True in production
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        app.logger.debug(f"Login attempt for user: {name}")
        user = User.query.filter_by(name=name).first()
        if user:
            app.logger.debug(f"User found: {user.name}")
            if check_password_hash(user.password_hash, password):
                app.logger.debug("Password check successful")
                try:
                    access_token = create_access_token(identity=str(user.user_id))
                    app.logger.debug("Access token created successfully")
                    
                    redirect_url = url_for('main_service', _external=True)
                    app.logger.debug(f"Redirect URL: {redirect_url}")
                    
                    response = make_response(jsonify({
                        'success': True,
                        'redirect_url': redirect_url
                    }))
                    set_access_cookies(response, access_token)
                    app.logger.debug("Access token set in cookies")
                    
                    return response, 200
                except Exception as e:
                    app.logger.error(f"Error during login process: {str(e)}")
                    return jsonify({
                        'success': False,
                        'message': '로그인 처리 중 오류가 발생했습니다.'
                    }), 500
            else:
                app.logger.debug("Password check failed")
        else:
            app.logger.debug("User not found")
        return jsonify({
            'success': False,
            'message': '잘못된 사용자 이름 또는 비밀번호입니다.'
        }), 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form['student_id']
        department = request.form['department']
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']
        
        if User.query.filter_by(student_id=student_id).first():
            return jsonify({"success": False, "message": "이미 등록된 학번입니다."}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "message": "이미 등록된 이메일입니다."}), 400
        
        hashed_password = generate_password_hash(password)
        new_user = User(student_id=student_id, department=department, name=name, 
                        email=email, phone_number=phone_number, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True, "message": "회원가입이 완료되었습니다."}), 201
    return render_template('register.html')

@app.route('/redirect_to_register')
def redirect_to_register():
    return redirect(url_for('register'))

@app.route('/main_service')
@jwt_required()
def main_service():
    current_user = get_jwt_identity()
    app.logger.debug(f"User {current_user} accessed main service")
    return redirect('http://localhost:5003')  # Redirect to main_service

@app.errorhandler(401)
def unauthorized(error):
    return redirect('http://localhost:5005/unauthorized')  # Redirect to error_service

@app.errorhandler(404)
def not_found(error):
    return redirect('http://localhost:5005/not_found')  # Redirect to error_service

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)

