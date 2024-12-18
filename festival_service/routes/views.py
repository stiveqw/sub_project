from flask import jsonify, request, render_template, redirect, url_for, make_response
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, create_access_token, unset_jwt_cookies
from . import festival
from models import Reservation, Festival, User, db
from datetime import datetime
from functools import wraps
from config import Config
from flask import Flask
import logging

app = Flask(__name__)
app.config.from_object(Config)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TEST_USER_ID = 99

def jwt_req_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not app.config['TESTING']:
            verify_jwt_in_request()
        else:
            verify_jwt_in_request(optional=True)
        return fn(*args, **kwargs)
    return wrapper

def get_current_user_id():
    if app.config['TESTING']:
        return TEST_USER_ID
    return get_jwt_identity()
#JWT_REQUIRED와 verify_jwt_in_request를 사용해야한다던 오류는 패키지 버전을 전부 업그레이드해서
#최신화 하는 것으로 해결
@festival.route('/')
@jwt_req_custom
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    user_id = get_current_user_id()

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
@jwt_req_custom
def apply(festival_key):
    user_id = get_current_user_id()
    festival = Festival.query.filter_by(festival_key=festival_key).first_or_404()
    # 현재 사용자의 예약 상태 확인
    reservation = Reservation.query.filter_by(festival_key=festival_key, user_id=user_id).first()
    is_reserved = reservation is not None and reservation.status == 'Reserved'
    reserved_seats = [r.seat_number for r in Reservation.query.filter_by(festival_key=festival_key, status='Reserved').all()]
    
    image = request.args.get('image', 'default.jpg')

    return render_template('festival_apply.html', 
                           festival=festival, 
                           reserved_seats=reserved_seats,
                           is_reserved=is_reserved,
                           image=image)

@festival.route('/api/apply', methods=['POST'])
@jwt_req_custom
def api_apply():
    user_id = get_current_user_id()
    data = request.json
    festival_key = data.get('festival_key')
    seat_number = data.get('seat_number')
    logger.info(f"Received application request for festival: {festival_key}, seat: {seat_number}, user: {user_id}")

    if not festival_key or not seat_number:
        logger.warning(f"Invalid request data: festival_key={festival_key}, seat_number={seat_number}")
        return jsonify({"success": False, "message": "축제 키와 좌석 번호가 필요합니다."}), 400

    festival = Festival.query.filter_by(festival_key=festival_key).first()
    if not festival:
        logger.error(f"Festival not found: {festival_key}")
        return jsonify({"success": False, "message": "해당 축제를 찾을 수 없습니다."}), 404

    if festival.capacity >= festival.total_seats:
        logger.warning(f"Festival {festival_key} is full. Capacity: {festival.capacity}/{festival.total_seats}")
        return jsonify({"success": False, "message": "축제가 이미 만석입니다."}), 400

    existing_reservation = Reservation.query.filter_by(
        festival_key=festival_key,
        seat_number=seat_number,
        status='Reserved'
    ).first()

    if existing_reservation:
        logger.warning(f"Seat {seat_number} already reserved for festival {festival_key}")
        return jsonify({"success": False, "message": "이미 예약된 좌석입니다."}), 400

    user_reservation = Reservation.query.filter_by(
        festival_key=festival_key,
        user_id=user_id,
        status='Reserved'
    ).first()

    if user_reservation:
        logger.warning(f"User {user_id} already has a reservation for festival {festival_key}")
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
        logger.info(f"Reservation successful: User {user_id}, Festival {festival_key}, Seat {seat_number}")
        return jsonify({"success": True, "message": "예약이 완료되었습니다."}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during reservation: {str(e)}")
        return jsonify({"success": False, "message": "예약 중 오류가 발생했습니다."}), 500

@festival.route('/api/cancel_reservation/<int:reservation_id>', methods=['POST'])
@jwt_req_custom
def cancel_reservation(reservation_id):
    try:
        user_id = get_current_user_id()
        reservation = Reservation.query.filter_by(id=reservation_id, user_id=user_id).first()
        
        if not reservation:
           return jsonify({"success": False, "message": "Reservation not found or not authorized"}), 404
        
        if reservation.status == 'Cancelled':
           return jsonify({"success": False, "message": "Reservation is already cancelled"}), 400
        
        festival = Festival.query.filter_by(festival_key=reservation.festival_key).first()
        if not festival:
           return jsonify({"success": False, "message": "Associated festival not found"}), 404
        reservation.status = 'Cancelled'
        if festival.capacity > 0:
            festival.capacity -= 1
        
        db.session.commit()
        return jsonify({"success": True, "message": "Reservation cancelled successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
    return jsonify({"success": False, "message": str(e)}), 500

@festival.route('/api/festivals')
@jwt_req_custom
def get_festivals():
    user_id = get_current_user_id()
    
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
@jwt_req_custom
def login():
    return redirect("http://kangyk.com/login")

@festival.route('/logout')
@jwt_req_custom
def logout():
   response = make_response(redirect('http://kangyk.com/login'))
   unset_jwt_cookies(response)
   return response


@festival.route('/redirect_to_main')
@jwt_req_custom
def redirect_to_main():
    return redirect("http://kangyk.com/main")

@festival.route('/redirect_to_news')
@jwt_req_custom
def redirect_to_news():
    return redirect("http://kangyk.com/notice")

@festival.route('/redirect_to_course')
@jwt_req_custom
def redirect_to_course():
    return redirect("http://kangyk.com/course_registration")

