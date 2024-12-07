import unittest
from models import Contact, User


class TestModels(unittest.TestCase):
    def test_user_password_hashing(self):
        password = "password123"
        user = User(email="test@example.com")
        user.set_password(password)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_contact_creation(self):
        contact = Contact(name="John", surname="Doe", email="john.doe@example.com")
        self.assertEqual(contact.name, "John")
        self.assertEqual(contact.surname, "Doe")
        self.assertEqual(contact.email, "john.doe@example.com")


if __name__ == '__main__':
    unittest.main()
