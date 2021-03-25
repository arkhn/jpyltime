from typing import List, Optional, Dict, Any, Tuple
import json

where_keyword = "WHERE "
select_keyword = "SELECT "
from_keyword = "FROM "
join_keyword = "INNER JOIN"
on_keyword = "ON"
equal_keyword = "="
and_keyword = "AND "

class FHIR2DS_Preprocessing():
    def __init__(self, map_attributes : Dict[str, Any]):
        """map_attributes: a mapping of Column Name in natural language to FHIR information (resource name, source name and conditions)"""
        self.map_attributes = map_attributes


    def _select(self,attributes: List[str]) -> str:
        """Generate SELECT ... FROM ... condition of the sql query, from a list of attribute names given by the user"""
        select_attributes = [self.map_attributes[attribute]["fhir_source"]["select"] for attribute in attributes if "select" in self.map_attributes[attribute]["fhir_source"]]
        select_attributes_flatten = [item for attributes in select_attributes for item in attributes]
        return select_keyword + ", \n".join(select_attributes_flatten) + "\n" + from_keyword +  self.map_attributes[attributes[0]]["fhir_resource"] 

    def _join(self, attributes: List[str]) -> Optional[str]:
        """Generate INNER JOIN ... ON ... conditions of the sql query, from a list of attribute names given by the user"""
        sql_join = []
        for attribute in attributes:
            if "join" in self.map_attributes[attribute]["fhir_source"]:
                for join_condition in self.map_attributes[attribute]["fhir_source"]["join"]: 
                    sql_join.append(" ".join([join_keyword,self.map_attributes[attribute]["fhir_resource"],on_keyword , join_condition["key"],equal_keyword, join_condition["value"]]))
        if not sql_join:
            return ""
        return "\n".join(sql_join)


    def _where(self, attributes: List[str]) -> Optional[str]:
        """Generate WHERE ... conditions of the sql query, from a list of attribute names given by the user"""
        where_conditions = []
        for attribute in attributes:
            map_attribute = self.map_attributes[attribute]
            if "where" in map_attribute["fhir_source"]:
                for where_condition in map_attribute["fhir_source"]["where"] :
                    where_conditions.append(" ".join([where_condition["key"],equal_keyword,where_condition["value"]]))
        if not where_conditions:
            return ""
        return where_keyword +("\n"+and_keyword).join(where_conditions)


    def _add_practitionner_id_condition(self, practitioner_id: str) :
        """Add a condition on the patient scope when a practioner id is specified by the user"""
        self.map_attributes["Practitioner"] = {
            'fhir_resource': 'Practitioner',
            'fhir_source': { 
                "join": [{ 
                    "key": "Practitioner.id", 
                    "value": "Patient.general-practitioner" 
                    }],
                "where": [{ 
                    "key": "Practitioner.id", 
                    "value": str(practitioner_id)
                    }] 
                } 
            }  
                
    def _add_patient_birthdate(self, birthdate_condition: str) :
        """Add a condition on the patient scope when a practioner id is specified by the user"""
        self.map_attributes["Birthdate"]["fhir_source"]["where"] = [{
                        "key": "Patient.birthdate",
                        "value": str(birthdate_condition)
                    }]

    def update_attributes(self, attributes: List[str], practitioner_id: Optional[str] = None, group_id: Optional[str]=None, patient_birthdate_condition: Optional[str] = None) -> Tuple[List[str], Dict]:
        """Update a list of attribute names given by the user with restriction on the patient scope by specifying a practioner id, a group id and / or a birthdate condition.

        Args:
            attributes (List[str]): List of attributes that must appear in the SQL query
            practitioner_id (Optional[str]): Practioner id to restrict the scope of the query to specific patient from a practioner. Defaults to None.
            group_id (Optional[str]): Group id to restrict the scope of the query to specific patient from a group. Defaults to None.
            patient_birthdate_condition (Optional[str]): Condition on the patient birthdate in str format. Ex: ge2000-01-01

        Returns:
            attributes: List of attributes updated with constraints on practioner, birthdate and group
        """
        if practitioner_id: 
            self._add_practitionner_id_condition(practitioner_id) 
            attributes.append("Practitioner")
        # TODO: condition on group_id (How is define a group of patient?)
        # if group_id:
            # self._add_group_id(group_id) 
            # attributes.append("Group") 
        if patient_birthdate_condition:
            self._add_patient_birthdate(patient_birthdate_condition)
            attributes.append("Birthdate")


        return attributes, self.map_attributes


    def generate_sql_query(self, attributes : List[str]) -> str:
        """Generate a SQL query from a list of attribute names.

        Args:
            attributes: List of attributes that must appear in the SQL query

        Returns:
            str: SQL query as a string
        """
        sql_select = self._select(attributes)
        sql_join = self._join(attributes)
        sql_where = self._where(attributes)
        sql_query = "\n".join([sql_part for sql_part in [sql_select, sql_join, sql_where] if sql_part])
        return sql_query


