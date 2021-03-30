"""Define the Pytest's fixtures for the API's tests."""

import pytest

from jpyltime.utils import Attribute


@pytest.fixture
def client():
    """Fixture for an API client."""
    from fastapi.testclient import TestClient

    from jpyltime.app import app

    return TestClient(app)


@pytest.fixture
def attributes():
    attributes = [
        Attribute(official_name="First name", custom_name="Prénom", anonymize=False),
        Attribute(official_name="Weight", custom_name="Poids", anonymize=False),
        Attribute(official_name="Medication", custom_name="Médicaments", anonymize=False),
        Attribute(official_name="Birthdate", custom_name="Anniversaire", anonymize=True),
    ]
    requested_attributes = {attribute.official_name: attribute for attribute in attributes}
    return requested_attributes
