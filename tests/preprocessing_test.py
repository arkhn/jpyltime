import json
from jpyltime.preprocessing_fhir2ds import FHIR2DS_Preprocessing
from jpyltime.utils import Attribute


global attribute_file
attribute_file = "documents/attributes_mapping.json"


def test_update_attributes():    
    attributes = [Attribute(official_name="First name", custom_name="Prénom", anonymize = False), Attribute(official_name="Gender", custom_name="Sexe", anonymize = False), Attribute(official_name="ASAT", custom_name="ASAT", anonymize = False),Attribute(official_name="Potassium", custom_name="Potassium", anonymize = False)]
    d_attributes = {attribute.official_name : attribute for attribute in attributes}

    preprocessing = FHIR2DS_Preprocessing()
    birthdate_condition = "ge2001-01-01"
    birthdate_attribute_name = "Birthdate"
    updated_attributes = preprocessing.update_attributes(d_attributes.copy(), patient_birthdate_condition=birthdate_condition)

    diff_attributes = set(updated_attributes.keys()).difference(set(d_attributes.keys()))
    assert len(diff_attributes) == 2
    assert diff_attributes == {'Identifier', 'Birthdate'}
    assert birthdate_attribute_name in updated_attributes
    assert "Patient.birthdate" in [where_condition["key"] for where_condition in preprocessing.map_attributes[birthdate_attribute_name]["fhir_source"]["where"] ]
    assert birthdate_condition in [where_condition["value"] for where_condition in preprocessing.map_attributes[birthdate_attribute_name]["fhir_source"]["where"] ]



def test_add_practitioner_id():
    attributes = [Attribute(official_name="First name", custom_name="Prénom", anonymize = False), Attribute(official_name="Gender", custom_name="Sexe", anonymize = False), Attribute(official_name="ASAT", custom_name="ASAT", anonymize = False),Attribute(official_name="Potassium", custom_name="Potassium", anonymize = False)]
    d_attributes = {attribute.official_name : attribute for attribute in attributes}
    practioner_attribute_name = "Practitioner"
    practioner_id = "38de92"
    
    preprocessing = FHIR2DS_Preprocessing()
    updated_attributes = preprocessing.update_attributes(d_attributes.copy(), practitioner_id=practioner_id)

    diff_attributes = set(updated_attributes.keys()).difference(set(d_attributes.keys()))
    assert len(diff_attributes) == 2
    assert diff_attributes == {'Identifier', 'Practitioner'}
    assert "Practitioner.id" in [where_condition["key"] for where_condition in preprocessing.map_attributes[practioner_attribute_name]["fhir_source"]["where"] ]
    assert practioner_id in [where_condition["value"] for where_condition in preprocessing.map_attributes[practioner_attribute_name]["fhir_source"]["where"] ] 

    query = preprocessing.generate_sql_query(updated_attributes)
    
    assert f"Practitioner.id = {practioner_id}" in query # Practioner id
    assert "INNER JOIN Practitioner"
    assert "Practitioner.id = Patient.general-practitioner" in query 



def test_simple_query():
    true = """SELECT Patient.name.given FROM Patient"""
    attributes = [Attribute(official_name="First name", custom_name="Prénom", anonymize = False)]
    d_attributes = {attribute.official_name : attribute for attribute in attributes}
    query =FHIR2DS_Preprocessing().generate_sql_query(d_attributes)
    assert true == query


# def test_wrong_attribute(sql_query):
#     with open(attribute_file, "r") as f:
#         map_attributes =  json.loads(f.read())

#     attributes = ["First name", "Sky"]
#     query = FHIR2DS_Preprocessing(map_attributes).generate_sql_query(attributes)


def test_complex_query():
    attributes = [Attribute(official_name="First name", custom_name="Prénom", anonymize = False), Attribute(official_name="Gender", custom_name="Sexe", anonymize = False), Attribute(official_name="ASAT", custom_name="ASAT", anonymize = False),Attribute(official_name="Potassium", custom_name="Potassium", anonymize = False)]
    d_attributes = {attribute.official_name : attribute for attribute in attributes}

    query = FHIR2DS_Preprocessing().generate_sql_query(d_attributes)

    assert "Patient.name.given" in query # First Name
    assert "Patient.gender" in query # Gender
    assert "ASAT.valueQuantity.value" in query # ASAT
    assert "ASAT.valueQuantity.unit" in query # ASAT
    assert "ASAT.code = http://loinc.org%7C1920-8" in query # ASAT
    assert "Potassium.valueQuantity.value" in query # Potassium
    assert "Potassium.valueQuantity.unit" in query # Potassium
    assert "Potassium.code = http://loinc.org%7C2823-3" in query # Potassium


def test_preprocessing():
    attributes = [Attribute(official_name="First name", custom_name="Prénom", anonymize = False), Attribute(official_name="Gender", custom_name="Sexe", anonymize = False), Attribute(official_name="ASAT", custom_name="ASAT", anonymize = False),Attribute(official_name="Potassium", custom_name="Potassium", anonymize = False)]
    d_attributes = {attribute.official_name : attribute for attribute in attributes}

    query, updated_attributes, map_attributes = FHIR2DS_Preprocessing().preprocessing(d_attributes.copy())

    diff_attributes = set(updated_attributes.keys()).difference(set(d_attributes.keys()))
    assert len(diff_attributes) == 1
    assert diff_attributes == {'Identifier'}

    assert "Patient.name.given" in query # First Name
    assert "Patient.gender" in query # Gender
    assert "ASAT.valueQuantity.value" in query # ASAT
    assert "ASAT.valueQuantity.unit" in query # ASAT
    assert "ASAT.code = http://loinc.org%7C1920-8" in query # ASAT
    assert "Potassium.valueQuantity.value" in query # Potassium
    assert "Potassium.valueQuantity.unit" in query # Potassium
    assert "Potassium.code = http://loinc.org%7C2823-3" in query # Potassium