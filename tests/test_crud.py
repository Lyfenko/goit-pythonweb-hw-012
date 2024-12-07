import unittest
import uuid
from fastapi.testclient import TestClient
from crud import create_user, get_user_by_email
from database import SessionLocal
from schemas import UserCreate
from models import User
from main import app


class TestCRUD(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def generate_random_email(self):
        base_email = "test@example.com"
        unique_id = str(uuid.uuid4())[:8]
        return f"{unique_id}-{base_email}"

    def test_create_user(self):
        user_data = {
            "email": self.generate_random_email(),
            "password": "password123",
            "is_active": True,
            "is_verified": False
        }
        user_create = UserCreate(**user_data)
        user = create_user(self.db, user_create)
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, user_data["email"])

    def test_get_user_by_email(self):
        user_data = {
            "email": self.generate_random_email(),
            "password": "password123",
            "is_active": True,
            "is_verified": False
        }
        user_create = UserCreate(**user_data)
        user = create_user(self.db, user_create)

        retrieved_user = get_user_by_email(self.db, user_data["email"])
        self.assertIsInstance(retrieved_user, User)
        self.assertEqual(retrieved_user.email, user_data["email"])


if __name__ == '__main__':
    unittest.main()
