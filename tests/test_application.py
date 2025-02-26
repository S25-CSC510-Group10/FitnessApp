import pytest
import sys
import os
from application import app, mongo
from flask import session
from application import reminder_email
from unittest.mock import MagicMock
from forms import CalorieForm

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


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
    return {
        "name": "hplenham",
        "email": "hplenham@gmail.com",
        "password": "3g:$*fe9R=@9zx",
    }


def mock_find_one(query):
    if query["email"] == mock_user["email"]:
        return mock_user
    return None


def mock_insert_one():
    return None


def mock_delete_many():
    return None


def mock_insert():
    return None  # Simulate successful insertion


def mock_update_many():
    return None  # Simulate successful update


def login_setup(client):
    client.post(
        "/register",
        data={
            "username": "hplenham",
            "email": "hplenham@gmail.com",
            "password": "3g:$*fe9R=@9zx",
            "confirm_password": "3g:$*fe9R=@9zx",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True,
    )


# Test a successful login.
def test_login_success(client, monkeypatch):

    login_setup(client)

    monkeypatch.setattr(mongo.db.user, "find_one", mock_find_one)

    response = client.post(
        "/login",
        data={
            "name": "hplenham",
            "email": "hplenham@gmail.com",
            "password": "3g:$*fe9R=@9zx",
        },
        follow_redirects=True,
    )

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"


# Test an unsuccessful login with a user that doesn't exist.
def test_login_failure(client, monkeypatch):

    monkeypatch.setattr(mongo.db.user, "find_one", mock_find_one)

    response = client.post(
        "/login",
        data={"name": "hi", "email": "beans@gmail.com", "password": "sadflkjas;ldfkj"},
        follow_redirects=True,
    )
    assert b"Login Unsuccessful" in response.data
    assert session.get("email") is None


# Test accessing login page when already logged in
def test_login_redirect_if_logged_in(client):
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
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword",
            "confirm_password": "securepassword",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True,
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
        data={
            "username": "",
            "email": "newuser@example.com",
            "password": "securepassword",
            "confirm_password": "securepassword",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True,
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
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "",
            "confirm_password": "",
            "weight": "70",
            "height": "175",
            "goal": "Weight Loss",
            "target_weight": "65",
        },
        follow_redirects=True,
    )

    assert b"Account created for newuser!" not in response.data


# Test adding a valid calorie intake.
def test_calories_valid(client, monkeypatch):

    monkeypatch.setattr(mongo.db.calories, "find_one", mock_find_one)
    monkeypatch.setattr(mongo.db.calories, "insert", mock_insert)
    monkeypatch.setattr(mongo.db.calories, "update_many", mock_update_many)
    monkeypatch.setattr(mongo.db.user, "find_one", mock_find_one)

    response = client.post(
        "/login",
        data={
            "name": "hplenham",
            "email": "hplenham@gmail.com",
            "password": "3g:$*fe9R=@9zx",
        },
        follow_redirects=True,
    )

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Put calories into their tracker
    response = client.post(
        "/calories", data={"food": "acai (20)", "burnout": "30"}, follow_redirects=True
    )

    form = CalorieForm()
    form.validate()
    print(form.errors)

    assert b"Successfully updated the data" in response.data


# Test adding an INVALID calorie intake where the item is wrong
def test_calories_invalid_item(client, monkeypatch):

    monkeypatch.setattr(mongo.db.calories, "find_one", mock_find_one)
    monkeypatch.setattr(mongo.db.calories, "insert", mock_insert)
    monkeypatch.setattr(mongo.db.calories, "update_many", mock_update_many)
    monkeypatch.setattr(mongo.db.user, "find_one", mock_find_one)

    response = client.post(
        "/login",
        data={
            "name": "hplenham",
            "email": "hplenham@gmail.com",
            "password": "3g:$*fe9R=@9zx",
        },
        follow_redirects=True,
    )

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Attempt to put in an invalid item (one that doesn't exist)
    response = client.post(
        "/calories", data={"food": "Acai (19)", "burnout": "30"}, follow_redirects=True
    )

    assert b"Successfully updated the data" not in response.data


# Test adding an INVALID calorie intake where burnout wasn't entered
def test_calories_invalid_burnout(client, monkeypatch):

    monkeypatch.setattr(mongo.db.calories, "find_one", mock_find_one)
    monkeypatch.setattr(mongo.db.calories, "insert", mock_insert)
    monkeypatch.setattr(mongo.db.calories, "update_many", mock_update_many)
    monkeypatch.setattr(mongo.db.user, "find_one", mock_find_one)

    response = client.post(
        "/login",
        data={
            "name": "hplenham",
            "email": "hplenham@gmail.com",
            "password": "3g:$*fe9R=@9zx",
        },
        follow_redirects=True,
    )

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Put in a valid item but with no burnout.
    response = client.post(
        "/calories", data={"food": "Acai (20)", "burnout": ""}, follow_redirects=True
    )

    assert b"Successfully updated the data" not in response.data


# Tests displaying a profile with a user logged in
def test_display_profile_valid(client):

    response = client.post(
        "/login",
        data={
            "name": "hplenham",
            "email": "hplenham@gmail.com",
            "password": "3g:$*fe9R=@9zx",
        },
        follow_redirects=True,
    )

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Request the profile page
    response = client.get("/display_profile", follow_redirects=True)

    # Assertions
    assert response.status_code == 200
    assert b"450" in response.data  # Check weight
    assert b"400" in response.data  # Check target weight


# Tests displaying a profile with a user not logged in.
def test_display_profile_invalid(client):

    # Request the profile page
    response = client.get("/display_profile", follow_redirects=True)

    # Assertions
    assert (
        b"450" not in response.data
    )  # Check that there is not a weight inside the response
    assert b"400" not in response.data  # Nor a target weight.


# Tests updating user profile information with valid data.
def test_user_profile_valid(client):

    # As usual, log the user in.
    response = client.post(
        "/login",
        data={
            "name": "hplenham",
            "email": "hplenham@gmail.com",
            "password": "3g:$*fe9R=@9zx",
        },
        follow_redirects=True,
    )

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Post new data to the page
    response = client.post(
        "/user_profile",
        data={
            "weight": "375",
            "height": "500",
            "goal": "Weight Loss",
            "target_weight": "350",
        },
        follow_redirects=True,
    )

    # Ensure that the target weight changed.
    assert b"375" in response.data


# Tests updating user profile information with invalid data.
def test_user_profile_invalid(client):

    # As usual, log the user in.
    response = client.post(
        "/login",
        data={
            "name": "hplenham",
            "email": "hplenham@gmail.com",
            "password": "3g:$*fe9R=@9zx",
        },
        follow_redirects=True,
    )

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Post new data to the page, but the goal isn't valid.
    response = client.post(
        "/user_profile",
        data={
            "weight": "350",
            "height": "400",
            "goal": "Pretty Women",
            "target_weight": "320",
        },
        follow_redirects=True,
    )

    # Ensure that the goal did not change.
    assert b"Pretty Women" not in response.data


@pytest.fixture
def mock_mongo(monkeypatch):
    """Mock MongoDB distinct email query"""
    mock_db = MagicMock()
    mock_db.distinct.return_value = ["test1@example.com", "test2@example.com"]
    monkeypatch.setattr("application.mongo.db.user", mock_db)
    return mock_db  # Return the mock to check calls if needed


@pytest.fixture
def mock_smtp(monkeypatch):
    """Mock SMTP to prevent actual emails from being sent"""
    sent_emails = []  # Shared list to store emails

    class MockSMTP:
        def __init__(self, host, port):
            self.sent_emails = sent_emails  # Store in shared list

        def login(self, email, password):
            pass  # Do nothing

        def sendmail(self, sender, recipient, message):
            self.sent_emails.append((sender, recipient, message))

        def quit(self):
            pass  # Do nothing

    monkeypatch.setattr(
        "application.smtplib.SMTP_SSL", lambda host, port: MockSMTP(host, port)
    )

    return sent_emails  # Return the shared list


# Tests the ability to send reminder emails.
def test_reminder_email(mock_mongo, mock_smtp):
    """Test the reminder_email function"""

    reminder_email()  # Call the function

    # Ensure MongoDB was queried
    mock_mongo.distinct.assert_called_once_with("email")

    # Verify emails were sent
    assert len(mock_smtp) == 2  # Now this should correctly detect sent emails
    assert (
        "burnoutapp2023@gmail.com",
        "test1@example.com",
        "Subject: Daily Reminder to Exercise",
    ) in mock_smtp
    assert (
        "burnoutapp2023@gmail.com",
        "test2@example.com",
        "Subject: Daily Reminder to Exercise",
    ) in mock_smtp
