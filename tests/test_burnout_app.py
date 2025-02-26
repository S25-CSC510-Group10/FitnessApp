import unittest
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from application import app, mongo, bot_response, get_calories
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

<<<<<<< HEAD
from application import app
=======
>>>>>>> 86deb4da4f4988b35479c795d28d53298d94140b

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


# --------------------------------------->
# --------- TESTING ADD_FAVORITE -------->
# --------------------------------------->
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
        "/add_favorite", data={"activity": "fake-exercise", "action": "add"}
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
    assert response.status_code == 302


# confirm removing a favorite that doesn’t exist
def test_remove_nonexistent_favorite(client, monkeypatch, mock_user, mock_exercise):
    def mock_find_one(query):
        return None  # No favorite found

    monkeypatch.setattr(mongo.db.favorites, "find_one", mock_find_one)

    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post(
        "/add_favorite", data={"activity": mock_exercise["href"], "action": "remove"}
    )
    assert response.status_code == 302


# confirm invalid action input
def test_add_favorite_invalid_action(client, mock_user, mock_exercise):
    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post(
        "/add_favorite",
        data={"activity": mock_exercise["href"], "action": "invalid_action"},
    )
    assert response.status_code == 400
    assert b"Invalid action specified" in response.data


# confirm empty request body
def test_add_favorite_empty_request(client, mock_user):
    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/add_favorite", data={})
    assert response.status_code == 400
    assert b"Exercise ID is required" in response.data


# --------------------------------------->
# --------- TESTING CHATBOT ------------->
# --------------------------------------->
# Test unauthorized access
def test_chatbot_unauthenticated(client):
    response = client.post("/chat", json={"message": "Hello"})
    assert response.status_code == 401
    assert b"User not logged in" in response.data


# Test missing message field
def test_chatbot_missing_message(client, mock_user):
    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/chat", json={})
    assert response.status_code == 400
    assert b"Message is required" in response.data


# Test empty message input
def test_chatbot_empty_message(client, mock_user):
    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 400
    assert b"Message is required" in response.data


# Test non-menu item message
def test_non_menu_item_message(client, mock_user):
    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/chat", json={"message": "I want to rule the world"})
    assert response.status_code == 200

    assert (
        b"Sorry, I didn't understand that. Please select an option below"
        in response.data
    )


# Test chatbot given 0 for menu
def test_chatbot_valid_response_zero(client, mock_user):
    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/chat", json={"message": "0"})
    assert response.status_code == 200
    assert (
        b"Hello there! I am BurnBot, and I am here to help you achieve your fitness goals."
        in response.data
    )


# Test chatbot given 1 to get calories of input food
def test_chatbot_valid_response_one(client, mock_user):
    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/chat", json={"message": "1"})
    assert response.status_code == 200
    assert (
        b"Please tell me the food item, and I will fetch its calorie count for you."
        in response.data
    )


# Test chatbot asking for menu with non numeric input
def test_chatbot_valid_response_non_numeric(client, mock_user):
    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/chat", json={"message": "menu"})
    assert response.status_code == 200
    assert (
        b"Hello there! I am BurnBot, and I am here to help you achieve your fitness goals."
        in response.data
    )

    response = client.post("/chat", json={"message": "start"})
    assert response.status_code == 200
    assert (
        b"Hello there! I am BurnBot, and I am here to help you achieve your fitness goals."
        in response.data
    )


# Test chatbot asking for calorie information of avocado
def test_chatbot_get_calorie(client, mock_user, monkeypatch):
    def mock_calories(food_item):
        if food_item == "avocado":
            return 110
        return 0

    monkeypatch.setattr("application.get_calories", mock_calories)

    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/chat", json={"message": "0"})
    response = client.post("/chat", json={"message": "1"})
    assert response.status_code == 200
    assert (
        b"Please tell me the food item, and I will fetch its calorie count for you."
        in response.data
    )

    response = client.post("/chat", json={"message": "avocado"})
    assert response.status_code == 200
    assert b"The calorie count for avocado is 110 kcal" in response.data


# Test asking for calorie information twice
def test_chatbot_get_calorie_twice(client, mock_user, monkeypatch):
    def mock_calories(food_item):
        if food_item == "avocado":
            return 110
        elif food_item == "bacon and eggs":
            return 500
        return 0

    monkeypatch.setattr("application.get_calories", mock_calories)

    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/chat", json={"message": "0"})
    response = client.post("/chat", json={"message": "1"})
    assert response.status_code == 200
    assert (
        b"Please tell me the food item, and I will fetch its calorie count for you."
        in response.data
    )

    response = client.post("/chat", json={"message": "avocado"})
    assert response.status_code == 200
    assert b"The calorie count for avocado is 110 kcal" in response.data

    response = client.post("/chat", json={"message": "bacon and eggs"})
    assert response.status_code == 200
    assert b"The calorie count for bacon and eggs is 500 kcal" in response.data


# Test asking for menu after getting calorie info
def test_chatbot_get_menu_after_calorie(client, mock_user, monkeypatch):
    def mock_calories(food_item):
        if food_item == "avocado":
            return 110
        return 0

    monkeypatch.setattr("application.get_calories", mock_calories)

    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/chat", json={"message": "0"})
    response = client.post("/chat", json={"message": "1"})
    assert response.status_code == 200
    assert (
        b"Please tell me the food item, and I will fetch its calorie count for you."
        in response.data
    )

    response = client.post("/chat", json={"message": "avocado"})
    assert response.status_code == 200
    assert b"The calorie count for avocado is 110 kcal" in response.data

    response = client.post("/chat", json={"message": "0"})
    assert response.status_code == 200
    assert (
        b"Hello there! I am BurnBot, and I am here to help you achieve your fitness goals."
        in response.data
    )


# Test getting calorie of food that can't be found
def test_chatbot_get_calorie_invalid_food(client, mock_user, monkeypatch):
    def mock_calories(food_item):
        if food_item == "avocado":
            return 110
        return None

    monkeypatch.setattr("application.get_calories", mock_calories)

    with client.session_transaction() as sess:
        sess["email"] = mock_user["email"]

    response = client.post("/chat", json={"message": "0"})
    response = client.post("/chat", json={"message": "1"})
    assert response.status_code == 200
    assert (
        b"Please tell me the food item, and I will fetch its calorie count for you."
        in response.data
    )

    response = client.post("/chat", json={"message": "fake-food"})
    assert response.status_code == 200
    assert (
        b"Sorry, I couldn't find the calorie count for fake-food. Please check the spelling or try a different food item. Otherwise, enter 0 to go back to the menu."
        in response.data
    )


if __name__ == "__main__":
    unittest.main()
