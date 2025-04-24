from celery.result import AsyncResult
from fastapi import FastAPI

import tasks  # Import all tasks
from border_based_calculations_by_year import (
    BorderType,
)
from celery_app import celery_app  # Import celery app instance

app = FastAPI()


# --- Status Check Endpoint ---
@app.get("/job_status/{task_id}")
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
@app.post("/border/river/")
def border_river(border_type: BorderType, year: int):
    task = tasks.calculate_border_river_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/emission/")
def border_emission(border_type: BorderType, year: int):
    task = tasks.calculate_border_emission_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/car_registration/")
def border_car_registration(border_type: BorderType, year: int):
    task = tasks.calculate_border_car_registration_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/landuse_area/")
def border_landuse_area(border_type: BorderType, year: int):
    task = tasks.calculate_border_landuse_area_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/coastline_distance/")
def border_coastline_distance(border_type: BorderType, year: int):
    task = tasks.calculate_border_coastline_distance_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/ndvi/")
def border_ndvi(border_type: BorderType, year: int):
    task = tasks.calculate_border_ndvi_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/airport_distance/")
def border_airport_distance(border_type: BorderType, year: int):
    task = tasks.calculate_border_airport_distance_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/mdl_distance/")
def border_mdl_distance(border_type: BorderType, year: int):
    task = tasks.calculate_border_mdl_distance_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/port_distance/")
def border_port_distance(border_type: BorderType, year: int):
    task = tasks.calculate_border_port_distance_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/rail/")
def border_rail(border_type: BorderType, year: int):
    task = tasks.calculate_border_rail_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/road/")
def border_road(border_type: BorderType, year: int):
    task = tasks.calculate_border_road_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/topographic_model/")
def border_topographic_model(border_type: BorderType, year: int):
    task = tasks.calculate_border_topographic_model_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/raster_emission/")
def border_raster_emission(border_type: BorderType, year: int):
    task = tasks.calculate_border_raster_emission_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/clinic_count/")
def border_clinic_count(border_type: BorderType, year: int):
    task = tasks.calculate_border_clinic_count_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.post("/border/hospital_count/")
def border_hospital_count(border_type: BorderType, year: int):
    task = tasks.calculate_border_hospital_count_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/")
def root():
    return {"message": "Korea GeoVariable FastAPI server is running."}
