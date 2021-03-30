import json

import pytest

from jpyltime.preprocessing_fhir2ds import FHIR2DS_Preprocessing
from jpyltime.utils import Attribute


@pytest.fixture
def requested_attributes():
    attributes = [
        Attribute(official_name="First name", custom_name="Prénom", anonymize=False),
        Attribute(official_name="Gender", custom_name="Sexe", anonymize=False),
        Attribute(official_name="ASAT", custom_name="ASAT", anonymize=False),
        Attribute(official_name="Potassium", custom_name="Potassium", anonymize=False),
    ]
    requested_attributes = {attribute.official_name: attribute for attribute in attributes}
    return requested_attributes


def test_add_group_id(requested_attributes):
    group_attribute_name = "Group"
    group_id = "38de92"

    preprocessing = FHIR2DS_Preprocessing(group_id=group_id)
    query = preprocessing.generate_sql_query(requested_attributes)

    assert f"Group.identifier = {group_id}" in query  # Group id
    assert "INNER JOIN Group ON Group.member = Patient.id" in query


def test_simple_query(requested_attributes):
    true = """SELECT Patient.name.given FROM Patient"""
    attributes = [Attribute(official_name="First name", custom_name="Prénom", anonymize=False)]
    requested_attributes = {attribute.official_name: attribute for attribute in attributes}
    query = FHIR2DS_Preprocessing().generate_sql_query(requested_attributes)
    assert true == query


def test_complex_query(requested_attributes):
    query = FHIR2DS_Preprocessing().generate_sql_query(requested_attributes)

    true = """SELECT Patient.name.given, Patient.gender, ASAT.valueQuantity.value, ASAT.valueQuantity.unit, Potassium.valueQuantity.value, Potassium.valueQuantity.unit FROM Patient INNER JOIN Observation as ASAT ON ASAT.subject = Patient.id INNER JOIN Observation as Potassium ON Potassium.subject = Patient.id WHERE ASAT.code = http://loinc.org%7C1920-8 AND Potassium.code = http://loinc.org%7C2823-3"""
    assert query.split() == true.split()


def test_preprocessing(requested_attributes):
    query, map_attributes = FHIR2DS_Preprocessing().preprocess(requested_attributes.copy())

    true = """SELECT Patient.name.given, Patient.gender, ASAT.valueQuantity.value, ASAT.valueQuantity.unit, Potassium.valueQuantity.value, Potassium.valueQuantity.unit FROM Patient INNER JOIN Observation as ASAT ON ASAT.subject = Patient.id INNER JOIN Observation as Potassium ON Potassium.subject = Patient.id WHERE ASAT.code = http://loinc.org%7C1920-8 AND Potassium.code = http://loinc.org%7C2823-3"""
    assert query.split() == true.split()
