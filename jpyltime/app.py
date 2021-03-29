"""Set-up the FastAPI to communicate with fhir2dataset."""

from typing import List, Dict, Any
import json
import settings
import io

import fhir2dataset as query
from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jpyltime.utils import Attribute
from jpyltime.preprocessing_fhir2ds import FHIR2DS_Preprocessing
from jpyltime.postprocessing_fhir2ds import FHIR2DS_Postprocessing
from fastapi.responses import StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  TODO: configure a logger
@app.post("/fhir2dataset")
def fhir2dataset_route(
    practitioner_id: str = Body(...),
    attributes: List[Attribute] = Body(...),
    patient_ids: List[str] = Body(...),
) -> StreamingResponse:
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
    # preprocessing
    requested_attributes = {attribute.official_name : attribute for attribute in attributes}
    sql_query, updated_requested_attributes, updated_map_attributes = FHIR2DS_Preprocessing().preprocess(requested_attributes)
    print(sql_query)
    
    sql_df = query.sql(sql_query, fhir_api_url=settings.FHIR_API_URL, token=practitioner_id)
    print(sql_df.head())

    # postprocessing
    df = FHIR2DS_Postprocessing(updated_map_attributes).postprocess(sql_df, updated_requested_attributes, patient_ids)
    response = StreamingResponse(io.StringIO(df.to_csv(index=False)), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"

    return response
