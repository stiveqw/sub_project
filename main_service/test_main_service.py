import unittest
from flask import url_for
from main_service import app

class TestMainService(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_home_redirect(self):
        response = self.app.get('/')
        if app.config['TESTING']:
            self.assertEqual(response.status_code, 200)  # Expecting successful response in testing mode
        else:
            self.assertEqual(response.status_code, 302)

    def test_course_registration_redirect(self):
        response = self.app.get('/course_registration')
        self.assertEqual(response.status_code, 302)
        self.assertIn('course-service.course-service.svc.cluster.local/course_registration', response.location)

    def test_festival_redirect(self):
        response = self.app.get('/festival')
        self.assertEqual(response.status_code, 302)
        self.assertIn('festival-service.festival-service.svc.cluster.local/', response.location)

    def test_news_redirect(self):
        response = self.app.get('/news')
        self.assertEqual(response.status_code, 302)
        self.assertIn('notice-service.notice-service.svc.cluster.local/news', response.location)

    def test_logout_redirect(self):
        response = self.app.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertIn('main-service.main-service.svc.cluster.local/main', response.location)

    def test_api_festivals(self):
        response = self.app.get('/api/festivals')
        if app.config['TESTING']:
            self.assertEqual(response.status_code, 200)  # Expecting successful response in testing mode
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertEqual(len(data['festivals']), 1)
            self.assertEqual(data['festivals'][0]['name'], 'Test Festival')
        else:
            self.assertEqual(response.status_code, 401)  # Failing without JWT in non-testing mode

if __name__ == '__main__':
    unittest.main()
