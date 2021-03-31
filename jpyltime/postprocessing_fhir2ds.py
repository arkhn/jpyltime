import json
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from jpyltime.utils import Attribute


class FHIR2DS_Postprocessing:
    def __init__(self, map_attributes: Dict[str, Any], anonymization_symbol: str = "*"):
        """map_attributes: a mapping of Column Name in natural language to FHIR and display information (resource name, source name and conditions)"""
        self.map_attributes = map_attributes
        self.anonymization_symbol = anonymization_symbol

    def _groupby_one_column(
        self, df: pd.DataFrame, col_for_merging: str, col_from_patient_table: Dict[str, bool]
    ) -> pd.DataFrame:
        """Groupby one column (arg. col_for_merging), then either:
            - keep only one value for column from main table (Patient), to avoid repetition of similar value (ex. Name)
            - combine other values as list of the same type (ex. Weight or Potassium)
        Check that the column selected to apply the groupby exists in the dataFrame, overwise raise an Exception.
        Remove patient index column coming from FHIR resource and reset new index"""
        if col_for_merging not in df.columns:
            raise Exception(
                f"Impossible to merge on column name {col_for_merging} as it is not present in the dataframe: {df.columns}"
            )
        df = df.groupby(by=[col_for_merging]).agg(lambda x: list(x[x.notna()])).reset_index()
        df.drop(columns=[col_for_merging], inplace=True)
        for col in df.columns:
            if col_from_patient_table[col]:
                df[col] = df[col].apply(lambda x: x[0] if x else None)
        return df

    def _concatenate_columns(
        self,
        df: pd.DataFrame,
        attributes: Dict[str, Attribute],
        patient_id_colname: str,
        patient_resource_name: str = "Patient",
    ) -> Tuple[pd.DataFrame, Dict[str, bool]]:
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
            col_from_patient_table: dictionary to know if a column in display_df belongs to the main table Patient or not
        """

        def flatten(x):
            return [a for i in x for a in flatten(i)] if isinstance(x, list) else [x]

        display_df = pd.DataFrame()
        display_df[patient_id_colname] = df[patient_id_colname]
        col_from_patient_table: Dict[str, bool] = {}
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
                col_from_patient_table[attribute.custom_name] = False
            # Case only renaming is required
            else:
                display_df[attribute.custom_name] = df[
                    attribute_info["fhir_source"]["select"][0]
                ].apply(lambda x: flatten(x)[0])
                col_from_patient_table[attribute.custom_name] = (
                    attribute_info["fhir_resource"] == patient_resource_name
                )
        return display_df, col_from_patient_table

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
        df, col_from_patient_table = self._concatenate_columns(df, attributes, patient_index)
        df = self._groupby_one_column(
            df, col_for_merging=patient_index, col_from_patient_table=col_from_patient_table
        )
        df = self.anonymize(df, attributes)
        return df.reset_index(drop=True)
