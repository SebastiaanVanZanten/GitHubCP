import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Provides a TestClient instance for testing the FastAPI app.
    The app uses in-memory activities, so each test gets a fresh state.
    """
    return TestClient(app)
