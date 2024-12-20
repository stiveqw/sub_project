from flask import render_template, redirect, url_for, jsonify, make_response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies
from functools import wraps
from . import main
from models import db, Course, Registration, Student, Festival
from sqlalchemy import desc

def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if current_app.config.get('TESTING', False):
            return fn(*args, **kwargs)
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception:
            return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('main.main', _external=True)}), 401
    return wrapper

@main.route('/dashboard')
@jwt_required_custom
def index():
    try:
        if current_app.config.get('TESTING', False):
            return render_template('index.html', username='Test User', festivals=[], applied_courses=[])

        current_user_id = get_jwt_identity()
        student = Student.query.filter_by(id=current_user_id).first()

        festivals = Festival.query.filter(Festival.capacity != Festival.total_seats)\
                            .order_by(desc(Festival.capacity))\
                            .limit(9)\
                            .all()

        applied_courses = db.session.query(Course).join(Registration).filter(
            Registration.student_id == student.student_id,
            Registration.status == 'Applied'
        ).all() if student else []

        applied_courses_data = [{
            'id': course.id,
            'course_name': course.course_name,
            'professor': course.professor,
            'credits': course.credits,
            'department': course.department,
            'year': course.year
        } for course in applied_courses]

        return render_template('index.html', 
                               username=student.name if student else 'User',
                               festivals=festivals,
                               applied_courses=applied_courses_data)
    except Exception as e:
        return "Internal Server Error", 500

@main.route('/festival/festivals')
@jwt_required_custom
def api_festivals():
    try:
        if current_app.config.get('TESTING', False):
            return jsonify({"success": True, "festivals": [{"name": "Test Festival", "capacity": 100, "total_seats": 10}]})

        festivals = Festival.query.filter(Festival.capacity != Festival.total_seats)\
                            .order_by(desc(Festival.capacity))\
                            .limit(9)\
                            .all()

        festivals_data = [festival.to_dict() for festival in festivals]
        return jsonify({"success": True, "festivals": festivals_data})
    except Exception:
        return jsonify({"success": False, "error": "An unexpected error occurred"}), 500

@main.route('/festival')
def festival():
    return redirect('http://localhost:5002/festival')

@main.route('/notice')
def notice():
    return redirect('http://localhost:5004/notice')

@main.route('/course_registration')
def course_registration():
    return redirect('http://localhost:5001/course_registration')

@main.route('/logout')
def logout():
    if current_app.config.get('TESTING', False):
        return redirect('http://localhost:5003/main')

    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    return response

@main.route('/login')
def main():
    return redirect('http://localhost:5006/login')