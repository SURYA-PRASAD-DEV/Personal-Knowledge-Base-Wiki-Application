"""
Firebase Firestore initialization module.
Safely loads credentials from a local service account JSON file.
If credentials are missing or firebase_admin is not installed,
runs without Firestore (file fallback in models.py).
"""
import os
import logging

logger = logging.getLogger(__name__)

db = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from config import Config

    cred_path = os.path.abspath(Config.FIREBASE_CREDENTIALS)
    logger.info('Looking for Firebase credentials at %s', cred_path)

    if os.path.exists(cred_path):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)

            db = firestore.client()
            logger.info('Firestore client created')
        except Exception as e:
            logger.exception('Firebase initialization failed: %s', e)
            db = None
    else:
        logger.warning('Service account JSON not found at %s; running without Firestore', cred_path)
        db = None

except ImportError:
    logger.info('firebase_admin not installed; running with JSON file backend')
    db = None
except Exception as e:
    logger.exception('Unexpected error during Firebase setup: %s', e)
    db = None
