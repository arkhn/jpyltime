"""Set-up the FastAPI to communicate with fhir2dataset."""

from typing import List

import fhir2dataset as query
from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Attribute(BaseModel):
    """Define the data model for the attributes."""

    official_name: str
    custom_name: str
    anonymize: bool


@app.post("/fhir2dataset")
def fhir2dataset_route(
    practitioner_id: str = Body(...),
    attributes: List[Attribute] = Body(...),
    patient_ids: List[str] = Body(...),
) -> str:
    """Route to call fhir2dataset & it's wrapping functions.

    Ags:
    * `practitioner_id`: identifier of a practitioner;
    * `attributes`: list of attributes to compute; each attribute contains:
        - `official_name`,
        - `custom_name`,
        - `anonymize`;
    * `patient_ids`: identifiers of the patients to output.

    Returns:
        JSON representation of the table containing the required data.
    """
    # TODO
    sql_query = """
    SELECT Patient.name.family, Patient.address.city
    FROM Patient
    WHERE Patient.birthdate = 2000-01-01 AND Patient.gender = 'female'
    """
    df = query.sql(sql_query)
    return df.to_json(orient="records")
