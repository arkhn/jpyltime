import json
from typing import Any, Dict, List, Optional, Tuple

from jpyltime.utils import Attribute


# FIXME Doesn't Fhir2Dataset provide some kind of SDK (a set of functions to build a query)?
# As both jpyltime and F2D are written in python, it's a bit painful to see them communicate via a handwritten string
class FHIR2DS_Preprocessing:
    def __init__(
        self,
        attribute_file: str = "jpyltime/documents/attributes_mapping.json",
        group_id: Optional[str] = None,
    ):
        """Args:
        map_attributes: a mapping of Column Name in natural language to FHIR information (resource name, source name and conditions)
        group_id (Optional[str]): Practioner id to restrict the scope of the query to specific patient from a practioner. Defaults to None.
        """
        with open(attribute_file, "r") as f:
            self.map_attributes = json.loads(f.read())
        self.group_id = group_id

    def _select(self, attributes: List[str]) -> str:
        """Generate SELECT ... FROM ... condition of the sql query, from a list of attribute names given by the user.
        Always FROM PATIENT"""
        select_attributes = [
            self.map_attributes[attribute]["fhir_source"]["select"]
            for attribute in attributes
            if "select" in self.map_attributes[attribute]["fhir_source"]
        ]
        select_attributes_flatten = [
            item for attributes in select_attributes for item in attributes
        ]
        return f"SELECT {', '.join(select_attributes_flatten)} FROM Patient"

    def _join(self, attributes: List[str]) -> Optional[str]:
        """Generate [INNER-CHILD] JOIN ... ON ... conditions of the sql query, from a list of attribute names given by the user"""
        sql_join = []
        for attribute in attributes:
            if "join" in self.map_attributes[attribute]["fhir_source"]:
                for join_condition in self.map_attributes[attribute]["fhir_source"]["join"]:
                    sql_join.append(
                        " ".join(
                            [
                                "CHILD JOIN",
                                self.map_attributes[attribute]["fhir_resource"],
                                "ON",
                                join_condition["key"],
                                "=",
                                join_condition["value"],
                            ]
                        )
                    )
        if self.group_id:
            sql_join.append(f"INNER JOIN Group ON Group.member = Patient._id")
        if not sql_join:
            return ""
        return " ".join(sql_join)

    def _where(self, attributes: List[str]) -> Optional[str]:
        """Generate WHERE ... conditions of the sql query, from a list of attribute names given by the user"""
        sql_where = []
        for attribute in attributes:
            map_attribute = self.map_attributes[attribute]
            if "where" in map_attribute["fhir_source"]:
                for where_condition in map_attribute["fhir_source"]["where"]:
                    sql_where.append(
                        " ".join([where_condition["key"], "=", where_condition["value"]])
                    )

        if self.group_id:
            sql_where.append(f"Group._id = {self.group_id}")
        if not sql_where:
            return ""
        return f"WHERE {' AND '.join(sql_where)}"

    def _check_attributes_defined(self, attributes: Dict[str, Attribute]):
        """Return an error if some attributes asked by the user are not defined in the fhir mapping dictionary"""
        undefined_attributes = set(attributes.keys()).difference(set(self.map_attributes.keys()))
        if undefined_attributes:
            raise ValueError(
                f"Undefined attributes {undefined_attributes}, they must be defined in the attributes mapping dictionnary."
            )

    def generate_sql_query(self, requested_attributes: Dict[str, Attribute]) -> str:
        """Generate a SQL query from a list of attribute.

        Args:
            attributes: List of attributes that must appear in the SQL query

        Returns:
            str: SQL query as a string
        """
        attributes = list(requested_attributes.keys())
        sql_select = self._select(attributes)
        sql_join = self._join(attributes)
        sql_where = self._where(attributes)
        sql_query = " ".join(
            [sql_part for sql_part in [sql_select, sql_join, sql_where] if sql_part]
        )
        return sql_query

    def preprocess(self, attributes: Dict[str, Attribute]) -> Tuple[str, Dict[str, Any]]:
        """Adapt a list of attributes to generate a correct sql query to request the fhir api

        Args:
            attributes: Dict of Attributes that must appear in the SQL query, given by the user

        Returns:
            Tuple[str, Dict[str, Attribute]]:
            - sql_query: sql query matching the given attributes and the fhir constraints
            - attributes: Dict of attribute, udapted with preprocessing info
            - map_attributes: mapping of Column Name in natural language to FHIR information (resource name, source name and conditions)
        """
        self._check_attributes_defined(attributes)
        sql_query = self.generate_sql_query(attributes)
        return sql_query, self.map_attributes
