"""Define fixtures for pytest."""
from fastapi.testclient import TestClient
import pytest


@pytest.fixture(scope="session", name="test_client")
def get_test_client():
    """Return the FastAPI test client, which is shared for each session."""
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session", name="admin_auth_headers")
def get_admin_auth_headers(test_client):
    """Return the authorization header with authority of a GROUP_ADMIN, which is shared for each session."""
    access_token = get_access_token(test_client, username="admin@group.com", password="secret")
    return {"Authorization": f"Bearer {access_token}"}


def get_access_token(test_client, username: str, password: str):
    """Login to specified account and return an access_token."""
    login_payload = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }
    response = test_client.post(
        "/ems-enterprise-ai/v1/auth/login",
        data=login_payload
    )
    access_token = response.json()["access_token"]
    return access_token