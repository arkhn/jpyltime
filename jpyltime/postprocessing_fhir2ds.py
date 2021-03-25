from typing import List, Dict, Any, Optional
import json
import pandas as pd

class FHIR2DS_Postprocessing():
    def __init__(self,map_attributes:Dict[str, Any],patient_id_attribute_name: str):
        """map_attributes: a mapping of Column Name in natural language to FHIR and display information (resource name, source name and conditions)"""
        self.map_attributes = map_attributes
        self.patient_id_attribute_name =patient_id_attribute_name 

    def _groupby_one_column(self, df: pd.DataFrame, col_for_merging:str) -> pd.DataFrame:
        """Groupby one column (arg. col_for_merging) and combine the grouped rows in list, keeping only not null value
            Check that the column selected to apply the groupby exists in the dataFrame, overwise raise an Exception."""
        if col_for_merging not in df.columns:
            raise Exception(f"Given column names are not in the dataframe: {df.columns}")
        return df.groupby(by=[col_for_merging]).agg(lambda x: list(x[x.notna()])).reset_index()


    def _concatenate_columns(self, df: pd.DataFrame, attributes : List[str]) -> pd.DataFrame:
        """Read display info in attribute dictionary and modify the dataFrame by combining some columns to improve readibility and display.
            Ex: combine value with quantity improve readibility: 
                --  | patient.weight.value : 30 | patient.weight.unit : kg | 
                ++  | Weight : 30 kg |
        """
        display_df = pd.DataFrame()
        for attribute in attributes:
            attribute_info = self.map_attributes[attribute]
            if "display" in attribute_info:
                display_df[attribute] = df[attribute_info["display"]["concatenate_columns"]].apply(lambda row: attribute_info["display"]["join_symbol"].join(row.values.astype(str)), axis=1)
            else:
                display_df[attribute] = df[attribute_info["fhir_source"]["select"][0]]
        return display_df

    def restrict_patient_scope(self, df: pd.DataFrame, group_id: List[str]) -> pd.DataFrame:
        """Filter to keep only patients whose id is present on the group_id"""
        return df[self.patient_id_attribute_name].isin(group_id)

    def improve_display(self, df: pd.DataFrame, attributes : List[str], group_id : Optional[List[str]] = None ) -> pd.DataFrame:
        """Improve readibility and display of a given dataFrame, by:
            - Filtering some patiens
            - Concatenated some columns, ex Value with Unit (| 30 | mg | => | 30 mg | )
            - Groupby one column to reduce redundancy 

        Args:
            df: DataFrame as outputted by FHIR2Dataset api
            attributes: List of attributes in natural language, asked by user
            group_id: List of patients that should appears on the data. Defaults to None.

        Returns:
            pd.DataFrame: The dataFrame updated with the previous transformation.
        """
        if group_id:
            df = self.restrict_patient_scope(group_id)
        display_df = self._concatenate_columns(df, attributes)
        display_df = self._groupby_one_column(display_df, self.patient_id_attribute_name)
        return display_df