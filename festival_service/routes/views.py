from flask import jsonify, request, render_template, redirect, url_for, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, unset_jwt_cookies
from . import festival
<<<<<<< HEAD
from models import Reservation, Festival, db


=======
from models import Reservation, Festival, User, db
from sqlalchemy import func
import logging
>>>>>>> parent of 971171e (지우기)
from datetime import datetime

logger = logging.getLogger(__name__)

@festival.route('/')
@jwt_required()
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    user_id = get_jwt_identity()

    festivals = Festival.query.order_by(Festival.date).paginate(page=page, per_page=per_page, error_out=False)
    
    reserved_festival_keys = [r.festival_key for r in Reservation.query.filter_by(user_id=user_id, status='Reserved').all()]
    
    user_reserved_festivals = db.session.query(
        Festival,
        Reservation.id.label('reservation_id'),
        Reservation.seat_number,
        Reservation.status,
        Reservation.reservation_time
    ).join(Reservation, Festival.festival_key == Reservation.festival_key
    ).filter(Reservation.user_id == user_id, Reservation.status == 'Reserved').all()

    user_reserved_festivals = [
        {
            'id': res.reservation_id,
            'festival_key': res.Festival.festival_key,
            'title': res.Festival.title,
            'seat_number': res.seat_number,
            'status': res.status,
            'reservation_time': res.reservation_time
        } for res in user_reserved_festivals
    ]

    festivals_data = []
    for festival in festivals.items:
        festival_dict = festival.to_dict()
        festival_dict['is_reserved'] = festival.festival_key in reserved_festival_keys
        festival_dict['is_full'] = festival.capacity >= festival.total_seats
        festivals_data.append(festival_dict)

    return render_template('festival_main.html', 
                           festivals=festivals_data,
                           reserved_festival_keys=reserved_festival_keys,
                           user_reserved_festivals=user_reserved_festivals)

@festival.route('/apply/<festival_key>')
@jwt_required()
def apply(festival_key):
    user_id = get_jwt_identity()
    festival = Festival.query.filter_by(festival_key=festival_key).first_or_404()
    
    # 현재 사용자의 예약 상태 확인
    reservation = Reservation.query.filter_by(festival_key=festival_key, user_id=user_id).first()
    is_reserved = reservation is not None and reservation.status == 'Reserved'

    reserved_seats = [r.seat_number for r in Reservation.query.filter_by(festival_key=festival_key, status='Reserved').all()]

    return render_template('festival_apply.html', 
                           festival=festival, 
                           reserved_seats=reserved_seats,
                           is_reserved=is_reserved)

@festival.route('/api/apply', methods=['POST'])
@jwt_required()
def api_apply():
    user_id = get_jwt_identity()
    data = request.json

    festival_key = data.get('festival_key')
    seat_number = data.get('seat_number')

    if not festival_key or not seat_number:
        return jsonify({"success": False, "message": "축제 키와 좌석 번호가 필요합니다."}), 400

    festival = Festival.query.filter_by(festival_key=festival_key).first()
    if not festival:
        return jsonify({"success": False, "message": "해당 축제를 찾을 수 없습니다."}), 404

    if festival.capacity >= festival.total_seats:
        return jsonify({"success": False, "message": "축제가 이미 만석입니다."}), 400

    existing_reservation = Reservation.query.filter_by(
        festival_key=festival_key,
        seat_number=seat_number,
        status='Reserved'
    ).first()

    if existing_reservation:
        return jsonify({"success": False, "message": "이미 예약된 좌석입니다."}), 400

    user_reservation = Reservation.query.filter_by(
        festival_key=festival_key,
        user_id=user_id,
        status='Reserved'
    ).first()

    if user_reservation:
        return jsonify({"success": False, "message": "이미 이 축제에 예약하셨습니다."}), 400

    new_reservation = Reservation(
        festival_key=festival_key,
        user_id=user_id,
        seat_number=seat_number,
        status='Reserved',
        reservation_time=datetime.utcnow()
    )

    try:
        db.session.add(new_reservation)
        festival.capacity += 1
        db.session.commit()
        return jsonify({"success": True, "message": "예약이 완료되었습니다."}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Reservation failed: {str(e)}")
        return jsonify({"success": False, "message": "예약 중 오류가 발생했습니다."}), 500

@festival.route('/api/cancel_reservation/<int:reservation_id>', methods=['POST'])
@jwt_required()
def cancel_reservation(reservation_id):
    try:
        user_id = get_jwt_identity()
        logger.info(f"Attempting to cancel reservation {reservation_id} for user {user_id}")
        
        reservation = Reservation.query.filter_by(id=reservation_id, user_id=user_id).first()
        
        if not reservation:
            logger.warning(f"Reservation {reservation_id} not found or not authorized for user {user_id}")
            return jsonify({"success": False, "message": "Reservation not found or not authorized"}), 404
        
        if reservation.status == 'Cancelled':
            logger.info(f"Reservation {reservation_id} is already cancelled")
            return jsonify({"success": False, "message": "Reservation is already cancelled"}), 400
        
        festival = Festival.query.filter_by(festival_key=reservation.festival_key).first()
        if not festival:
            logger.warning(f"Festival not found for reservation {reservation_id}")
            return jsonify({"success": False, "message": "Associated festival not found"}), 404

        reservation.status = 'Cancelled'
        if festival.capacity > 0:
            festival.capacity -= 1
        
        db.session.commit()
        
        logger.info(f"Reservation {reservation_id} cancelled successfully by user {user_id}")
        return jsonify({"success": True, "message": "Reservation cancelled successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in cancel_reservation: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@festival.route('/api/festivals')
@jwt_required()
def get_festivals():
    user_id = get_jwt_identity()
    
    festivals = Festival.query.order_by(Festival.date).all()
    reserved_festival_keys = [r.festival_key for r in Reservation.query.filter_by(user_id=user_id, status='Reserved').all()]
    
    festivals_data = []
    for festival in festivals:
        festival_dict = festival.to_dict()
        festival_dict['is_reserved'] = festival.festival_key in reserved_festival_keys
        festival_dict['is_full'] = festival.capacity >= festival.total_seats
        festivals_data.append(festival_dict)
    
    return jsonify({"success": True, "festivals": festivals_data})

@festival.route('/login')
def login():
    return redirect("http://localhost:5006/login")

@festival.route('/logout')
@jwt_required()
def logout():
    logger.info(f"Received request for {request.path}")
    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    return response


@festival.route('/redirect_to_main')
def redirect_to_main():
    return redirect("http://localhost:5003/")

@festival.route('/redirect_to_news')
def redirect_to_news():
    return redirect("http://localhost:5004/")

@festival.route('/redirect_to_course')
def redirect_to_course():
    return redirect("http://localhost:5001/")

