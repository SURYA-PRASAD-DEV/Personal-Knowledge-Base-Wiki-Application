import os
import logging
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).parent


class Config:
    """Base configuration shared by all environments."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    FIREBASE_CREDENTIALS = os.environ.get(
        'FIREBASE_CREDENTIALS', str(BASE_DIR / 'serviceAccountKey.json')
    )
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', '')

    SEARCH_INDEX_DIR = str(BASE_DIR / 'data' / 'search_index')
    DATA_DIR = str(BASE_DIR / 'data')

    LOG_LEVEL = logging.INFO
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = logging.WARNING


class TestingConfig(Config):
    """Testing configuration — uses isolated test data directory."""
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test-secret-key'
    DATA_DIR = str(BASE_DIR / 'data_test')
    SEARCH_INDEX_DIR = str(BASE_DIR / 'data_test' / 'search_index')
    USE_FIRESTORE = False


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
