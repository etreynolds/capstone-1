from app import app, convert
from flask import session
from unittest import TestCase


class AppFuncTestCase(TestCase):
    """Testing time convert func."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_convert(self):
        self.assertEqual(convert(120), "2h 0m")
        self.assertEqual(convert(130), "2h 10m")


class AppViewsTestCase(TestCase):
    """Testing flask routes."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertIn('<a href="/signup">/signup</a>', html)

    def test_signup(self):
        user = {'name': 'test', 'email': 'email@test.com',
                'username': 'test', 'password': 'testing'}

        with app.test_client() as client:
            res = client.post('/signup', data=user)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)


class SessionTestCase(TestCase):
    """Testing the session."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_session_count(self):
        with app.test_client() as client:
            resp = client.get("/")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(session['count'], 1)
