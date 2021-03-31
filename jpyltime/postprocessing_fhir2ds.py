import json
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from jpyltime.utils import Attribute


class FHIR2DS_Postprocessing:
    def __init__(self, map_attributes: Dict[str, Any], anonymization_symbol: str = "*"):
        """map_attributes: a mapping of Column Name in natural language to FHIR and display information (resource name, source name and conditions)"""
        self.map_attributes = map_attributes
        self.anonymization_symbol = anonymization_symbol

    def _groupby_patient_column(self, df: pd.DataFrame, patient_columns: List[str]) -> pd.DataFrame:
        """Groupby Patient and combine other values as list of the same type (ex. Weight or Potassium)"""
        # Aggregate information by Patient, dropping null values to avoid NaN in output list
        return (
            df.groupby(patient_columns, dropna=False)
            .agg(lambda x: list(x[x.notna()]))
            .reset_index()
        )

    def _concatenate_columns(
        self,
        df: pd.DataFrame,
        attributes: Dict[str, Attribute],
        patient_id_colname: str,
        patient_resource_name: str = "Patient",
    ) -> Tuple[pd.DataFrame, List[str]]:
        """To improve readibility and display, some columns are gathered to reduce the complexity of the dataFrame.
            Display info are written in the attribute dictionary and the dataFrame is modified according to the instructions, by combining some columns.
            Ex: combine value with quantity improve readibility:
                --  | patient.weight.value : 30 | patient.weight.unit : kg |
                ++  | Weight : 30 kg |
            Replace col name with custom name
            Keep tracks of columns coming from main resource table (Patient)

        Args:
            df: DataFrame as outputted by FHIR2Dataset api
            attributes: Dict of attributes asked by user, with info on anonymization constraints and custom names
            patient_id_colname: Name of the column for patient index in FHIR
            patient_resource_name: Name of main table, Patient resource in FHIR

        Return:
            display_df: df with improved readibility
            col_from_patient_table: list of columns in display_df coming from the main table, Patient
        """

        def flatten(x):
            return [a for i in x for a in flatten(i)] if isinstance(x, list) else [x]

        display_df = pd.DataFrame()
        display_df[patient_id_colname] = df[patient_id_colname]
        col_from_patient_table: List[str] = []
        # Fill the new dataset with : new column names and combination of some column values
        for attribute in attributes.values():
            attribute_info = self.map_attributes[attribute.official_name]
            # Case some column must be combined
            if "display" in attribute_info:
                display_df[attribute.custom_name] = df[
                    attribute_info["display"]["concatenate_columns"]
                ].apply(
                    lambda row: attribute_info["display"]["join_symbol"].join(
                        row.values.astype(str)
                    ),
                    axis=1,
                )
            # Case only renaming is required
            else:
                display_df[attribute.custom_name] = df[
                    attribute_info["fhir_source"]["select"][0]
                ].apply(lambda x: flatten(x)[0])
                if attribute_info["fhir_resource"] == patient_resource_name:
                    col_from_patient_table.append(attribute.custom_name)
        return display_df, col_from_patient_table + [patient_id_colname]

    def anonymize(self, df: pd.DataFrame, attributes: Dict[str, Attribute]) -> pd.DataFrame:
        """Anonymize columns by replacing value with a symbol"""
        for attribute in attributes.values():
            if attribute.anonymize:
                df[attribute.custom_name] = self.anonymization_symbol
        return df

    def postprocess(
        self,
        df: pd.DataFrame,
        attributes: Dict[str, Attribute],
        patient_index: str = "Patient:from_id",
    ) -> pd.DataFrame:
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
        df, patient_columns = self._concatenate_columns(df, attributes, patient_index)
        df = self._groupby_patient_column(df, patient_columns)
        df = self.anonymize(df, attributes)
        # Drop unwanted Patient:from_id index coming from FHIR
        df.drop(columns=[patient_index], inplace=True)
        return df.reset_index(drop=True)
