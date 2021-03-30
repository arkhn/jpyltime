import json

import pytest

from jpyltime.preprocessing_fhir2ds import FHIR2DS_Preprocessing
from jpyltime.utils import Attribute


def test_add_group_id(attributes):
    group_attribute_name = "Group"
    group_id = "38de92"

    preprocessing = FHIR2DS_Preprocessing(group_id=group_id)
    query = preprocessing.generate_sql_query(attributes)

    assert f"Group.identifier = {group_id}" in query  # Group id
    assert "INNER JOIN Group ON Group.member = Patient._id" in query


def test_simple_query():
    true = """SELECT Patient.name.given FROM Patient"""
    attributes = [Attribute(official_name="First name", custom_name="Prénom", anonymize=False)]
    requested_attributes = {attribute.official_name: attribute for attribute in attributes}
    query = FHIR2DS_Preprocessing().generate_sql_query(requested_attributes)
    assert true == query


def test_complex_query(attributes):
    query = FHIR2DS_Preprocessing().generate_sql_query(attributes)
    true = """SELECT Patient.name.given, Weight.valueQuantity.value, Weight.valueQuantity.unit, MedicationRequest.medicationCodeableConcept.coding.display, MedicationRequest.dosageInstruction.doseAndRate.doseQuantity.value, MedicationRequest.dosageInstruction.doseAndRate.doseQuantity.unit, Patient.birthDate FROM Patient INNER JOIN Observation as Weight ON Weight.subject = Patient._id INNER JOIN MedicationRequest ON MedicationRequest.subject = Patient._id WHERE Weight.code = http://loinc.org%7C29463-7"""
    assert query == true


def test_preprocessing(attributes):
    query, map_attributes = FHIR2DS_Preprocessing().preprocess(attributes.copy())
    true = """SELECT Patient.name.given, Weight.valueQuantity.value, Weight.valueQuantity.unit, MedicationRequest.medicationCodeableConcept.coding.display, MedicationRequest.dosageInstruction.doseAndRate.doseQuantity.value, MedicationRequest.dosageInstruction.doseAndRate.doseQuantity.unit, Patient.birthDate FROM Patient INNER JOIN Observation as Weight ON Weight.subject = Patient._id INNER JOIN MedicationRequest ON MedicationRequest.subject = Patient._id WHERE Weight.code = http://loinc.org%7C29463-7"""
    assert query == true
