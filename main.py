import os

from celery.result import AsyncResult
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader

import tasks  # Import all tasks
from border_based_calculations_by_year import (
    BorderType,
)
from celery_app import celery_app  # Import celery app instance

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# API Key authentication
API_KEY = os.environ.get("API_KEY")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not API_KEY:
        # If no API key is set, don't enforce authentication
        return None
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Invalid API Key")


# --- Status Check Endpoint ---
@app.get("/job_status/{task_id}", dependencies=[Depends(get_api_key)])
def get_job_status(task_id: str):
    """Check the status of a submitted job."""
    task_result = AsyncResult(task_id, app=celery_app)

    response = {"task_id": task_id, "status": task_result.status, "result": None}

    if task_result.successful():
        response["result"] = task_result.get()
    elif task_result.failed():
        # Access the custom error info stored in meta
        try:
            # Celery stores traceback/exception info differently depending on version/config
            # Try accessing the meta info we set
            error_info = (
                task_result.info
                if isinstance(task_result.info, dict)
                else str(task_result.info)
            )
            response["result"] = error_info
        except Exception:
            response["result"] = "Failed to retrieve error details."
    # Handle other states like PENDING, STARTED, RETRY if needed

    return response


# --- Border-based endpoints ---
@app.post("/border/river/", dependencies=[Depends(get_api_key)])
def border_river(border_type: BorderType, year: int):
    task = tasks.calculate_border_river_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/emission/", dependencies=[Depends(get_api_key)])
def border_emission(border_type: BorderType, year: int):
    task = tasks.calculate_border_emission_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/car_registration/", dependencies=[Depends(get_api_key)])
def border_car_registration(border_type: BorderType, year: int):
    task = tasks.calculate_border_car_registration_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/landuse_area/", dependencies=[Depends(get_api_key)])
def border_landuse_area(border_type: BorderType, year: int):
    task = tasks.calculate_border_landuse_area_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/coastline_distance/", dependencies=[Depends(get_api_key)])
def border_coastline_distance(border_type: BorderType, year: int):
    task = tasks.calculate_border_coastline_distance_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/ndvi/", dependencies=[Depends(get_api_key)])
def border_ndvi(border_type: BorderType, year: int):
    task = tasks.calculate_border_ndvi_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/airport_distance/", dependencies=[Depends(get_api_key)])
def border_airport_distance(border_type: BorderType, year: int):
    task = tasks.calculate_border_airport_distance_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/mdl_distance/", dependencies=[Depends(get_api_key)])
def border_mdl_distance(border_type: BorderType, year: int):
    task = tasks.calculate_border_mdl_distance_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/port_distance/", dependencies=[Depends(get_api_key)])
def border_port_distance(border_type: BorderType, year: int):
    task = tasks.calculate_border_port_distance_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/rail/", dependencies=[Depends(get_api_key)])
def border_rail(border_type: BorderType, year: int):
    task = tasks.calculate_border_rail_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/road/", dependencies=[Depends(get_api_key)])
def border_road(border_type: BorderType, year: int):
    task = tasks.calculate_border_road_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/topographic_model/", dependencies=[Depends(get_api_key)])
def border_topographic_model(border_type: BorderType, year: int):
    task = tasks.calculate_border_topographic_model_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/raster_emission/", dependencies=[Depends(get_api_key)])
def border_raster_emission(border_type: BorderType, year: int):
    task = tasks.calculate_border_raster_emission_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/clinic_count/", dependencies=[Depends(get_api_key)])
def border_clinic_count(border_type: BorderType, year: int):
    task = tasks.calculate_border_clinic_count_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/hospital_count/", dependencies=[Depends(get_api_key)])
def border_hospital_count(border_type: BorderType, year: int):
    task = tasks.calculate_border_hospital_count_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/")
def root():
    return {"message": "Korea GeoVariable FastAPI server is running."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
