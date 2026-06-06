"""Tests for user authentication: register, login, logout, protected routes."""


def test_register_page_loads(client):
    """GET /register returns 200."""
    resp = client.get('/register')
    assert resp.status_code == 200
    assert b'Register' in resp.data


def test_register_new_user(client):
    """POST /register with valid data creates user and redirects."""
    resp = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Registration successful' in resp.data


def test_register_duplicate_username(client, sample_user):
    """Registering with an existing username shows error."""
    user, _ = sample_user
    resp = client.post('/register', data={
        'username': user.username,
        'email': 'other@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
    }, follow_redirects=True)
    assert b'already taken' in resp.data


def test_login_valid(client, sample_user):
    """POST /login with correct credentials logs in and redirects."""
    user, password = sample_user
    resp = client.post('/login', data={
        'username': user.username,
        'password': password,
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Logged in' in resp.data


def test_login_invalid(client, sample_user):
    """POST /login with wrong password shows error."""
    user, _ = sample_user
    resp = client.post('/login', data={
        'username': user.username,
        'password': 'wrongpass',
    }, follow_redirects=True)
    assert b'Invalid' in resp.data


def test_protected_route_redirects_anonymous(client):
    """Anonymous user accessing /articles/new is redirected to /login."""
    resp = client.get('/articles/new')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_logout(logged_in_client):
    """GET /logout logs out and redirects."""
    resp = logged_in_client.get('/logout', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Logged out' in resp.data
