import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_create_user(client):
    # Test the create_user route
    response = client.post("/users/", json={"email": "test@example.com", "password": "password"})
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main(["-vv", "-s", "--cov=.", "--cov-report=html"])
