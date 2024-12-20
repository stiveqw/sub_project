import unittest
from flask import url_for
from festival_service import app, db
from models import Festival, User, Reservation
from datetime import datetime, timedelta
import json
from config import TestConfig
import os

# TEST_USER_ID를 views.py와 동일하게 설정
TEST_USER_ID = 99

class TestFestivalService(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config.from_object(TestConfig)
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'mysql')}@{os.getenv('DB_HOST', 'mysql')}/{os.getenv('DB_NAME', 'festival_db')}"
        self.app_context = app.app_context()
        self.client = app.test_client()
        self.app_context.push()
        db.create_all()

        # 테스트용 데이터 생성
        test_user = User(user_id=TEST_USER_ID, name="Test User", email="test@example.com", phone_number="1234567890")
        db.session.add(test_user)
        
        test_festival = Festival(
            festival_key="test_festival",
            title="Test Festival",
            total_seats=100,
            capacity=0,
            date=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(test_festival)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/festival')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Festival', response.data)

    def test_apply_page(self):
        response = self.client.get('/festival/apply/test_festival')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Festival', response.data)

    def test_api_apply(self):
        data = {
            'festival_key': 'test_festival',
            'seat_number': 'A1'
        }
        response = self.client.post('/festival/apply', 
                                    data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])

    def test_api_cancel_reservation(self):
        # 먼저 예약을 생성합니다
        user = User.query.filter_by(email="test@example.com").first()
        festival = Festival.query.filter_by(festival_key="test_festival").first()
        reservation = Reservation(
            festival_key=festival.festival_key,
            user_id=user.user_id,
            seat_number='A1',
            status='Reserved'
        )
        db.session.add(reservation)
        db.session.commit()

        response = self.client.post(f'/festival/cancel_reservation/{reservation.id}')
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])

    def test_api_festivals(self):
        response = self.client.get('/festival/festivals')
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])
        self.assertEqual(len(json_data['festivals']), 1)

if __name__ == '__main__':
    unittest.main()