from flask import render_template, redirect, url_for, request, jsonify, make_response, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies
from functools import wraps
import logging
import re
from . import festival
from models import Festival, Reservation, db
from sqlalchemy import func

logger = logging.getLogger(__name__)

def parse_seat_number(seat_number):
    match = re.match(r'([A-Z])(\d+)', seat_number)
    if match:
        row, number = match.groups()
        return (ord(row) - ord('A')) * 30 + int(number)
    return None

def format_seat_number(seat_index):
    row = chr(ord('A') + (seat_index - 1) // 30)
    number = (seat_index - 1) % 30 + 1
    return f"{row}{number}"

@festival.route('/')
@jwt_required()
def home():
    try:
        verify_jwt_in_request()
        page = request.args.get('page', 1, type=int)
        per_page = 6  # 한 페이지에 표시할 축제 수
        
        # 전체 축제 수 조회
        total_festivals = Festival.query.count()
        
        # 페이지네이션 적용
        festivals = Festival.query.order_by(Festival.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        user_id = get_jwt_identity()
        reserved_festival_keys = [r.festival_key for r in Reservation.query.filter_by(user_id=user_id).all()]
        
        # 각 축제별 예약된 좌석 수 계산
        reservations = db.session.query(Reservation.festival_key, func.count(Reservation.id).label('reserved_seats')) \
            .group_by(Reservation.festival_key).all()
        reservation_dict = {r.festival_key: r.reserved_seats for r in reservations}
        
        festivals_data = [{
            'id': f.id,
            'festival_key': f.festival_key,
            'title': f.title,
            'total_seats': f.total_seats,
            'capacity': f.capacity,
            'reserved_seats': reservation_dict.get(f.festival_key, 0),  # 예약된 좌석 수, 없으면 0
            'date': f.date.isoformat(),
            'created_at': f.created_at.isoformat()
        } for f in festivals.items]
        
        # 전체 페이지 수 계산
        total_pages = (total_festivals + per_page - 1) // per_page
        
        return render_template('festival_main.html', 
                               festivals=festivals_data, 
                               page=page, 
                               total_pages=total_pages,
                               reserved_festival_keys=reserved_festival_keys)
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('festival.login', _external=True)}), 401




@festival.route('/apply/<string:festival_key>')
@jwt_required()
def apply(festival_key):
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        festival = Festival.query.filter_by(festival_key=festival_key).first_or_404()
        
        # 해당 축제에 대한 사용자의 예약 여부 확인
        is_already_reserved = Reservation.query.filter_by(user_id=user_id, festival_key=festival_key).first() is not None
        
        # 이미 예약된 좌석 목록 가져오기
        reserved_seats = [r.seat_number for r in Reservation.query.filter_by(festival_key=festival_key).all()]
        
        # 전체 예약 수 계산
        total_reservations = len(reserved_seats)
        
        return render_template('festival_apply.html', 
                               festival=festival, 
                               reserved_seats=reserved_seats,
                               total_reservations=total_reservations,
                               is_already_reserved=is_already_reserved)
    except Exception as e:
        logger.error(f"Error in apply route: {str(e)}")
        return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('festival.login', _external=True)}), 401
@festival.route('/api/apply', methods=['POST'])
@jwt_required()
def api_apply():
    user_id = get_jwt_identity()
    data = request.json
    festival_key = data.get('festival_key')
    seat_number = data.get('seat_number')

    if not festival_key or not seat_number:
        return jsonify({"success": False, "message": "Invalid request data"}), 400

    festival = Festival.query.filter_by(festival_key=festival_key).first()
    if not festival:
        return jsonify({"success": False, "message": "Festival not found"}), 404

    existing_reservation = Reservation.query.filter_by(festival_key=festival_key, seat_number=seat_number).first()
    if existing_reservation:
        return jsonify({"success": False, "message": "This seat is already reserved"}), 400

    new_reservation = Reservation(festival_key=festival_key, user_id=user_id, seat_number=seat_number)
    db.session.add(new_reservation)
    db.session.commit()

    return jsonify({"success": True, "message": "Reservation successful"})

@festival.route('/redirect_to_main')
def redirect_to_main():
    return redirect('http://localhost:5003/')

@festival.route('/redirect_to_news')
def redirect_to_news():
    return redirect('http://localhost:5004/news')

@festival.route('/redirect_to_course')
def redirect_to_course():
    return redirect('http://localhost:5001/course_registration')

@festival.route('/logout')
@jwt_required()
def logout():
    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    return response

@festival.route('/login')
def login():
    return redirect('http://localhost:5006/login')