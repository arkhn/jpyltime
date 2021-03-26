
from pydantic import BaseModel

class Attribute(BaseModel):
    """Define the data model for the attributes."""

    official_name: str
    custom_name: str
    anonymize: bool