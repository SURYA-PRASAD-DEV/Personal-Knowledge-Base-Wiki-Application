"""
Shared pytest fixtures for the Chiac wiki test suite.
Uses TestingConfig with JSON backend and isolated test data directory.
"""
import sys
import shutil
from pathlib import Path
import pytest

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope='function')
def app():
    """Create a fresh Flask app for each test with TestingConfig."""
    import os
    os.environ['FLASK_CONFIG'] = 'testing'

    # Force JSON backend for tests
    import firebase_module
    original_db = firebase_module.db
    firebase_module.db = None

    import models as models_mod
    models_mod.USE_FIRESTORE = False

    import auth as auth_mod
    auth_mod.USE_FIRESTORE = False

    from app import create_app
    test_app = create_app('testing')

    yield test_app

    # Cleanup: remove test data directory
    from config import TestingConfig
    test_data_dir = Path(TestingConfig.DATA_DIR)
    if test_data_dir.exists():
        shutil.rmtree(test_data_dir)

    # Restore original db
    firebase_module.db = original_db


@pytest.fixture(scope='function')
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def sample_article(app):
    """Create and return a sample article for testing."""
    import models
    article = models.create_article(
        title='Test Article',
        content='<p>This is test content with some keywords for searching.</p>',
        tags=['test', 'sample'],
        created_by='testuser',
    )
    return article


@pytest.fixture(scope='function')
def sample_user(app):
    """Register a sample user and return (user, password)."""
    from auth import create_user
    password = 'testpassword123'
    user = create_user('testuser', 'test@example.com', password)
    return user, password


@pytest.fixture(scope='function')
def logged_in_client(client, sample_user):
    """A test client that is already logged in."""
    user, password = sample_user
    client.post('/login', data={
        'username': user.username,
        'password': password,
    }, follow_redirects=True)
    return client
