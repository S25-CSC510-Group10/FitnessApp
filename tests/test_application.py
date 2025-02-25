import pytest
import sys
import os
from application import app, mongo
from flask import session
from forms import CalorieForm
import pdb

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "secret"
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client

# Database user
@pytest.fixture
def mock_user():
    return {"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}

def mock_find_one(query, fields):
    if query["email"] == mock_user["email"]:
        return mock_user
    return None

def mock_insert_one(data):
    return None

def mock_delete_many(query):
    return None

def mock_insert(data):
        return None  # Simulate successful insertion

def mock_update_many(query, update):
    return None  # Simulate successful update

# Test a successful login.
def test_login_success(client, mock_user, monkeypatch):
    
    monkeypatch.setattr(mongo.db.user, "find_one", mock_find_one)

    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

# Test an unsuccessful login with a user that doesn't exist.
def test_login_failure(client, monkeypatch):
    
    monkeypatch.setattr(mongo.db.user, "find_one", mock_find_one)

    response = client.post("/login", data={"name": "hi", "email": "beans@gmail.com", "password": "sadflkjas;ldfkj"}, follow_redirects=True)
    assert b"Login Unsuccessful" in response.data
    assert session.get("email") is None

# Test accessing login page when already logged in
def test_login_redirect_if_logged_in(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    
    response = client.get("/login", follow_redirects=True)
    assert response.status_code == 200

# Test a user's registration.
def test_registration(client, monkeypatch):
    
    monkeypatch.setattr(mongo.db.user, "delete_many", mock_delete_many)

    # Ensure no existing user has the same email
    mongo.db.user.delete_many({"email": "newuser@example.com"})
    mongo.db.profile.delete_many({"email": "newuser@example.com"})


    monkeypatch.setattr(mongo.db.user, "insert_one", mock_insert_one)
    monkeypatch.setattr(mongo.db.profile, "insert_profile", mock_insert_one)

    response = client.post(
        "/register",
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword",
            "confirm_password": "securepassword",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True
    )

    assert b"Account created for newuser!" in response.data

# Test a user's registration that should fail with no username.
def test_registration_no_username(client, monkeypatch):
    
    monkeypatch.setattr(mongo.db.user, "delete_many", mock_delete_many)

    # Ensure no existing user has the same email
    mongo.db.user.delete_many({"email": "newuser@example.com"})
    mongo.db.profile.delete_many({"email": "newuser@example.com"})

    monkeypatch.setattr(mongo.db.user, "insert_one", mock_insert_one)
    monkeypatch.setattr(mongo.db.profile, "insert_profile", mock_insert_one)

    response = client.post(
        "/register",
        data = {
            "username": "",
            "email": "newuser@example.com",
            "password": "securepassword",
            "confirm_password": "securepassword",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True
    )

    assert b"Account created for newuser!" not in response.data

# Test a user's registration that should fail with no password.
def test_registration_no_password(client, monkeypatch):
    
    monkeypatch.setattr(mongo.db.user, "delete_many", mock_delete_many)

    # Ensure no existing user has the same email
    mongo.db.user.delete_many({"email": "newuser@example.com"})
    mongo.db.profile.delete_many({"email": "newuser@example.com"})

    monkeypatch.setattr(mongo.db.user, "insert_one", mock_insert_one)
    monkeypatch.setattr(mongo.db.profile, "insert_profile", mock_insert_one)

    response = client.post(
        "/register",
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "",
            "confirm_password": "",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True
    )

    assert b"Account created for newuser!" not in response.data

# def test_calories(client, monkeypatch):

#     monkeypatch.setattr(mongo.db.calories, "find_one", mock_find_one)
#     monkeypatch.setattr(mongo.db.calories, "insert", mock_insert)
#     monkeypatch.setattr(mongo.db.calories, "update_many", mock_update_many)

#     # Register a user.
#     client.post(
#         "/register",
#         data = {
#             "username": "newuser",
#             "email": "newuser@example.com",
#             "password": "securepassword",
#             "confirm_password": "securepassword",
#             "weight": "70",
#             "height": "175",
#             "goal": "Weight Loss",
#             "target_weight": "65",
#         },
#         follow_redirects=True
#     )

#     # Log the user in
#     client.post(
#         "/login",
#         data={"email": "newuser@example.com", "pwd": "securepassword"},
#         follow_redirects=True,
#     )

#     form = CalorieForm()

#     print(form.food.choices[0][1])
#     form.validate()

#     # Put calories into their tracker
#     response = client.post(
#         "/calories",
#         data = {
#             "food": form.food.choices[0][1],
#             "burnout": "30"
#         },
#         follow_redirects=True
#     )

#     print("Form errors:", form.errors)

#     assert b"Successfully updated the data" in response.data