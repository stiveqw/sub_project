from flask import render_template, redirect, url_for, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies
from functools import wraps
import logging
from . import course

logger = logging.getLogger(__name__)

@course.route('/')
@jwt_required()
def index():
    try:
        verify_jwt_in_request()
        return render_template('course_main.html')
    except Exception as e:
        return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('course.login', _external=True)}), 401

@course.route('/course_registration')
@jwt_required()
def course_registration():
    return render_template('course_registration.html')

@course.route('/redirect_to_main')
def redirect_to_main():
    return redirect('http://localhost:5003/')

@course.route('/redirect_to_festival')
def redirect_to_festival():
    return redirect('http://localhost:5002/')

@course.route('/redirect_to_news')
def redirect_to_news():
    return redirect('http://localhost:5004/news')

@course.route('/logout')
@jwt_required()
def logout():
    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    return response

@course.route('/login')
def login():
    return redirect('http://localhost:5006/login')

