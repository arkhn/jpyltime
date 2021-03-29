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



def test_add_group_id():
    attributes = [Attribute(official_name="First name", custom_name="Prénom", anonymize = False), Attribute(official_name="Gender", custom_name="Sexe", anonymize = False), Attribute(official_name="ASAT", custom_name="ASAT", anonymize = False),Attribute(official_name="Potassium", custom_name="Potassium", anonymize = False)]
    d_attributes = {attribute.official_name : attribute for attribute in attributes}
    group_attribute_name = "Group"
    group_id = "38de92"
    
    preprocessing = FHIR2DS_Preprocessing()
    updated_attributes = preprocessing.update_attributes(d_attributes.copy(), group_id=group_id)

    diff_attributes = set(updated_attributes.keys()).difference(set(d_attributes.keys()))
    assert len(diff_attributes) == 2
    assert diff_attributes == {'Identifier', 'Group'}
    assert "Group.id" in [where_condition["key"] for where_condition in preprocessing.map_attributes[group_attribute_name]["fhir_source"]["where"] ]
    assert group_id in [where_condition["value"] for where_condition in preprocessing.map_attributes[group_attribute_name]["fhir_source"]["where"] ] 

    query = preprocessing.generate_sql_query(updated_attributes)
    
    assert f"Group.id = {group_id}" in query # Group id
    assert "INNER JOIN Group ON Group.member = Patient.id" in query



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

    true = """SELECT Patient.name.given, Patient.gender, ASAT.valueQuantity.value, ASAT.valueQuantity.unit, Potassium.valueQuantity.value, Potassium.valueQuantity.unit FROM Patient INNER JOIN Observation as ASAT ON ASAT.subject = Patient.id INNER JOIN Observation as Potassium ON Potassium.subject = Patient.id WHERE ASAT.code = http://loinc.org%7C1920-8 AND Potassium.code = http://loinc.org%7C2823-3"""
    assert query.split() == true.split()

def test_preprocessing():
    attributes = [Attribute(official_name="First name", custom_name="Prénom", anonymize = False), Attribute(official_name="Gender", custom_name="Sexe", anonymize = False), Attribute(official_name="ASAT", custom_name="ASAT", anonymize = False),Attribute(official_name="Potassium", custom_name="Potassium", anonymize = False)]
    d_attributes = {attribute.official_name : attribute for attribute in attributes}

    query, updated_attributes, map_attributes = FHIR2DS_Preprocessing().preprocess(d_attributes.copy())

    diff_attributes = set(updated_attributes.keys()).difference(set(d_attributes.keys()))
    assert len(diff_attributes) == 1
    assert diff_attributes == {'Identifier'}
    
    true = """SELECT Patient.name.given, Patient.gender, ASAT.valueQuantity.value, ASAT.valueQuantity.unit, Potassium.valueQuantity.value, Potassium.valueQuantity.unit, Patient.identifier.value FROM Patient INNER JOIN Observation as ASAT ON ASAT.subject = Patient.id INNER JOIN Observation as Potassium ON Potassium.subject = Patient.id WHERE ASAT.code = http://loinc.org%7C1920-8 AND Potassium.code = http://loinc.org%7C2823-3"""
    assert query.split() == true.split()