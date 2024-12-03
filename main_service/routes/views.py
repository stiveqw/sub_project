from flask import render_template, redirect, url_for, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies
from functools import wraps
import logging
from . import main

logger = logging.getLogger(__name__)

def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            logger.debug("JWT verified successfully")
            return fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"JWT verification failed: {str(e)}")
            return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('main.login', _external=True)}), 401
    return wrapper

@main.route('/')
@jwt_required_custom
def index():
    try:
        current_user = get_jwt_identity()
        logger.info(f"User {current_user} accessed the main page")
        return render_template('index.html', username=current_user)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return "Internal Server Error", 500

@main.route('/festival')
@jwt_required_custom
def festival():
    return redirect('http://localhost:5002/')

@main.route('/news')
@jwt_required_custom
def news():
    return redirect('http://localhost:5004/news')

@main.route('/course_registration')
@jwt_required_custom
def course_registration():
    return redirect('http://localhost:5001/course_registration')

@main.route('/logout')
@jwt_required_custom
def logout():
    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    return response

@main.route('/login')
def login():
    return redirect('http://localhost:5006/login')

