import json
import pandas as pd
from jpyltime.postprocessing_fhir2ds import FHIR2DS_Postprocessing
from jpyltime.utils import Attribute


global attribute_file
attribute_file = "documents/attributes_mapping.json"

def example_dataframe():
    data = [[["8392"], 'tom', 10,"ICD", 22, "mg", 50, "kg", "2019-20-20"], [["8392"], 'tom', 1, "ICD",8493, "L", 50, "kg"], [["8392"], 'nick', 10,"ICD", 22, "mg", 90, "kg"], [["9382"], 'julie', 1,"ICD", 38, "L", 92, "kg"], [["3728"],'john', 10, "ICD",22, "mg" ,20, "kg"]]   
    # Create the pandas DataFrame 
    df = pd.DataFrame(data, columns = ["Patient.identifier.value", 'Patient.name.given', 'MedicationRequest:from_id', "MedicationRequest.medicationCodeableConcept.coding.display",'MedicationRequest.dosageInstruction.doseAndRate.doseQuantity.value','MedicationRequest.dosageInstruction.doseAndRate.doseQuantity.unit',
        'Weight.valueQuantity.value',
        'Weight.valueQuantity.unit', 'Patient.birthDate'])
    return df

def test_postprocessing():
    df = example_dataframe()
    attributes = [Attribute(official_name="Identifier", custom_name="PatientID", anonymize = False),Attribute(official_name="First name", custom_name="Prénom", anonymize = False), Attribute(official_name="Weight", custom_name="Poids", anonymize = False), Attribute(official_name="Medication", custom_name="Médicaments", anonymize = False),Attribute(official_name="Birthdate", custom_name="Anniversaire", anonymize = True)]
    d_attributes = {attribute.official_name : attribute for attribute in attributes}
    patient_ids = ["8392", "9382"]

    with open(attribute_file, "r") as f:
        map_attributes =  json.loads(f.read())
    anonymization_symbol= "*"
    postprocessing = FHIR2DS_Postprocessing(map_attributes, anonymization_symbol=anonymization_symbol)
    display_df = postprocessing.postprocessing(df, d_attributes, patient_ids)

    assert len(display_df) == 2
    assert display_df["PatientID"].is_unique 
    assert display_df.iloc[0]["Prénom"] == {"tom", "nick"}
    assert display_df.iloc[0]["Poids"] == {"90 kg", "50 kg"}
    assert all(display_df[display_df["Anniversaire"] ==  anonymization_symbol])
