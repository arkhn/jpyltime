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
        ["8392", "tom", 1, "ICD", 8493, "L", 50, "kg", "2019-20-20"],
        ["2038", "nick", 10, "ICD", 22, "mg", 90, "kg", "2019-03-23"],
        ["9382", "julie", 1, "ICD", 38, "L", 92, "kg", "1300-05-17"],
        ["3728", "john", 10, "ICD", 22, "mg", 20, "kg", "2839-11-20"],
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


def test_postprocessing(map_attributes, example_dataframe, attributes):
    anonymization_symbol = "*"
    postprocessing = FHIR2DS_Postprocessing(
        map_attributes, anonymization_symbol=anonymization_symbol
    )
    display_df = postprocessing.postprocess(example_dataframe, attributes)
    expected_columns = ["Prénom", "Anniversaire", "Poids", "Médicaments"]
    expected = pd.DataFrame(
        [
            ["*", "2019-03-23", ["90 kg"], ["ICD 22 mg"]],
            ["*", "2839-11-20", ["20 kg"], ["ICD 22 mg"]],
            ["*", "2019-20-20", ["50 kg", "50 kg"], ["ICD 22 mg", "ICD 8493 L"]],
            ["*", "1300-05-17", ["92 kg"], ["ICD 38 L"]],
        ],
        columns=expected_columns,
    )

    assert expected.equals(display_df)
