from flask import render_template, redirect, url_for, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies
from functools import wraps
import logging
from . import course
from models import Course, db
from sqlalchemy import desc

logger = logging.getLogger(__name__)

@course.route('/')
@jwt_required()
def index():
    try:
        verify_jwt_in_request()
        return render_template('course_service.html')
    except Exception as e:
        return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('course.login', _external=True)}), 401

@course.route('/course_registration')
@jwt_required()
def course_registration():
    return redirect(url_for('course.course_service'))

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

@course.route('/course_service')
@jwt_required()
def course_service():
    return render_template('course_service.html')

@course.route('/api/courses')
def get_courses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 3, type=int)
    
    courses = Course.query.order_by(desc(Course.created_at)).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'courses': [{
            'id': course.id,
            'course_name': course.course_name,
            'professor': course.professor,
            'max_students': course.max_students,
            'department': course.department,
            'year': course.year,
            'created_at': course.created_at.isoformat()
        } for course in courses.items],
        'total_pages': courses.pages
    })

