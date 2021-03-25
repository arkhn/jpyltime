"""Define the Pytest's fixtures for the API's tests."""

import pytest


@pytest.fixture
def client():
    """Fixture for an API client."""
    from fastapi.testclient import TestClient

    from jpyltime.app import app

    return TestClient(app)
