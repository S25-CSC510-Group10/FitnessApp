import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from application import app

class TestApplicationExtra(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_logout_route(self):
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_ajaxhistory_route(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/ajaxhistory', data={'date': '2024-01-01'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'email', response.data)  # Check if "email" key is in response

    def test_shop_route(self):
        with self.app.session_transaction() as sess:
            sess['email'] = 'testuser@example.com'
        response = self.app.get('/shop') 
        self.assertEqual(response.status_code, 200)

    def test_blog_route(self):
        response = self.app.get('/blog')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'blog', response.data.lower())  # Check if "blog" is present in response

    def test_water_route_logged_in(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/water', data={'intake': '250'})
            self.assertEqual(response.status_code, 200)

    def test_clear_intake_route(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/clear-intake')
            self.assertEqual(response.status_code, 302)
            self.assertIn('/water', response.headers['Location'])  # Ensure redirect to /water

    def test_ajaxhistory_invalid_date(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/ajaxhistory', data={'date': 'invalid-date'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'date', response.data)  # Check that date key is returned

    def test_dashboard_route_no_login(self):
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirected to login if not logged in

    def test_register_existing_user(self):
        response = self.app.post('/register', data={
            'username': 'existinguser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertEqual(response.status_code, 200)

    def test_update_user_profile(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/user_profile', data={
                'weight': '70',
                'height': '175',
                'goal': 'Fitness',
                'target_weight': '65'
            })
            self.assertEqual(response.status_code, 200)

    def test_exercise_of_the_day_route_unauthenticated(self):
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 302)

    def test_exercise_of_the_day_route(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = self.app.get('/dashboard')
            self.assertEqual(response.status_code, 200)

    def test_yoga_route_logged_out(self):
        response = self.app.get('/yoga')
        self.assertEqual(response.status_code, 302)  # Redirects if not logged in

    def test_invalid_favorite_action(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = 'testuser@example.com'
            response = client.post('/add_favorite', json={'exercise_id': '123', 'action': 'invalid_action'})
            self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
