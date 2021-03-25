"""Set-up the FastAPI to communicate with fhir2dataset."""

from typing import List

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


@app.get("/")
def read_root():
    """Test function."""
    return {"Hello": "World"}


@app.post("/fhir2dataset")
def call_fhir2dataset(
    practitioner_id: str,
    attributes: List[Attribute],
    patient_ids: List[str] = Body(...),
):
    # TODO
    pass
