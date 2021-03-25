"""Test the root to fhir2dataset."""

from typing import List

import pytest
from fastapi.testclient import TestClient

from jpyltime.app import Attribute


@pytest.mark.parametrize("practitioner_id, attributes, patient_ids", [])
def test_fhir2dataset(
    client: TestClient, practitioner_id: str, attributes: List[Attribute], patient_ids: List[str]
):
    """Test a call to to the API of fhir2dataset."""
    response = client.post(
        "/fhir2dataset",
        json={
            "practitioner_id": practitioner_id,
            "attributes": attributes,
            "patient_ids": patient_ids,
        },
    )
    assert response.status_code == 200
