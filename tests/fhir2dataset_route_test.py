"""Test the root to fhir2dataset."""

from typing import List

import pytest
from fastapi.testclient import TestClient

from jpyltime.app import Attribute


@pytest.mark.parametrize("practitioner_id, attributes, group_id", [])
def test_fhir2dataset(
    client: TestClient, practitioner_id: str, attributes: List[Attribute], group_id: str
):
    """Test a call to to the API of fhir2dataset."""
    response = client.post(
        "/fhir2dataset",
        json={
            "practitioner_id": practitioner_id,
            "attributes": attributes,
            "group_id": group_id,
        },
    )
    assert response.status_code == 200
