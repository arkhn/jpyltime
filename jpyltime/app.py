"""Set-up the FastAPI to communicate with fhir2dataset."""

from typing import List

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/fhir2dataset")
def read_item(
    practitioner_id: str,
    group_id: str,
    col_names: List[str] = Query(...),
):
    # TODO
    pass
