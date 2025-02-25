import unittest
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from application import app, mongo
from flask import session, url_for


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "secret"
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_user():
    return {
        "email": "test@user.com",
        "name": "Test User",
        "password": "supersecurepassword",
    }


@pytest.fixture
def mock_exercise():
    return {
        "exercise_id": "1",
        "email": "email",
        "name": "Yoga for Beginners",
        "href": "yoga",
        "image": "../static/img/yoga.jpg",
        "video_link": "https://www.youtube.com/watch?v=c8hjhRqIwHE",
        "description": "New to Yoga? You are at the right place! Learn easy yoga poses to buil…",
    }


class TestApplicationExtra(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_logout_route(self):
        response = self.app.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_ajaxhistory_route(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.post("/ajaxhistory", data={"date": "2024-01-01"})
            self.assertEqual(response.status_code, 200)
            self.assertIn(
                b"email", response.data
            )  # Check if "email" key is in response

    def test_shop_route(self):
        with self.app.session_transaction() as sess:
            sess["email"] = "testuser@example.com"
        response = self.app.get("/shop")
        self.assertEqual(response.status_code, 200)

    def test_blog_route(self):
        response = self.app.get("/blog")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"blog", response.data.lower()
        )  # Check if "blog" is present in response

    def test_water_route_logged_in(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.post("/water", data={"intake": "250"})
            self.assertEqual(response.status_code, 200)

    def test_clear_intake_route(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.post("/clear-intake")
            self.assertEqual(response.status_code, 302)
            self.assertIn(
                "/water", response.headers["Location"]
            )  # Ensure redirect to /water

    def test_ajaxhistory_invalid_date(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.post("/ajaxhistory", data={"date": "invalid-date"})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"date", response.data)  # Check that date key is returned

    def test_dashboard_route_no_login(self):
        response = self.app.get("/dashboard")
        self.assertEqual(
            response.status_code, 302
        )  # Redirected to login if not logged in

    def test_register_existing_user(self):
        response = self.app.post(
            "/register",
            data={
                "username": "existinguser",
                "email": "testuser@example.com",
                "password": "password123",
                "confirm_password": "password123",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_update_user_profile(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.post(
                "/user_profile",
                data={
                    "weight": "70",
                    "height": "175",
                    "goal": "Fitness",
                    "target_weight": "65",
                },
            )
            self.assertEqual(response.status_code, 200)

    def test_exercise_of_the_day_route_unauthenticated(self):
        response = self.app.get("/dashboard")
        self.assertEqual(response.status_code, 302)

    def test_exercise_of_the_day_route(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = self.app.get("/dashboard")
            self.assertEqual(response.status_code, 200)

    def test_yoga_route_logged_out(self):
        response = self.app.get("/yoga")
        self.assertEqual(response.status_code, 302)  # Redirects if not logged in

    # TESTING BURNBOT

    # TESTING ADD_FAVORITE


# return 401 if email not in db
def test_add_favorite_unauthenticated(client):
    response = client.post("/add_favorite", data={"activity": "yoga", "action": "add"})
    assert response.status_code == 401
    assert b"User not logged in" in response.data


# return 400 if action not in form
def test_add_favorite_missing_action(client, mock_user, mock_exercise):
    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/add_favorite", data={"activity": mock_exercise["href"]})
    assert response.status_code == 400
    assert b"Favorite action is required" in response.data


# return 400 if activity not in form
def test_add_favorite_missing_activity(client, mock_user):
    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/add_favorite", data={"action": "add"})
    assert response.status_code == 400
    assert b"Exercise ID is required" in response.data


# return 400 if exercise corresonding to activity not found in db
def test_add_favorite_exercise_not_found(client, monkeypatch, mock_user, mock_exercise):
    def mock_find_one(query):
        return None  # Simulate exercise not found

    monkeypatch.setattr(mongo.db.your_exercise_collection, "find_one", mock_find_one)

    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post(
        "/add_favorite", data={"activity": mock_exercise["href"], "action": "add"}
    )
    assert response.status_code == 404
    assert b"Exercise not found" in response.data


# confirm nothing changes if we favorite exercise already in favorited
def test_add_favorite_already_favorited(client, monkeypatch, mock_user, mock_exercise):
    def mock_find_one(query):
        if "href" in query:
            return mock_exercise  # Found exercise
        return {
            "email": mock_user["email"],
            "href": mock_exercise["href"],
        }  # Already favorited

    monkeypatch.setattr(mongo.db.your_exercise_collection, "find_one", mock_find_one)
    monkeypatch.setattr(mongo.db.favorites, "find_one", mock_find_one)

    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post(
        "/add_favorite", data={"activity": mock_exercise["href"], "action": "add"}
    )
    assert response.status_code == 302  # Redirect after no change


# confirm favorite with a non-favorited exercise
def test_add_favorite_new_exercise(client, monkeypatch, mock_user, mock_exercise):
    def mock_find_one(query):
        if "href" in query:
            return mock_exercise  # Found exercise
        return None  # Not yet favorited

    def mock_insert_one(data):
        return None  # Simulate successful insert

    monkeypatch.setattr(mongo.db.your_exercise_collection, "find_one", mock_find_one)
    monkeypatch.setattr(mongo.db.favorites, "find_one", lambda q: None)
    monkeypatch.setattr(mongo.db.favorites, "insert_one", mock_insert_one)

    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post(
        "/add_favorite", data={"activity": mock_exercise["href"], "action": "add"}
    )
    assert response.status_code == 302  # Redirect after success


# confirm unfavorite
def test_unfavorite_exercise(client, monkeypatch, mock_user, mock_exercise):
    def mock_find_one(query):
        if "href" in query:
            return mock_exercise  # Found exercise
        return {
            "email": mock_user["email"],
            "href": mock_exercise["href"],
        }  # Found favorite

    def mock_delete_one(query):
        return None  # Simulate delete success

    monkeypatch.setattr(mongo.db.your_exercise_collection, "find_one", mock_find_one)
    monkeypatch.setattr(mongo.db.favorites, "find_one", mock_find_one)
    monkeypatch.setattr(mongo.db.favorites, "delete_one", mock_delete_one)

    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post(
        "/add_favorite", data={"activity": mock_exercise["href"], "action": "remove"}
    )
    assert response.status_code == 302  # Redirect after success

# potential

# test unfavorite invalid exercise etc.

if __name__ == "__main__":
    unittest.main()
