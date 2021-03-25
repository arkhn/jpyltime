import json
from jpyltime.preprocessing_fhir2ds import FHIR2DS_Preprocessing


global attribute_file
attribute_file = "documents/attributes_mapping.json"


def test_update_attributes():    
    with open(attribute_file, "r") as f:
        map_attributes =  json.loads(f.read())

    attributes = ["First name", "Gender", "ASAT", "Potassium"]

    preprocessing = FHIR2DS_Preprocessing(map_attributes)
    birthdate_condition = "ge2001-01-01"
    birthdate_attribute_name = "Birthdate"
    updated_attributes, updated_map_attributes = preprocessing.update_attributes(attributes[:], patient_birthdate_condition=birthdate_condition)

    assert len(updated_attributes) == len(attributes) + 1
    assert birthdate_attribute_name in updated_attributes
    assert "Patient.birthdate" in [where_condition["key"] for where_condition in updated_map_attributes[birthdate_attribute_name]["fhir_source"]["where"] ]
    assert birthdate_condition in [where_condition["value"] for where_condition in updated_map_attributes[birthdate_attribute_name]["fhir_source"]["where"] ]



def test_add_practitioner_id():
    with open(attribute_file, "r") as f:
        map_attributes =  json.loads(f.read())

    attributes = ["First name", "Gender", "ASAT", "Potassium"]
    practioner_attribute_name = "Practitioner"
    practioner_id = "38de92"
    
    preprocessing = FHIR2DS_Preprocessing(map_attributes)
    updated_attributes, updated_map_attributes = preprocessing.update_attributes(attributes[:], practitioner_id=practioner_id)

    assert len(updated_attributes) == len(attributes) + 1
    assert practioner_attribute_name in updated_attributes
    assert "Practitioner.id" in [where_condition["key"] for where_condition in updated_map_attributes[practioner_attribute_name]["fhir_source"]["where"] ]
    assert practioner_id in [where_condition["value"] for where_condition in updated_map_attributes[practioner_attribute_name]["fhir_source"]["where"] ] 

    query = preprocessing.generate_sql_query(updated_attributes)
    
    assert f"Practitioner.id = {practioner_id}" in query # Practioner id
    assert "INNER JOIN Practitioner"
    assert "Practitioner.id = Patient.general-practitioner" in query 



def test_simple_query():
    with open(attribute_file, "r") as f:
        map_attributes =  json.loads(f.read())

    true = """SELECT Patient.name.given FROM Patient"""
    attributes = ["First name"]
    query =FHIR2DS_Preprocessing(map_attributes).generate_sql_query(attributes)
    assert true == query


# def test_wrong_attribute(sql_query):
#     with open(attribute_file, "r") as f:
#         map_attributes =  json.loads(f.read())

#     attributes = ["First name", "Sky"]
#     query = FHIR2DS_Preprocessing(map_attributes).generate_sql_query(attributes)


def test_complex_query():
    with open(attribute_file, "r") as f:
        map_attributes =  json.loads(f.read())

    attributes = ["First name", "Gender", "ASAT", "Potassium"]

    query = FHIR2DS_Preprocessing(map_attributes).generate_sql_query(attributes)
    print(query)
    assert "Patient.name.given" in query # First Name
    assert "Patient.gender" in query # Gender
    assert "ASAT.valueQuantity.value" in query # ASAT
    assert "ASAT.valueQuantity.unit" in query # ASAT
    assert "ASAT.code = http://loinc.org%7C1920-8" in query # ASAT
    assert "Potassium.valueQuantity.value" in query # Potassium
    assert "Potassium.valueQuantity.unit" in query # Potassium
    assert "Potassium.code = http://loinc.org%7C2823-3" in query # Potassium




