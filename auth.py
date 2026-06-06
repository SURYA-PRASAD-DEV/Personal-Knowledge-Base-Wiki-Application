"""
User authentication module.
Dual backend: Firestore 'users' collection or JSON fallback in data/users.json.
"""
import uuid
import json
import logging
from datetime import datetime
from pathlib import Path

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from firebase_module import db

logger = logging.getLogger(__name__)

USE_FIRESTORE = db is not None

_USERS_FILE = None
_USER_STORE = {}

USERS_COL = 'users'


def init_auth(app):
    """Initialize auth module with app config. Must be called after app is created."""
    global _USERS_FILE, _USER_STORE, USE_FIRESTORE

    if app.config.get('USE_FIRESTORE') is False:
        USE_FIRESTORE = False

    data_dir = Path(app.config.get('DATA_DIR', Path(__file__).parent / 'data'))
    data_dir.mkdir(exist_ok=True)
    _USERS_FILE = data_dir / 'users.json'

    if not USE_FIRESTORE:
        _USER_STORE.clear()
        if _USERS_FILE.exists():
            try:
                _USER_STORE.update(
                    json.loads(_USERS_FILE.read_text(encoding='utf-8'))
                )
            except Exception:
                pass


class User(UserMixin):
    """Flask-Login compatible user model."""

    def __init__(self, uid, username, email, password_hash, created_at=None):
        self.id = uid
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': str(self.created_at),
        }

    @staticmethod
    def from_dict(uid, data):
        return User(
            uid=uid,
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            created_at=data.get('created_at'),
        )


def _save_users_json():
    """Persist in-memory user store to JSON file."""
    if _USERS_FILE:
        _USERS_FILE.write_text(
            json.dumps(_USER_STORE, default=str, indent=2), encoding='utf-8'
        )


def create_user(username, email, password):
    """Register a new user. Returns User object or None if username/email taken."""
    if get_user_by_username(username) or get_user_by_email(email):
        return None

    uid = str(uuid.uuid4())
    pw_hash = generate_password_hash(password)
    data = {
        'username': username,
        'email': email,
        'password_hash': pw_hash,
        'created_at': str(datetime.utcnow()),
    }

    if USE_FIRESTORE:
        db.collection(USERS_COL).document(uid).set(data)
    else:
        _USER_STORE[uid] = data
        _save_users_json()

    return User.from_dict(uid, data)


def get_user_by_id(uid):
    """Load user by ID. Used by Flask-Login's user_loader callback."""
    if USE_FIRESTORE:
        doc = db.collection(USERS_COL).document(uid).get()
        if not doc.exists:
            return None
        return User.from_dict(doc.id, doc.to_dict())
    else:
        data = _USER_STORE.get(uid)
        if not data:
            return None
        return User.from_dict(uid, data)


def get_user_by_username(username):
    """Find user by username."""
    if USE_FIRESTORE:
        docs = db.collection(USERS_COL).where('username', '==', username).limit(1).get()
        for doc in docs:
            return User.from_dict(doc.id, doc.to_dict())
        return None
    else:
        for uid, data in _USER_STORE.items():
            if data.get('username') == username:
                return User.from_dict(uid, data)
        return None


def get_user_by_email(email):
    """Find user by email."""
    if USE_FIRESTORE:
        docs = db.collection(USERS_COL).where('email', '==', email).limit(1).get()
        for doc in docs:
            return User.from_dict(doc.id, doc.to_dict())
        return None
    else:
        for uid, data in _USER_STORE.items():
            if data.get('email') == email:
                return User.from_dict(uid, data)
        return None
