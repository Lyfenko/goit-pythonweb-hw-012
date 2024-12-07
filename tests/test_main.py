import unittest
from fastapi.testclient import TestClient
from main import app


class TestMain(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        pass

    def test_create_user(self):
        user_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        response = self.client.post("/users/", json=user_data)
        self.assertEqual(response.status_code, 200)

    def test_create_user_duplicate_email(self):
        user_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        self.client.post("/users/", json=user_data)
        response = self.client.post("/users/", json=user_data)
        self.assertEqual(response.status_code, 409)

    def test_login_for_access_token(self):
        login_data = {
            "username": "test@example.com",
            "password": "testpassword"
        }
        response = self.client.post("/token/", data=login_data)
        self.assertEqual(response.status_code, 200)

    def test_login_for_access_token_invalid_credentials(self):
        login_data = {
            "username": "test@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post("/token/", data=login_data)
        self.assertEqual(response.status_code, 401)

    def test_get_user_profile(self):
        user_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        self.client.post("/users/", json=user_data)
        login_data = {
            "username": "test@example.com",
            "password": "testpassword"
        }
        login_response = self.client.post("/token/", data=login_data)
        access_token = login_response.json().get("access_token")
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.get("/users/me/", headers=headers)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
