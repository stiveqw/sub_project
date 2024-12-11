from flask import render_template, redirect, url_for, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies
from functools import wraps

from . import main
from models import db, Course, Registration, Student, Festival
from sqlalchemy import desc



def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('main.login', _external=True)}), 401
    return wrapper

@main.route('/')
@jwt_required()
def index():
    try:
        current_user_id = get_jwt_identity()
        student = Student.query.filter_by(id=current_user_id).first()
        
        # 축제 리스트 가져오기
        festivals = Festival.query.filter(Festival.capacity != Festival.total_seats)\
                            .order_by(desc(Festival.capacity))\
                            .limit(9)\
                            .all()
        
        # 수강 과목 리스트 가져오기
        if student:
            applied_courses = db.session.query(Course).join(Registration).filter(
                Registration.student_id == student.student_id,
                Registration.status == 'Applied'
            ).all()
            
            applied_courses_data = [{
                'id': course.id,
                'course_name': course.course_name,
                'professor': course.professor,
                'credits': course.credits,
                'department': course.department,
                'year': course.year
            } for course in applied_courses]
        else:
            applied_courses_data = []
        
        return render_template('index.html', 
                               username=student.name if student else 'User',
                               festivals=festivals,
                               applied_courses=applied_courses_data)
    except Exception as e:
        return "Internal Server Error", 500

@main.route('/api/festivals')
@jwt_required()
def api_festivals():
    try:
        festivals = Festival.query.filter(Festival.capacity != Festival.total_seats)\
                            .order_by(desc(Festival.capacity))\
                            .limit(9)\
                            .all()
        
        festivals_data = [festival.to_dict() for festival in festivals]
        return jsonify({"success": True, "festivals": festivals_data})
    except Exception as e:
        return jsonify({"success": False, "error": "An unexpected error occurred"}), 500

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
@jwt_required()
def logout():
    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    return response

@main.route('/login')
def login():
    return redirect('http://localhost:5006/login')

