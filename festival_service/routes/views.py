from flask import render_template, redirect, url_for, request, jsonify, make_response
from flask_jwt_extended import jwt_required, verify_jwt_in_request, unset_jwt_cookies
from . import festival
from models import Festival, db
from math import ceil

ITEMS_PER_PAGE = 3

@festival.route('/')
@jwt_required()
def home():
    try:
        verify_jwt_in_request()
        page = request.args.get('page', 1, type=int)
        festivals = Festival.query.paginate(page=page, per_page=ITEMS_PER_PAGE, error_out=False)
        total_pages = ceil(festivals.total / ITEMS_PER_PAGE)
        return render_template('festival_main.html', festivals=festivals.items, page=page, total_pages=total_pages)
    except Exception as e:
        return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('festival.login', _external=True)}), 401

@festival.route('/apply/<int:festival_id>')
@jwt_required()
def apply(festival_id):
    festival = Festival.query.get_or_404(festival_id)
    return render_template('festival_apply.html', festival=festival)

@festival.route('/api/festival/<int:festival_id>')
@jwt_required()
def get_festival(festival_id):
    festival = Festival.query.get_or_404(festival_id)
    return jsonify(festival.to_dict())

@festival.route('/api/apply', methods=['POST'])
@jwt_required()
def api_apply():
    data = request.json
    festival_id = data.get('festival_id')
    seat_number = data.get('seat_number')
    
    festival = Festival.query.get_or_404(festival_id)
    if festival.capacity <= 0:
        return jsonify({"success": False, "message": "축제 신청이 마감되었습니다."}), 400
    
    # 여기에 실제 예약 로직 추가
    festival.capacity -= 1
    db.session.commit()
    
    return jsonify({"success": True, "message": "축제 신청이 완료되었습니다."}), 200

@festival.route('/logout', methods=['GET', 'POST'])
@jwt_required()
def logout():
    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    return response

@festival.route('/redirect_to_main')
def redirect_to_main():
    return redirect('http://localhost:5003')

@festival.route('/redirect_to_news')
def redirect_to_news():
    return redirect('http://localhost:5004/news')

@festival.route('/redirect_to_course')
def redirect_to_course():
    return redirect('http://localhost:5001/course_registration')

@festival.route('/login')
def login():
    return redirect('http://localhost:5006/login')

