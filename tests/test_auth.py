import re
import pytest

from app import create_app
from app.extensions import db as _db
from app.models.user import User


def get_csrf(html: str):
    m = re.search(r"name=[\"']csrf_token[\"'] type=[\"']hidden[\"'] value=[\"']([^\"']+)[\"']", html)
    if m:
        return m.group(1)
    m = re.search(r"name=[\"']csrf_token[\"'] value=[\"']([^\"']+)[\"']", html)
    return m.group(1) if m else None


@pytest.fixture
def app():
    app = create_app("testing")
    app.config.update({
        "WTF_CSRF_ENABLED": True,
        "TESTING": True,
    })

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, email, password, first_name="A", last_name="B"):
    r = client.get("/auth/register")
    csrf = get_csrf(r.data.decode())
    data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "confirm_password": password,
        "csrf_token": csrf,
    }
    return client.post("/auth/register", data=data)


def login(client, email, password, next_url=None):
    url = "/auth/login"
    if next_url:
        url += f"?next={next_url}"
    r = client.get(url)
    csrf = get_csrf(r.data.decode())
    data = {"email": email, "password": password, "csrf_token": csrf}
    return client.post(url, data=data, follow_redirects=False)


def test_successful_registration(client, app):
    resp = register(client, "user@example.com", "StrongPass1!")
    assert resp.status_code in (302,)
    with app.app_context():
        user = User.query.filter_by(email="user@example.com").first()
        assert user is not None


def test_duplicate_email_registration(client, app):
    with app.app_context():
        u = User(email="dup@example.com")
        u.set_password("StrongPass1!")
        _db.session.add(u)
        _db.session.commit()

    resp = register(client, "dup@example.com", "StrongPass1!")
    # Should render the register page again with validation error
    assert resp.status_code == 200
    assert b"An account with this email already exists." in resp.data


def test_weak_password_rejection(client):
    resp = register(client, "weak@example.com", "weakpass")
    assert resp.status_code == 200
    assert b"Password must be at least 12 characters" in resp.data


def test_successful_login(client, app):
    with app.app_context():
        u = User(email="login@example.com")
        u.set_password("StrongPass1!")
        _db.session.add(u)
        _db.session.commit()

    resp = login(client, "login@example.com", "StrongPass1!")
    assert resp.status_code == 302
    # After login, logout endpoint should be accessible and redirect
    r2 = client.get("/auth/logout", follow_redirects=False)
    assert r2.status_code == 302


def test_failed_login(client, app):
    with app.app_context():
        u = User(email="fail@example.com")
        u.set_password("StrongPass1!")
        _db.session.add(u)
        _db.session.commit()

    resp = login(client, "fail@example.com", "WrongPass")
    # Should render login with error flash
    assert resp.status_code == 200
    assert b"Invalid email or password." in resp.data


def test_account_lockout(client, app):
    email = "lock@example.com"
    with app.app_context():
        u = User(email=email)
        u.set_password("StrongPass1!")
        _db.session.add(u)
        _db.session.commit()

    # perform failed attempts equal to lock threshold (default 5)
    for _ in range(5):
        r = login(client, email, "WrongPass")
    with app.app_context():
        u = User.query.filter_by(email=email).first()
        assert u.is_locked

    # even correct password should not allow login while locked
    r2 = login(client, email, "StrongPass1!")
    assert r2.status_code == 200
    assert b"Invalid email or password." in r2.data


def test_logout(client, app):
    with app.app_context():
        u = User(email="out@example.com")
        u.set_password("StrongPass1!")
        _db.session.add(u)
        _db.session.commit()

    r = login(client, "out@example.com", "StrongPass1!")
    assert r.status_code == 302
    r2 = client.get("/auth/logout", follow_redirects=False)
    assert r2.status_code == 302


def test_password_reset_request(client):
    r = client.get("/auth/reset-password")
    csrf = get_csrf(r.data.decode())
    resp = client.post(
        "/auth/reset-password",
        data={"email": "someone@example.com", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert resp.status_code == 302


def test_csrf_protection_on_registration(client):
    # Post without csrf token should be rejected
    resp = client.post(
        "/auth/register",
        data={"email": "x@example.com", "password": "StrongPass1!", "confirm_password": "StrongPass1!"},
    )
    assert resp.status_code == 400


def test_open_redirect_protection(client, app):
    with app.app_context():
        u = User(email="redir@example.com")
        u.set_password("StrongPass1!")
        _db.session.add(u)
        _db.session.commit()

    evil = "https://evil.com"
    r = client.get(f"/auth/login?next={evil}")
    csrf = get_csrf(r.data.decode())
    resp = client.post(f"/auth/login?next={evil}", data={"email": "redir@example.com", "password": "StrongPass1!", "csrf_token": csrf}, follow_redirects=False)
    assert resp.status_code == 302
    location = resp.headers.get("Location", "")
    assert "evil.com" not in location
