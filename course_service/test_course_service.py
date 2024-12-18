import unittest
from flask import json, url_for
from course_service import app
from models import db, Course, Student, Registration
from datetime import datetime, timedelta
from config import TestConfig
import os

# TEST_USER_ID를 views.py와 동일하게 설정
TEST_USER_ID = 99

class TestFestivalService(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config.from_object(TestConfig)
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'P*ssW0rd')}@{os.getenv('DB_HOST', 'mysql')}/{os.getenv('DB_NAME', 'course_db')}"
        self.app_context = app.app_context()
        self.client = app.test_client()
        self.app_context.push()
        db.create_all()

        # 테스트용 데이터 생성
        test_user = Student(id=TEST_USER_ID, student_id='99', name="Test User", email="test@example.com", phone_number="1234567890")
        db.session.add(test_user)
        
        test_course = Course(
            course_key = 'CS101',
            course_name = 'Introduction to Computer Science',  
            professor = 'Introduction to Test Professor',
            max_students = 50,
            current_students = 30,
            credits = 4-5,
            department = 'Introduction to Test Department',
            year = 4,
            created_at = datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(test_course)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_courses(self):
        response = self.client.get('/api/get_courses')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('courses', data)

    def test_search_courses(self):
        response = self.client.get('/api/search_courses?course_name=Introduction')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['courses']), 1)
        self.assertEqual(data['courses'][0]['course_name'], "Introduction to Computer Science")

    def test_apply_course(self):
        response = self.client.post('/api/apply_course', 
                                    data=json.dumps({'course_key': 'CS101'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], "과목 신청이 완료되었습니다.")

    def test_cancel_course(self):
        # 먼저 과목을 신청합니다
        self.client.post('/api/apply_course', 
                         data=json.dumps({'course_key': 'CS101'}),
                         content_type='application/json')

        # 이제 과목을 취소합니다
        response = self.client.post('/api/cancel_course', 
                                    data=json.dumps({'course_key': 'CS101'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], "과목 취소가 완료되었습니다.")

    def test_get_applied_courses(self):
        # 먼저 과목을 신청합니다
        self.client.post('/api/apply_course', 
                         data=json.dumps({'course_key': 'CS101'}),
                         content_type='application/json')

        # 신청한 과목 목록을 가져옵니다
        response = self.client.get('/api/get_applied_courses')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['courses']), 1)
        self.assertEqual(data['courses'][0]['course_name'], "Introduction to Computer Science")

if __name__ == '__main__':
    unittest.main()

