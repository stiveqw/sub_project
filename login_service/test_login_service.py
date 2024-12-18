import unittest
import os
import time
from login_service import app, db
from models import User
from werkzeug.security import generate_password_hash
from faker import Faker
from sqlalchemy.exc import OperationalError

class LoginServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'mysql')}@{os.getenv('DB_HOST', 'mysql')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'user_db')}"
        self.client = app.test_client()

        self._wait_for_mysql()

        with app.app_context():
            fake_student_id = str(self.fake.random_number(digits=8))
            fake_password = 'password'

            self.test_user = User(
                student_id=fake_student_id,
                department=self.fake.word(),
                name=self.fake.name(),
                email=self.fake.email(),
                phone_number='010-1234-1234',
                password_hash=generate_password_hash(fake_password)
            )
            db.session.add(self.test_user)
            db.session.commit()

            self.test_user_id = self.test_user.user_id
            self.test_password = fake_password

    def _wait_for_mysql(self):
        retries = 30
        while retries > 0:
            try:
                with app.app_context():
                    db.engine.connect()
                return
            except OperationalError:
                retries -= 1
                time.sleep(2)
        raise Exception("MySQL not available after retries")

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            user = User.query.get(self.test_user_id)
            if user:
                db.session.delete(user)
                db.session.commit()

    def test_login(self):
        with app.app_context():
            user = User.query.get(self.test_user_id)
            if not user:
                self.fail("Test user not found in the database.")

        response = self.client.post('/login', data=dict(
            student_id=self.test_user.student_id,
            password=self.test_password
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)

    def test_register(self):
        email_local = self.fake.word()
        email_domain = "example"
        email_tld = "com"
        full_email = f"{email_local}@{email_domain}.{email_tld}"

        phone1 = "010"
        phone2 = "1234"
        phone3 = "5678"
        full_phone_number = f"{phone1}-{phone2}-{phone3}"

        response = self.client.post('/register', data=dict(
            student_id=str(self.fake.random_number(digits=8)),
            department=self.fake.word(),
            name=self.fake.name(),
            email=full_email,
            phone_number=full_phone_number,
            password='newpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 201)
        self.assertIn(b'success', response.data)

if __name__ == '__main__':
    unittest.main()