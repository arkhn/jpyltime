import json

from jpyltime.postprocessing_fhir2ds import FHIR2DS_Postprocessing
from jpyltime.preprocessing_fhir2ds import FHIR2DS_Preprocessing 
from typing import List, Optional

class Wrapper_FHIR2DS():
    def __init__(self, attribute_file : str = "documents/attributes_mapping.json"):
        """Load a mapping of Column Name in natural language to FHIR information (resource name, source name, conditions and display)"""
        with open(attribute_file, "r") as f:
            self.map_attributes =  json.loads(f.read())
        
        self.identifier_attribute_name = "Identifier"
        if self.identifier_attribute_name not in self.map_attributes.keys():
           raise ValueError(f"Undefined Patient ID attribute {self.identifier_attribute_name}, it must be defined in the attribute mapping dictionnary.")

        self.preprocessing = FHIR2DS_Preprocessing(self.map_attributes)
        # TODO 
        # self.api = 
        self.postprocessing = FHIR2DS_Postprocessing(self.map_attributes, self.identifier_attribute_name)


    def _api(self, sql_query: str):
        pass


    def _check_attributes_defined(self, attributes: List[str]):
        """Return an error if some attributes asked by the user are not defined in the fhir mapping dictionary"""
        undefined_attributes = set(attributes).difference(set(self.map_attributes.keys()))
        if undefined_attributes:
           raise ValueError(f"Undefined attributes {undefined_attributes}, they must be defined in the attributes mapping dictionnary.")

    def pipeline(self, attributes : List[str],practitioner_id:Optional[str], group_id:Optional[List[str]], patient_birthdate_condition:Optional[str],merge_on_col: str):
        """Full wrapper pipeline for FHIR2Dataset:
            - Check given attributes are valid
            - Update given attributes with constraints on practioner, patient group and birthdate condition
            - Generate sql query based on attributes and constraints
            - // run api on generated sql query //
            - Postprocess dataframe to filter by patient group and improve display 

        Args:
            attributes: List of attributes that must appear in the SQL query
            practitioner_id (Optional[str]): Practioner id to restrict the scope of the query to specific patient from a practioner. Defaults to None.
            patient_birthdate_condition (Optional[str]): Condition on the patient birthdate in str format. Ex: ge2000-01-01
            group_id (Optional[str]): Group id to restrict the scope of the query to specific patient from a group. Defaults to None.
            merge_on_col: Name of the column to groupby the final data. By default Patient ID.

        Returns:
            Well formatted DataFrame, ready to be displayed
        """
        self._check_attributes_defined(attributes)
        
        # Add a select condition on Patient Identifier to every sql query 
        if self.identifier_attribute_name not in attributes :
            attributes.append(self.identifier_attribute_name) 

        attributes, self.map_attributes = self.preprocessing.update_attributes(attributes, practitioner_id, patient_birthdate_condition)
        sql_query = self.preprocessing.generate_sql_query(attributes)

        # TODO 
        sql_df = self._api(sql_query)
        
        display_df = self.postprocessing.improve_display(sql_df, attributes, self.identifier_attribute_name, group_id)
        return display_df

    
