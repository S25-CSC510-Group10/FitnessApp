import unittest
import sys
import os
from app import app

# Global valid data variable for registration user
data = {
            'username': 'TestUser',
            'email': 'testEmail@example.com',
            'password': 'Testpwd!', # Length: 8; UpperCase: Y, Special Char: Y
            'confirm_password': 'Testpwd!',
            'weight': '70',
            'height': '180',
            'goal': 'Lose weight',
            'target_weight': '65'
        }

class TestApplicationS23(unittest.TestCase):

    # Ensure proper setup of client and application
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Test page load
    def test_registration_page_load(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Join Today', response.data)
        self.assertIn(b'Sign Up', response.data)

    # Test valid registration
    def test_valid_registration(self):
        response = self.app.post('/register', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Success', response.data)


if __name__ == '__main__':
    unittest.main()