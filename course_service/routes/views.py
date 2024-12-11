from flask import render_template, redirect, url_for, request, jsonify, make_response
from flask_jwt_extended import jwt_required, unset_jwt_cookies, get_jwt_identity
from werkzeug.exceptions import Unauthorized, UnprocessableEntity
from . import course

from models import db, Course, Registration, Student
from sqlalchemy.exc import SQLAlchemyError







@course.route('/api/get_courses', methods=['GET'])
@jwt_required()
def get_courses():
    
    try:
        # Return empty list for courses
        courses_data = []


        # 현재 사용자의 ID 가져오기
        current_user_id = get_jwt_identity()
        
        # 현재 사용자의 신청한 과목 정보 가져오기
        student = Student.query.filter_by(id=current_user_id).first()
        if student:
            applied_courses = db.session.query(Course).join(Registration).filter(
                Registration.student_id == student.student_id,
                Registration.status == 'Applied'
            ).all()
            
            applied_courses_data = [{
                'id': course.id,
                'course_key': course.course_key,
                'course_name': course.course_name,
                'professor': course.professor,
                'credits': course.credits,
                'department': course.department,
                'year': course.year
            } for course in applied_courses]
        else:
            applied_courses_data = []
        
        return jsonify({
            "success": True, 
            "courses": courses_data,
            "appliedCourses": applied_courses_data
        }), 200
    except Exception as e:
        
        return jsonify({"success": False, "message": "An error occurred while fetching courses"}), 500

@course.route('/course_registration')
@jwt_required()
def course_service():

    return render_template('course_service.html')

@course.route('/api/dropdown_options', methods=['GET'])
@jwt_required()
def get_dropdown_options():
    
    try:
        credits = db.session.query(Course.credits).distinct().order_by(Course.credits).all()
        departments = db.session.query(Course.department).distinct().order_by(Course.department).all()
        
        return jsonify({
            "success": True,
            "credits": [credit[0] for credit in credits],
            "departments": [dept[0] for dept in departments if dept[0]]  # None 값 제외
        }), 200
    except Exception as e:
       
        return jsonify({"success": False, "message": "An error occurred while fetching dropdown options"}), 500

@course.route('/api/credits')
@jwt_required()
def get_credits():
    
    return redirect(url_for('course.get_dropdown_options'))

@course.route('/api/departments')
@jwt_required()
def get_departments():
    
    return redirect(url_for('course.get_dropdown_options'))



@course.route('/api/search_courses')
@jwt_required()
def search_courses():
    
    try:
        credits = request.args.get('credits')
        department = request.args.get('department')
        course_name = request.args.get('course_name')

        query = Course.query

        if credits and credits != 'Select Credits':
            query = query.filter(Course.credits == int(credits))
        if department and department != 'Select Department':
            query = query.filter(Course.department == department)
        if course_name:
            query = query.filter(Course.course_name.ilike(f'%{course_name}%'))

        courses = query.all()
        courses_list = [{
            'id': course.id,
            'course_key': course.course_key,
            'course_name': course.course_name,
            'professor': course.professor,
            'max_students': course.max_students,
            'current_students': course.current_students,
            'credits': course.credits,
            'department': course.department,
            'year': course.year,
            'created_at': course.created_at.isoformat() if course.created_at else None
        } for course in courses]
        
        return jsonify({'success': True, 'courses': courses_list})
    except Exception as e:
       
        return jsonify({"success": False, "message": "An error occurred while searching courses"}), 500

@course.route('/api/apply_course', methods=['POST'])
@jwt_required()
def apply_course():
    data = request.get_json()
    course_key = data.get('course_key')
    user_id = get_jwt_identity()  # This gets the user.id from JWT

  

    try:
        # Get the student record using id (which is equivalent to user_id)
        student = Student.query.filter_by(id=user_id).first()
        if not student:
            
            return jsonify({"success": False, "message": "학생 정보를 찾을 수 없습니다."}), 404

        student_id = student.student_id  # Get the actual student_id
        
        course = Course.query.filter_by(course_key=course_key).first()
        if not course:
            
            return jsonify({"success": False, "message": "과목을 찾을 수 없습니다."}), 404

        if course.current_students >= course.max_students:
           
            return jsonify({"success": False, "message": "수강 인원이 꽉 찼습니다."}), 400

        existing_registration = Registration.query.filter_by(
            course_key=course_key, 
            student_id=student_id
        ).first()
        
        if existing_registration:
            if existing_registration.status == 'Applied':
                
                return jsonify({"success": False, "message": "이미 신청한 과목입니다."}), 400
            elif existing_registration.status == 'Cancelled':
                # Update the existing registration to 'Applied'
                existing_registration.status = 'Applied'
                db.session.add(existing_registration)
            else:
                
                return jsonify({"success": False, "message": "알 수 없는 등록 상태입니다."}), 500
        else:
            # Create a new registration
            new_registration = Registration(course_key=course_key, student_id=student_id, status='Applied')
            db.session.add(new_registration)
        
        # Increment current_students
        course.current_students += 1
        
        db.session.commit()
       
        return jsonify({"success": True, "message": "과목 신청이 완료되었습니다."}), 200
    except Exception as e:
        db.session.rollback()
       
        return jsonify({"success": False, "message": str(e)}), 500

@course.route('/api/cancel_course', methods=['POST'])
@jwt_required()
def cancel_course():
    data = request.get_json()
    course_key = data.get('course_key')
    user_id = get_jwt_identity()

    try:
        # Get the student record using id (which is equivalent to user_id)
        student = Student.query.filter_by(id=user_id).first()
        if not student:
            return jsonify({"success": False, "message": "학생 정보를 찾을 수 없습니다."}), 404

        student_id = student.student_id  # Get the actual student_id

        registration = Registration.query.filter_by(
            course_key=course_key, 
            student_id=student_id
        ).first()
        
        if not registration:
            return jsonify({"success": False, "message": "신청 내역을 찾을 수 없습니다."}), 404

        course = Course.query.filter_by(course_key=course_key).first()
        if not course:
            return jsonify({"success": False, "message": "과목을 찾을 수 없습니다."}), 404

        db.session.delete(registration)
        
        # Decrement current_students
        course.current_students = max(0, course.current_students - 1)
        
        db.session.commit()
        return jsonify({"success": True, "message": "과목 취소가 완료되었습니다."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@course.route('/api/get_applied_courses', methods=['GET'])
@jwt_required()
def get_applied_courses():
   
    try:
        user_id = get_jwt_identity()
        
        student = Student.query.filter_by(id=user_id).first()
        if not student:
            return jsonify({"success": False, "message": "Student not found"}), 404

        applied_courses = db.session.query(Course).join(Registration).filter(
            Registration.student_id == student.student_id,
            Registration.status == 'Applied'
        ).all()

        courses_data = [{
            'id': course.id,
            'course_name': course.course_name,
            'professor': course.professor,
            'credits': course.credits,
            'department': course.department,
            'year': course.year
        } for course in applied_courses]

        return jsonify({"success": True, "courses": courses_data}), 200

    except SQLAlchemyError as e:
        return jsonify({"success": False, "message": "Database error occurred"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

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

