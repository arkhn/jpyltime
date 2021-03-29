from typing import List, Dict, Any, Optional
import json
import pandas as pd

from jpyltime.utils import Attribute

class FHIR2DS_Postprocessing():
    def __init__(self,map_attributes:Dict[str, Any], anonymization_symbol: str = "*"):
        """map_attributes: a mapping of Column Name in natural language to FHIR and display information (resource name, source name and conditions)"""
        self.map_attributes = map_attributes
        self.anonymization_symbol = anonymization_symbol

    def _groupby_one_column(self, df: pd.DataFrame, col_for_merging:str) -> pd.DataFrame:
        """Groupby one column (arg. col_for_merging) and combine the grouped rows in list, keeping only not null value
            Check that the column selected to apply the groupby exists in the dataFrame, overwise raise an Exception."""
        if col_for_merging not in df.columns:
            raise Exception(f"Impossible to merge on column name {col_for_merging} as it is not present in the dataframe: {df.columns}")
        return df.groupby(by=[col_for_merging]).agg(lambda x: set(x[x.notna()])).reset_index()



    def _concatenate_columns(self, df: pd.DataFrame, attributes : Dict[str, Attribute], patient_id_colname: str) -> pd.DataFrame:
        """To improve readibility and display, some columns are gathered to reduce the complexity of the dataFrame.
            Display info are written in the attribute dictionary and the dataFrame is modified according to the instructions, by combining some columns.
            Ex: combine value with quantity improve readibility: 
                --  | patient.weight.value : 30 | patient.weight.unit : kg | 
                ++  | Weight : 30 kg |
            Replace col name with custom name

        Args:
            df: DataFrame as outputted by FHIR2Dataset api
            attributes: Dict of attributes asked by user, with info on anonymization constraints and custom names

        """
        display_df = pd.DataFrame()
        display_df[patient_id_colname] = df[patient_id_colname]
        # Fill the new dataset with : new column names and combination of some column values
        for attribute in attributes.values():
            attribute_info = self.map_attributes[attribute.official_name]
            # Case some column must be combined
            if "display" in attribute_info:
                display_df[attribute.custom_name] = df[attribute_info["display"]["concatenate_columns"]].apply(lambda row: attribute_info["display"]["join_symbol"].join(row.values.astype(str)), axis=1)
            # Case only renaming is required
            else:
                flatten_column_data = df[attribute_info["fhir_source"]["select"][0]].apply(lambda x:[item for sublist in x for item in sublist][0] if isinstance(x, list) else x)
                display_df[attribute.custom_name] = flatten_column_data
        return display_df


    def anonymize(self, df: pd.DataFrame, attributes: Dict[str, Attribute]) -> pd.DataFrame:
        """Anonymize columns by replacing value with a symbol"""
        for attribute in attributes.values():
            if attribute.anonymize:
                df[attribute.custom_name] = self.anonymization_symbol
        return df

    def postprocess(self, df: pd.DataFrame, attributes : Dict[str, Attribute]) -> pd.DataFrame:
        """Improve readibility and display of a given dataFrame, by:
            - Concatenated some columns, ex Value with Unit (| 30 | mg | => | 30 mg | )
            - Groupby one column to reduce redundancy 
            - Anonymize sensitive data

        Args:
            df: DataFrame as outputted by FHIR2Dataset api
            attributes: Dict of attributes asked by user, with info on anonymization constraints and custom names

        Returns:
            pd.DataFrame: The dataFrame updated with the previous transformation.
        """
        patient_index = df.columns[0]
        df = self._concatenate_columns(df, attributes, patient_index)
        df = self._groupby_one_column(df, col_for_merging=patient_index)
        df = self.anonymize(df, attributes)
        return df.reset_index(drop=True)

