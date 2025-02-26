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


# ----------------------------------------------
# ----------------- USER LOGIN -----------------
# ----------------------------------------------

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


# ----------------------------------------------
# ------------ USER REGISTRATION ---------------
# ----------------------------------------------

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
            "password": "Securepassword!",
            "confirm_password": "Securepassword!",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True
    )

    assert b"Account created for newuser!" in response.data

# Test a user's registration with the uppercase in the middle of the password.
def test_registration_uppercase_in_middle(client, monkeypatch):
    
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
            "password": "ecurepaSssword!",
            "confirm_password": "ecurepaSssword!",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True
    )

    assert b"Account created for newuser!" in response.data

# Test a user's registration with the uppercase at the end of the password
def test_registration_uppercase_at_end(client, monkeypatch):
    
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
            "password": "ecurepassword!S",
            "confirm_password": "ecurepassword!S",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True
    )

    assert b"Account created for newuser!" in response.data


# Test a user's registration with special character at the beginning of the password
def test_registration_special_at_beginning(client, monkeypatch):
    
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
            "password": "!Securepassword",
            "confirm_password": "!Securepassword",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True
    )

    assert b"Account created for newuser!" in response.data

# Test a user's registration.
def test_registration_special_in_middle(client, monkeypatch):
    
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
            "password": "Secure!password",
            "confirm_password": "Secure!password",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True
    )

    assert b"Account created for newuser!" in response.data

# Test a user's registration with multiple uppercase letters.
def test_registration_multiple_uppercase(client, monkeypatch):
    
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
            "password": "SecuSrepaSssword!",
            "confirm_password": "SecuSrepaSssword!",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True
    )

    assert b"Account created for newuser!" in response.data

# Test a user's registration with multiple uppercase letters.
def test_registration_multiple_special(client, monkeypatch):
    
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
            "password": "Secure!pass!word!",
            "confirm_password": "Secure!pass!word!",
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
            "password": "Securepassword!",
            "confirm_password": "Securepassword!",
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

# Test a user's registration that should fail with short password
def test_registration_invalid_password_too_short(client, monkeypatch):
    
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
            "password": "Passwd!", # Password Length: 7, Uppercase: Yes, Special Character, Yes
            "confirm_password": "Passwd!",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True
    )

    assert b"Account created for newuser!" not in response.data

# Test a user's registration that should fail with no special character in password
def test_registration_invalid_password_no_uppercase(client, monkeypatch):
    
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
            "password": "password!", # Password Length: 9, Uppercase: No, Special Character, Yes
            "confirm_password": "password!",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True
    )

    assert b"Account created for newuser!" not in response.data


# Test a user's registration that should fail with no special character in password
def test_registration_invalid_password_no_special_character(client, monkeypatch):
    
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
            "password": "Password", # Password Length: 8, Uppercase: Yes, Special Character, No
            "confirm_password": "Password",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True
    )

    assert b"Account created for newuser!" not in response.data


# ----------------------------------------------
# -------------- CALORIE INTAKE ----------------
# ----------------------------------------------

# Test adding a valid calorie intake.
def test_calories_valid(client, monkeypatch):

    monkeypatch.setattr(mongo.db.calories, "find_one", mock_find_one)
    monkeypatch.setattr(mongo.db.calories, "insert", mock_insert)
    monkeypatch.setattr(mongo.db.calories, "update_many", mock_update_many)
    monkeypatch.setattr(mongo.db.user, "find_one", mock_find_one)

    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Put calories into their tracker
    response = client.post(
        "/calories",
        data = {
            "food": "Acai (20)",
            "burnout": "30"
        },
        follow_redirects=True
    )

    assert b"Successfully updated the data" in response.data

# Test adding an INVALID calorie intake where the item is wrong
def test_calories_invalid_item(client, monkeypatch):

    monkeypatch.setattr(mongo.db.calories, "find_one", mock_find_one)
    monkeypatch.setattr(mongo.db.calories, "insert", mock_insert)
    monkeypatch.setattr(mongo.db.calories, "update_many", mock_update_many)
    monkeypatch.setattr(mongo.db.user, "find_one", mock_find_one)

    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Attempt to put in an invalid item (one that doesn't exist)
    response = client.post(
        "/calories",
        data = {
            "food": "Acai (19)",
            "burnout": "30"
        },
        follow_redirects=True
    )

    assert b"Successfully updated the data" not in response.data

# Test adding an INVALID calorie intake where burnout wasn't entered
def test_calories_invalid_item(client, monkeypatch):

    monkeypatch.setattr(mongo.db.calories, "find_one", mock_find_one)
    monkeypatch.setattr(mongo.db.calories, "insert", mock_insert)
    monkeypatch.setattr(mongo.db.calories, "update_many", mock_update_many)
    monkeypatch.setattr(mongo.db.user, "find_one", mock_find_one)

    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Put in a valid item but with no burnout.
    response = client.post(
        "/calories",
        data = {
            "food": "Acai (20)",
            "burnout": ""
        },
        follow_redirects=True
    )

    assert b"Successfully updated the data" not in response.data

# ----------------------------------------------
# ----------------- PROFILE --------------------
# ----------------------------------------------

# Tests displaying a profile with a user logged in
def test_display_profile(client):

    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Request the profile page
    response = client.get("/display_profile")

    # Assertions
    assert response.status_code == 200
    assert b"Weight Loss" in response.data  # Check goal
    assert b"450" in response.data  # Check weight
    assert b"400" in response.data  # Check target weight