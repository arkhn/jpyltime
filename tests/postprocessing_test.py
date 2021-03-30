import json

import pandas as pd
import pytest

from jpyltime.postprocessing_fhir2ds import FHIR2DS_Postprocessing
from jpyltime.utils import Attribute


@pytest.fixture
def map_attributes():
    attribute_file = "jpyltime/documents/attributes_mapping.json"
    with open(attribute_file, "r") as f:
        map_attributes = json.loads(f.read())
    return map_attributes


@pytest.fixture
def example_dataframe():
    data = [
        ["8392", "tom", 10, "ICD", 22, "mg", 50, "kg", "2019-20-20"],
        ["8392", "tom", 1, "ICD", 8493, "L", 50, "kg"],
        ["8392", "nick", 10, "ICD", 22, "mg", 90, "kg"],
        ["9382", "julie", 1, "ICD", 38, "L", 92, "kg"],
        ["3728", "john", 10, "ICD", 22, "mg", 20, "kg"],
    ]
    # Create the pandas DataFrame
    df = pd.DataFrame(
        data,
        columns=[
            "Patient:from_id",
            "Patient.name.given",
            "MedicationRequest:from_id",
            "MedicationRequest.medicationCodeableConcept.coding.display",
            "MedicationRequest.dosageInstruction.doseAndRate.doseQuantity.value",
            "MedicationRequest.dosageInstruction.doseAndRate.doseQuantity.unit",
            "Weight.valueQuantity.value",
            "Weight.valueQuantity.unit",
            "Patient.birthDate",
        ],
    )
    return df


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


def test_postprocessing(map_attributes, example_dataframe, attributes):
    anonymization_symbol = "*"
    postprocessing = FHIR2DS_Postprocessing(
        map_attributes, anonymization_symbol=anonymization_symbol
    )
    display_df = postprocessing.postprocess(example_dataframe, attributes)

    true_columns = ["Patient:from_id", "Prénom", "Poids", "Médicaments", "Anniversaire"]
    true = pd.DataFrame(
        [
            ["3728", {"john"}, {"20 kg"}, {"ICD 22 mg"}, "*"],
            ["8392", {"tom", "nick"}, {"50 kg", "90 kg"}, {"ICD 8493 L", "ICD 22 mg"}, "*"],
            ["9382", {"julie"}, {"92 kg"}, {"ICD 38 L"}, "*"],
        ],
        columns=true_columns,
    )

    assert true.equals(display_df)
