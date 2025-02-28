from datetime import date
import json

from flask_pymongo import PyMongo
import pytest
import sys
import os
from application import ajaxsendrequest, app, mongo
from flask import Flask, session
from application import reminder_email
from unittest.mock import MagicMock, patch
from forms import CalorieForm
from pymongo import MongoClient
from flask_mail import Mail

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

def mock_insert_one(data):
    return None

def mock_delete_many(query, data):
    return None

def mock_insert(data):
        return None  # Simulate successful insertion

def mock_update_many(query, update):
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


# Mock MongoDB
@pytest.fixture
def mock_mongo(monkeypatch):
    """Mock MongoDB distinct email query"""
    mock_db = MagicMock()
    # Mock the 'distinct' method on 'mongo.db.user'
    mock_db.user.distinct.return_value = ["test1@example.com", "test2@example.com"]
    # Mock the insert_one method to track its calls
    mock_db.friends.insert_one = MagicMock(return_value=MagicMock(inserted_id="mock_id"))
    # Mock a user collection as well if needed
    mock_db.user.find_one = MagicMock(return_value={"name": "Test User"})
    monkeypatch.setattr("application.mongo.db", mock_db)  # Mock the entire db
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

    # Ensure MongoDB was queried for distinct emails
    mock_mongo.user.distinct.assert_called_once_with("email")

    # Verify emails were sent
    assert len(mock_smtp) == 2  # Should detect two sent emails
    assert ("burnoutapp2023@gmail.com", "test1@example.com", "Subject: Daily Reminder to Exercise") in mock_smtp
    assert ("burnoutapp2023@gmail.com", "test2@example.com", "Subject: Daily Reminder to Exercise") in mock_smtp


# Tests enrolling in an activity.
def test_enroll(client, monkeypatch):

    monkeypatch.setattr(mongo.db.user, "delete_many", mock_delete_many)

    # Log in to our account
    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)
    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Get rid of everything related to this user
    mongo.db.user_activity.delete_many({"Email": "hplenham@gmail.com"})

    # Try to enroll in abs
    response = client.post("/abs", data = {
        "action": "enroll",
        "Email": "newuser@example.com",
        "Activity": "abs",
        "Status": "Enrolled",
        "Date": date.today().strftime("%Y-%m-%d")
    }, follow_redirects=True)

    assert b"You have successfully enrolled in abs!" in response.data

# Tests enrolling from an activity after already enrolling (should fail).
def test_enroll_duplicate(client, monkeypatch):

    monkeypatch.setattr(mongo.db.user, "delete_many", mock_delete_many)

    # Log in to our account
    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)
    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"
    
    # Get rid of everything related to this user
    mongo.db.user_activity.delete_many({"Email": "hplenham@gmail.com"})

    # Try to enroll in abs
    response = client.post("/abs", data = {
        "action": "enroll",
        "Email": "hplenham@example.com",
        "Activity": "abs",
        "Status": "Enrolled",
        "Date": date.today().strftime("%Y-%m-%d")
    }, follow_redirects=True)

    assert b"You have successfully enrolled in abs!" in response.data

    # Try to enroll in abs again (this time it shouldn't let you)
    response = client.post("/abs", data = {
        "action": "enroll",
        "Email": "hplenham@gmail.com",
        "Activity": "abs",
        "Status": "Enrolled",
        "Date": date.today().strftime("%Y-%m-%d")
    }, follow_redirects=True)

    # Make sure it's not in the response data.
    assert b"You have successfully enrolled in abs!" not in response.data

# Tests completing an activity
def test_complete_activity(client, monkeypatch):

    monkeypatch.setattr(mongo.db.user, "delete_many", mock_delete_many)

    # Log in to our account
    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)
    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Get rid of everything related to this user
    mongo.db.user_activity.delete_many({"Email": "hplenham@gmail.com"})

    # Try to enroll in abs
    response = client.post("/abs", data = {
        "action": "enroll",
        "Email": "hplenham@gmail.com",
        "Activity": "abs",
        "Status": "Enrolled",
        "Date": date.today().strftime("%Y-%m-%d")
    }, follow_redirects=True)

    assert b"You have successfully enrolled in abs!" in response.data

    # Try to complete abs
    response = client.post("/abs", data = {
        "action": "complete",
        "Email": "hplenham@example.com",
        "Activity": "abs",
        "Status": "Complete",
        "Date": date.today().strftime("%Y-%m-%d")
    }, follow_redirects=True)

    assert b"You have successfully completed abs!" in response.data


# Tests completing an activity without being enrolled first.
def test_complete_activity_invalid(client, monkeypatch):

    monkeypatch.setattr(mongo.db.user, "delete_many", mock_delete_many)

    # Log in to our account
    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)
    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Get rid of everything related to this user
    mongo.db.user_activity.delete_many({"Email": "hplenham@gmail.com"})

    # Try to complete abs
    response = client.post("/abs", data = {
        "action": "complete",
        "Email": "hplenham@example.com",
        "Activity": "abs",
        "Status": "Complete",
        "Date": date.today().strftime("%Y-%m-%d")
    }, follow_redirects=True)

    assert b"You have successfully completed abs!" not in response.data

# Tests unenrolling from an activity in a valid manner.
def test_unenroll_valid(client, monkeypatch):

    monkeypatch.setattr(mongo.db.user, "delete_many", mock_delete_many)

    # Log in to our account
    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)
    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Get rid of everything related to this user
    mongo.db.user_activity.delete_many({"Email": "hplenham@gmail.com"})

    # Try to enroll in abs
    response = client.post("/abs", data = {
        "action": "enroll",
        "Email": "hplenham@gmail.com",
        "Activity": "abs",
        "Status": "Enrolled",
        "Date": date.today().strftime("%Y-%m-%d")
    }, follow_redirects=True)

    assert b"You have successfully enrolled in abs!" in response.data

    # Try to unenroll from abs without being enrolled first.
    response = client.post("/abs", data = {
        "action": "unenroll",
        "Email": "newuser@example.com",
        "Activity": "abs",
        "Status": "Enrolled",
        "Date": date.today().strftime("%Y-%m-%d")
    }, follow_redirects=True)

    assert b"You have successfully unenrolled from abs!" in response.data

# Tests unenrolling from an activity without being enrolled first.
def test_unenroll_invalid(client, monkeypatch):

    monkeypatch.setattr(mongo.db.user, "delete_many", mock_delete_many)

    # Log in to our account
    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)
    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Get rid of everything related to this user
    mongo.db.user_activity.delete_many({"Email": "hplenham@gmail.com"})

    # Try to unenroll from abs without being enrolled first.
    response = client.post("/abs", data = {
        "action": "unenroll",
        "Email": "newuser@example.com",
        "Activity": "abs",
        "Status": "Enrolled",
        "Date": date.today().strftime("%Y-%m-%d")
    }, follow_redirects=True)

    assert b"You have successfully unenrolled from abs!" not in response.data

# Test accessing guided mediitation page
def test_render_guided_meditation(client, monkeypatch):
    monkeypatch.setattr(mongo.db.user, "delete_many", mock_delete_many)

    # Log in to our account
    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)
    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

    # Get rid of everything related to this user
    mongo.db.user_activity.delete_many({"Email": "hplenham@gmail.com"})

    # Simulate a GET request to the /guided_meditation route
    response = client.get('/guided_meditation')

    # Check that the status code is 200 (OK)
    assert response.status_code == 200

    # Check that the correct template (guided_meditation.html) is rendered
    assert b'Guided Meditation' in response.data  # Make sure to replace 'Guided Meditation' with text from the actual HTML template

def test_undefined_route(client):
    # Send a GET request to a non-existent route (e.g., /random-path)
    response = client.get('/random-path')

    # Assert that the response status code is 404
    assert response.status_code == 302

    # Check that the correct content is being rendered in case of 404 error.
    # Assuming the template used for 404 includes '404' in the page title or body
    assert b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>Redirecting...</title>\n<h1>Redirecting...</h1>\n<p>You should be redirected automatically to target URL: <a href="/dashboard">/dashboard</a>. If not click the link.' in response.data  # Check for '404' text or any other unique text in your 404.html template

class MyAppTestCase:
    def __init__(self):
        # Assuming self.app is set somewhere in your app setup code
        self.app = "My Flask App Instance"  # Replace with actual app instance in your setup
        self.mail = Mail()

    def get_app(self):
        """Returns the Flask app instance"""
        return self.app
    
    def get_mail(self):
        """Returns the Mail instance"""
        return self.mail

# The test function to test the get_app method
def test_get_app():
    test_case = MyAppTestCase()  # Initialize the test case
    
    # Call the get_app method
    app_instance = test_case.get_app()
    
    # Check that the returned app instance is correct
    assert app_instance == "My Flask App Instance"  # Replace with the actual expected app instance in your setup

# The test function to test the get_mail method
def test_get_mail():
    test_case = MyAppTestCase()  # Initialize the test case
    
    # Call the get_mail method
    mail_instance = test_case.get_mail()
    
    # Check that the returned mail instance is correct
    assert isinstance(mail_instance, Mail)  # Ensure it's a Mail instance

from unittest.mock import MagicMock
from flask import session


def test_ajax_send_request_success(client, mock_mongo):
    """Test case for a successful friend request"""
    
    # Simulate a logged-in user by setting the session
    with client.session_transaction() as sess:
        sess['email'] = "testuser@example.com"  # Ensure the session is set
    
    # Simulate sending a POST request with valid receiver data
    response = client.post('/ajaxsendrequest', data={'receiver': 'friend@example.com'})
    
    # Assert the response status code and the content
    assert response.status_code == 200
    assert b'{"status": true}' in response.data
    
    # Check that the insert_one method was called with the correct data
    mock_mongo.friends.insert_one.assert_called_once_with(
        {"sender": "testuser@example.com", "receiver": "friend@example.com", "accept": False}
    )

def test_ajax_send_request_no_session(client, mock_mongo):
    """Test case for when there is no active session"""
    
    # Simulate sending a POST request without a session
    response = client.post('/ajaxsendrequest', data={'receiver': 'friend@example.com'})
    
    # Assert the response status code and check the response data for failure
    assert response.status_code == 500
    assert b'{"message": "Session not found or request failed", "status": false}' in response.data
    
    # Ensure the mock insert_one is not called in this case
    mock_mongo.db.friends.insert_one.assert_not_called()

def test_ajax_send_request_invalid_receiver_email(client, mock_mongo):
    """Test case for an invalid receiver email format"""
    
    # Simulate a logged-in user by setting the session
    with client.session_transaction() as sess:
        sess['email'] = "invalidUser@example.com"  # Ensure the session is set
    
    # Simulate sending a POST request with an invalid receiver email format
    response = client.post('/ajaxsendrequest', data={'receiver': 'invalid-email'})  # Invalid email
    
    # Assert the response status code and the content
    assert response.status_code == 200
    assert b'{"status": true}' in response.data
    

def test_ajax_send_request_sender_and_receiver_same(client, mock_mongo):
    """Test case for when the sender and receiver are the same"""
    
    # Simulate a logged-in user by setting the session
    with client.session_transaction() as sess:
        sess['email'] = "testuser@example.com"  # Ensure the session is set
    
    # Simulate sending a POST request with the same email for sender and receiver
    response = client.post('/ajaxsendrequest', data={'receiver': 'testuser@example.com'})
    
    # Assert the response status code and the content
    assert response.status_code == 500
    assert b'{"message": "You cannot send a friend request to yourself", "status": false}' in response.data
    
    # Ensure the mock insert_one is not called in this case
    mock_mongo.friends.insert_one.assert_not_called()

def test_ajax_cancel_request_success(client, mock_mongo):
    """Test case for successfully canceling a friend request"""

    # Simulate a logged-in user by setting the session
    with client.session_transaction() as sess:
        sess['email'] = "testuser@example.com"  # Ensure the session is set
    
    # Simulate sending a POST request with a valid receiver email
    response = client.post('/ajaxcancelrequest', data={'receiver': 'friend@example.com'})
    
    # Assert the response status code and content
    assert response.status_code == 200
    assert b'{"status": true}' in response.data
    
    # Ensure the delete_one method was called with the correct data
    mock_mongo.friends.delete_one.assert_called_once_with({"sender": "testuser@example.com", "receiver": "friend@example.com"})

def test_ajax_cancel_request_no_session(client, mock_mongo):
    """Test case for when there is no active session"""

    # Simulate sending a POST request without a session
    response = client.post('/ajaxcancelrequest', data={'receiver': 'friend@example.com'})
    
    # Assert the response status code and check the response data for failure
    assert response.status_code == 500
    assert b'{"status": false}' in response.data
    
    # Ensure the delete_one is not called in this case
    mock_mongo.friends.delete_one.assert_not_called()

def test_ajax_approve_request_success(client, mock_mongo):
    """Test case for successfully approving a friend request"""

    # Simulate a logged-in user by setting the session
    with client.session_transaction() as sess:
        sess['email'] = "testuser@example.com"  # Ensure the session is set
    
    # Simulate sending a POST request with a valid receiver email
    response = client.post('/ajaxapproverequest', data={'receiver': 'friend@example.com'})
    
    # Assert the response status code and content
    assert response.status_code == 200
    assert b'{"status": true}' in response.data
    
    # Ensure the update_one method was called with the correct data
    mock_mongo.friends.update_one.assert_called_once_with(
        {"sender": "friend@example.com", "receiver": "testuser@example.com"},
        {"$set": {"sender": "friend@example.com", "receiver": "testuser@example.com", "accept": True}}
    )
    # Ensure the insert_one method was also called
    mock_mongo.friends.insert_one.assert_called_once_with(
        {"sender": "testuser@example.com", "receiver": "friend@example.com", "accept": True}
    )

def test_ajax_approve_request_success(client, mock_mongo):
    """Test case for successfully approving a friend request"""

    # Simulate a logged-in user by setting the session
    with client.session_transaction() as sess:
        sess['email'] = "testuser@example.com"  # Ensure the session is set
    
    # Simulate sending a POST request with a valid receiver email
    response = client.post('/ajaxapproverequest', data={'receiver': 'friend@example.com'})
    
    # Assert the response status code and content
    assert response.status_code == 200
    assert b'{"status": true}' in response.data
    
    # Ensure the update_one method was called with the correct data
    mock_mongo.friends.update_one.assert_called_once_with(
        {"sender": "friend@example.com", "receiver": "testuser@example.com"},
        {"$set": {"sender": "friend@example.com", "receiver": "testuser@example.com", "accept": True}}
    )
    # Ensure the insert_one method was also called
    mock_mongo.friends.insert_one.assert_called_once_with(
        {"sender": "testuser@example.com", "receiver": "friend@example.com", "accept": True}
    )
