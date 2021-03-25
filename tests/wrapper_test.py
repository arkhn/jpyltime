import pandas as pd
from jpyltime.wrapper_fhir2ds import Wrapper_FHIR2DS

def example_dataframe():
    data = [["8392", 'tom', 10,"ICD", 22, "mg", 50, "kg", "2019-20-20"], ["8392", 'tom', 1, "ICD",8493, "L", 50, "kg"], ["8392", 'nick', 10,"ICD", 22, "mg", 90, "kg"], ["3829", 'julie', 1,"ICD", 38, "L", 92, "kg"], ["98329",'john', 10, "ICD",22, "mg" ,20, "kg"]]   
    # Create the pandas DataFrame 
    df = pd.DataFrame(data, columns = ["Patient.identifier", 'Patient.name.given', 'MedicationRequest:from_id', "MedicationRequest.medicationCodeableConcept.coding.display",'MedicationRequest.dosageInstruction.doseAndRate.doseQuantity.value','MedicationRequest.dosageInstruction.doseAndRate.doseQuantity.unit',
        'Weight.valueQuantity.value',
        'Weight.valueQuantity.unit', 'Patient.birthDate'])
    return df

def test_wrapper_preprocessing():
    wrapper = Wrapper_FHIR2DS()
    attributes = ["First name",  "Weight", "Medication", "Identifier"]
    attributes, wrapper.map_attributes = wrapper.preprocessing.update_attributes(attributes, patient_birthdate_condition="ge2001-01-01")
    query = wrapper.preprocessing.generate_sql_query(attributes)

    select_cols = ["Patient.name.given", "Weight.valueQuantity.value", "Weight.valueQuantity.unit", "Patient.identifier","Patient.birthDate", "Patient.birthDate" ]
    assert sum([col in query for col in select_cols ]) == len(select_cols)
    assert "INNER JOIN Observation as Weight ON Weight.subject = Patient.id" in query
    assert "INNER JOIN MedicationRequest ON MedicationRequest.subject = Patient.id" in query
    assert "Weight.code = http://loinc.org%7C29463-7" in query
    assert "Patient.birthdate = ge2001-01-01" in query

def test_wrapper_postprocessing():
    df = example_dataframe()
    attributes = ["First name",  "Weight", "Medication", "Identifier", "Birthdate"]

    wrapper = Wrapper_FHIR2DS()
    display_df = wrapper.postprocessing.improve_display(df, attributes)

    assert display_df[wrapper.identifier_attribute_name].is_unique
    assert display_df["Weight"][1] == ["50 kg", "50 kg", "90 kg"]
    assert display_df["Medication"][1] == ["ICD 22 mg", "ICD 8493 L", "ICD 22 mg"]
    assert display_df["Birthdate"][0] ==  []
    assert display_df["Birthdate"][1] ==  ["2019-20-20"]


def test_pipeline():

    wrapper = Wrapper_FHIR2DS()
    attributes = ["First name",  "Weight", "Medication", "Identifier"]
    attributes, wrapper.map_attributes = wrapper.preprocessing.update_attributes(attributes, patient_birthdate_condition="ge2001-01-01")
    query = wrapper.preprocessing.generate_sql_query(attributes)

    select_cols = ["Patient.name.given", "Weight.valueQuantity.value", "Weight.valueQuantity.unit", "Patient.identifier","Patient.birthDate", "Patient.birthDate" ]
    assert sum([col in query for col in select_cols ]) == len(select_cols)
    assert "INNER JOIN Observation as Weight ON Weight.subject = Patient.id" in query
    assert "INNER JOIN MedicationRequest ON MedicationRequest.subject = Patient.id" in query
    assert "Weight.code = http://loinc.org%7C29463-7" in query
    assert "Patient.birthdate = ge2001-01-01" in query

    # TODO : replace with test API 
    df = example_dataframe()

    display_df = wrapper.postprocessing.improve_display(df, attributes)

    assert display_df[wrapper.identifier_attribute_name].is_unique
    assert display_df["Weight"][1] == ["50 kg", "50 kg", "90 kg"]
    assert display_df["Medication"][1] == ["ICD 22 mg", "ICD 8493 L", "ICD 22 mg"]
    assert display_df["Birthdate"][0] ==  []
    assert display_df["Birthdate"][1] ==  ["2019-20-20"]

