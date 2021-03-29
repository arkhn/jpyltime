from typing import List, Optional, Dict, Any, Tuple
import json

from jpyltime.utils import Attribute


# FIXME Doesn't Fhir2Dataset provide some kind of SDK (a set of functions to build a query)?
# As both jpyltime and F2D are written in python, it's a bit painful to see them communicate via a handwritten string
class FHIR2DS_Preprocessing():
    def __init__(self, attribute_file : str="jpyltime/documents/attributes_mapping.json"):
        """map_attributes: a mapping of Column Name in natural language to FHIR information (resource name, source name and conditions)"""
        with open(attribute_file, "r") as f:
            self.map_attributes =  json.loads(f.read())
        

    def _select(self, attributes: List[str]) -> str:
        """Generate SELECT ... FROM ... condition of the sql query, from a list of attribute names given by the user.
            Always FROM PATIENT"""
        select_attributes = [self.map_attributes[attribute]["fhir_source"]["select"] for attribute in attributes if "select" in self.map_attributes[attribute]["fhir_source"]]
        select_attributes_flatten = [item for attributes in select_attributes for item in attributes]
        return f"SELECT {', '.join(select_attributes_flatten)} FROM Patient"

    def _join(self, attributes: List[str]) -> Optional[str]:
        """Generate INNER JOIN ... ON ... conditions of the sql query, from a list of attribute names given by the user"""
        sql_join = []
        for attribute in attributes:
            if "join" in self.map_attributes[attribute]["fhir_source"]:
                for join_condition in self.map_attributes[attribute]["fhir_source"]["join"]: 
                    sql_join.append(" ".join(["INNER JOIN", self.map_attributes[attribute]["fhir_resource"], "ON" , join_condition["key"], "=" , join_condition["value"]]))
        if not sql_join:
            return ""
        return " ".join(sql_join)


    def _where(self, attributes: List[str]) -> Optional[str]:
        """Generate WHERE ... conditions of the sql query, from a list of attribute names given by the user"""
        where_conditions = []
        for attribute in attributes:
            map_attribute = self.map_attributes[attribute]
            if "where" in map_attribute["fhir_source"]:
                for where_condition in map_attribute["fhir_source"]["where"] :
                    where_conditions.append(" ".join([where_condition["key"], "=", where_condition["value"]]))
        if not where_conditions:
            return ""
        return f"WHERE {' AND '.join(where_conditions)}"


    def _add_group_id_condition(self, group_id: str) :
        """Add a condition on the patient scope when a group id is specified by the user"""
        self.map_attributes["Group"]["fhir_source"]["where"] =[{ 
                    "key": "Group.identifier", 
                    "value": str(group_id)
                    }] 


    def _add_patient_birthdate(self, birthdate_condition: str) :
        """Add a condition on the patient scope when a practioner id is specified by the user"""
        self.map_attributes["Birthdate"]["fhir_source"]["where"] = [{
                        "key": "Patient.birthdate",
                        "value": str(birthdate_condition)
                    }]


    # FIXME I don't think this method is really useful. Is it meant for restricting the resources to which the practitioner has access? If so, I don't think jpyltime should do that
    def update_attributes(self, attributes: Dict[str, Attribute], group_id: Optional[str] = None,  patient_birthdate_condition: Optional[str] = None):
        """Update a dict of attribute given by the user with restriction on the patient scope by specifying a group id and / or a birthdate condition.

        Args:
            attributes (Dict[Attribute]): Dict of attributes that must appear in the SQL query
            group_id (Optional[str]): Group id to restrict the scope of the query to patients from a specific cohort. Defaults to None.
            patient_birthdate_condition (Optional[str]): Condition on the patient birthdate in str format. Ex: ge2000-01-01

        Returns:
            attributes: List of attributes updated with constraints on practioner, birthdate 
        """
        if group_id: 
            self._add_group_id_condition(group_id) 
            if "Group" not in attributes:
                attributes["Group"] = Attribute(official_name="Group",custom_name="Cohort",anonymize=False)
        if patient_birthdate_condition:
            self._add_patient_birthdate(patient_birthdate_condition)
            if "Birthdate" not in attributes:
                attributes["Birthdate"] = Attribute(official_name="Birthdate",custom_name="Birthdate",anonymize=False)
        return attributes


    def _check_attributes_defined(self, attributes: Dict[str, Attribute]):
        """Return an error if some attributes asked by the user are not defined in the fhir mapping dictionary"""
        undefined_attributes = set(attributes.keys()).difference(set(self.map_attributes.keys()))
        if undefined_attributes:
            raise ValueError(f"Undefined attributes {undefined_attributes}, they must be defined in the attributes mapping dictionnary.")

    def generate_sql_query(self, d_attributes : Dict[str,Attribute]) -> str:
        """Generate a SQL query from a list of attribute.

        Args:
            attributes: List of attributes that must appear in the SQL query

        Returns:
            str: SQL query as a string
        """
        attributes = d_attributes.keys()
        sql_select = self._select(attributes)
        sql_join = self._join(attributes)
        sql_where = self._where(attributes)
        sql_query = "\n".join([sql_part for sql_part in [sql_select, sql_join, sql_where] if sql_part])
        return sql_query

    def preprocess(self, attributes: Dict[str, Attribute], group_id:Optional[str]= None, patient_birthdate_condition: Optional[str] = None) -> Tuple[str, Dict[str, Attribute], Dict[str,Any]]:
        """Adapt a list of attributes to generate a correct sql query to request the fhir api

        Args:
            attributes: Dict of Attributes that must appear in the SQL query, given by the user
            practitioner_id (Optional[str]): Practioner id to restrict the scope of the query to specific patient from a practioner. Defaults to None.
            patient_birthdate_condition (Optional[str]): Condition on the patient birthdate in str format. Ex: ge2000-01-01

        Returns:
            Tuple[str, Dict[str, Attribute]]: 
            - sql_query: sql query matching the given attributes and the fhir constraints
            - attributes: Dict of attribute, udapted with preprocessing info (as condition on birthdate and mandatory presence of "Identifier")
            - map_attributes: mapping of Column Name in natural language to FHIR information (resource name, source name and conditions)
        """
        self._check_attributes_defined(attributes)

        attributes = self.update_attributes(attributes, group_id, patient_birthdate_condition)
        sql_query = self.generate_sql_query(attributes)
        return sql_query, attributes, self.map_attributes



