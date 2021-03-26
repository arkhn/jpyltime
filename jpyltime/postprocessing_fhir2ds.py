from typing import List, Dict, Any, Optional
import json
import pandas as pd

from jpyltime.utils import Attribute

class FHIR2DS_Postprocessing():
    def __init__(self,map_attributes:Dict[str, Any]):
        """map_attributes: a mapping of Column Name in natural language to FHIR and display information (resource name, source name and conditions)"""
        self.map_attributes = map_attributes

    def _groupby_one_column(self, df: pd.DataFrame, col_for_merging:str) -> pd.DataFrame:
        """Groupby one column (arg. col_for_merging) and combine the grouped rows in list, keeping only not null value
            Check that the column selected to apply the groupby exists in the dataFrame, overwise raise an Exception."""
        if col_for_merging not in df.columns:
            raise Exception(f"Impossible to merge on column name {col_for_merging} as it is not present in the dataframe: {df.columns}")
        return df.groupby(by=[col_for_merging]).agg(lambda x: set(x[x.notna()])).reset_index()

    def _concatenate_columns(self, df: pd.DataFrame, attributes : Dict[str, Attribute], patient_id_col: str) -> pd.DataFrame:
        """Read display info in attribute dictionary and modify the dataFrame by combining some columns to improve readibility and display.
            Ex: combine value with quantity improve readibility: 
                --  | patient.weight.value : 30 | patient.weight.unit : kg | 
                ++  | Weight : 30 kg |
        """
        display_df = pd.DataFrame()
        display_df[patient_id_col] = df[patient_id_col]
        for attribute in attributes.values():
            attribute_info = self.map_attributes[attribute.official_name]
            if "display" in attribute_info:
                display_df[attribute.custom_name] = df[attribute_info["display"]["concatenate_columns"]].apply(lambda row: attribute_info["display"]["join_symbol"].join(row.values.astype(str)), axis=1)
            else:
                display_df[attribute.custom_name] = df[attribute_info["fhir_source"]["select"][0]]
        return display_df

    def restrict_patient_scope(self, df: pd.DataFrame, patient_ids: List[str], patient_id_col: str) -> pd.DataFrame:
        """Filter to keep only patients whose id is present on patient_ids"""
        return df[patient_id_col].isin(patient_ids)

    def anonymize(self, df: pd.DataFrame, attributes: Dict[str, Attribute], anonymization_symbol = "*") -> pd.DataFrame:
        """Anonymized columns by replacing value with symbol"""
        for attribute in attributes.values():
            if attribute.anonymize:
                df[attribute.custom_name] = anonymization_symbol
        return df

    def postprocessing(self, df: pd.DataFrame, attributes : Dict[str, Attribute], patient_ids : Optional[List[str]] = None ) -> pd.DataFrame:
        """Improve readibility and display of a given dataFrame, by:
            - Filtering some patiens
            - Concatenated some columns, ex Value with Unit (| 30 | mg | => | 30 mg | )
            - Groupby one column to reduce redundancy 

        Args:
            df: DataFrame as outputted by FHIR2Dataset api
            attributes: Dict of attributes asked by user
            patient_ids: List of patients that should appears on the data. Defaults to None.

        Returns:
            pd.DataFrame: The dataFrame updated with the previous transformation.
        """
        patient_id_col = "Patient:from_id"
        if patient_ids:
            df = self.restrict_patient_scope(df, patient_ids, patient_id_col)
        df = self._concatenate_columns(df, attributes, patient_id_col)
        df = self._groupby_one_column(df, col_for_merging=patient_id_col)
        df = self.anonymize(df, attributes)
        return df

