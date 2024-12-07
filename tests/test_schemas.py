import unittest
from datetime import date
from pydantic import ValidationError
from schemas import UserCreate, ContactCreate


class TestSchemas(unittest.TestCase):
    def test_user_create_schema(self):
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "is_active": True,
            "is_verified": False
        }
        user_create = UserCreate(**user_data)
        self.assertEqual(user_create.email, "test@example.com")
        self.assertEqual(user_create.password, "password123")
        self.assertTrue(user_create.is_active)
        self.assertFalse(user_create.is_verified)

        # Test invalid email
        user_data["email"] = "invalid_email"
        with self.assertRaises(ValidationError):
            UserCreate(**user_data)

    def test_contact_create_schema(self):
        contact_data = {
            "name": "John",
            "surname": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "birthday": date(1990, 1, 1),
            "additional_data": "Additional data"
        }
        contact_create = ContactCreate(**contact_data)
        self.assertEqual(contact_create.name, "John")
        self.assertEqual(contact_create.surname, "Doe")
        self.assertEqual(contact_create.email, "john.doe@example.com")
        self.assertEqual(contact_create.phone, "1234567890")
        self.assertEqual(contact_create.birthday, date(1990, 1, 1))
        self.assertEqual(contact_create.additional_data, "Additional data")


if __name__ == '__main__':
    unittest.main()
