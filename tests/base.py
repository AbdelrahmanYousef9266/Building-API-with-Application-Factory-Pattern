import unittest
from app import create_app, db

# Use SQLite in-memory so tests never touch the production MySQL database
TEST_CONFIG = {
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SECRET_KEY": "test-secret-key",
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 60,
    "RATELIMIT_ENABLED": False,
}


class BaseTestCase(unittest.TestCase):
    """
    Base class for all test cases.
    Creates a fresh in-memory SQLite database before each test
    and tears it down after.
    """

    def setUp(self):
        self.app = create_app(TEST_CONFIG)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
