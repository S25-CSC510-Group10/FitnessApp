import pytest
import sys
import os
from application import app, mongo
from flask import session
from forms import LoginForm

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

# Test a successful login.
def test_login_success(client, mock_user, monkeypatch):
    def mock_find_one(query, fields):
        if query["email"] == mock_user["email"]:
            return mock_user
        return None

    monkeypatch.setattr(mongo.db.user, "find_one", mock_find_one)

    response = client.post("/login", data={"name": "hplenham", "email": "hplenham@gmail.com", "password": "3g:$*fe9R=@9zx"}, follow_redirects=True)
    
    # messages = get_flashed_messages()
    # print(messages)  # Print any flash messages for debugging

    form = LoginForm()
    form.validate()
    # Print the form errors for debugging
    print("Form Errors:", form.errors)

    assert b"You have been logged in!" in response.data
    assert session.get("email") == "hplenham@gmail.com"

# Test an unsuccessful login with a user that doesn't exist.
def test_login_failure(client, monkeypatch):
    def mock_find_one(query, fields):
        return None
    
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
# def test_registration(client, monkeypatch):