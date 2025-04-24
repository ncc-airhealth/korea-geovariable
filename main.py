from celery.result import AsyncResult
from fastapi import FastAPI

import tasks  # Import all tasks
from border_based_calculations_by_year import (
    BorderType,
)
from celery_app import celery_app  # Import celery app instance
from point_based_calculations import (
    BufferSize,
)

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
@app.get("/border/river/")
def border_river(border_type: BorderType, year: int):
    task = tasks.calculate_border_river_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/emission/")
def border_emission(border_type: BorderType, year: int):
    task = tasks.calculate_border_emission_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/car_registration/")
def border_car_registration(border_type: BorderType, year: int):
    task = tasks.calculate_border_car_registration_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/landuse_area/")
def border_landuse_area(border_type: BorderType, year: int):
    task = tasks.calculate_border_landuse_area_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/coastline_distance/")
def border_coastline_distance(border_type: BorderType, year: int):
    task = tasks.calculate_border_coastline_distance_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/ndvi/")
def border_ndvi(border_type: BorderType, year: int):
    task = tasks.calculate_border_ndvi_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/airport_distance/")
def border_airport_distance(border_type: BorderType, year: int):
    task = tasks.calculate_border_airport_distance_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/mdl_distance/")
def border_mdl_distance(border_type: BorderType, year: int):
    task = tasks.calculate_border_mdl_distance_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/port_distance/")
def border_port_distance(border_type: BorderType, year: int):
    task = tasks.calculate_border_port_distance_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/rail/")
def border_rail(border_type: BorderType, year: int):
    task = tasks.calculate_border_rail_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/road/")
def border_road(border_type: BorderType, year: int):
    task = tasks.calculate_border_road_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/topographic_model/")
def border_topographic_model(border_type: BorderType, year: int):
    task = tasks.calculate_border_topographic_model_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/raster_emission/")
def border_raster_emission(border_type: BorderType, year: int):
    task = tasks.calculate_border_raster_emission_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/clinic_count/")
def border_clinic_count(border_type: BorderType, year: int):
    task = tasks.calculate_border_clinic_count_task.delay(border_type.value, year)
    return {"task_id": task.id}


@app.get("/border/hospital_count/")
def border_hospital_count(border_type: BorderType, year: int):
    task = tasks.calculate_border_hospital_count_task.delay(border_type.value, year)
    return {"task_id": task.id}


# --- Point-based endpoints ---
@app.get("/point/clinic_count/")
def point_clinic_count(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_clinic_count_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/hospital_count/")
def point_hospital_count(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_hospital_count_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/business_registration_count/")
def point_business_registration_count(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_business_registration_count_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/business_employee_count/")
def point_business_employee_count(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_business_employee_count_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/house_type_count/")
def point_house_type_count(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_house_type_count_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/landuse/")
def point_landuse(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_landuse_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


# --- Additional Point-based endpoints ---
@app.get("/point/jgg_centroid_raster_value/")
def point_jgg_centroid_raster_value(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_jgg_centroid_raster_value_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/dem_raster_value/")
def point_dem_raster_value(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_dem_raster_value_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/dsm_raster_value/")
def point_dsm_raster_value(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_dsm_raster_value_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/jgg_centroid_buffer_count/")
def point_jgg_centroid_buffer_count(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_jgg_centroid_buffer_count_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/bus_stop_count/")
def point_bus_stop_count(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_bus_stop_count_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/rail_station_count/")
def point_rail_station_count(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_rail_station_count_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/jgg_centroid_shortest_distance/")
def point_jgg_centroid_shortest_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_jgg_centroid_shortest_distance_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/bus_stop_distance/")
def point_bus_stop_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_bus_stop_distance_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/airport_distance/")
def point_airport_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_airport_distance_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/rail_distance/")
def point_rail_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_rail_distance_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/rail_station_distance/")
def point_rail_station_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_rail_station_distance_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/coastline_distance/")
def point_coastline_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_coastline_distance_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/mdl_distance/")
def point_mdl_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_mdl_distance_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/port_distance/")
def point_port_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_port_distance_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/mr1_distance/")
def point_mr1_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_mr1_distance_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/mr2_distance/")
def point_mr2_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_mr2_distance_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/road_distance/")
def point_road_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_road_distance_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/river_distance/")
def point_river_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_river_distance_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/clinic_distance/")
def point_clinic_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_clinic_distance_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/hospital_distance/")
def point_hospital_distance(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_hospital_distance_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/car_mean/")
def point_car_mean(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_car_mean_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/emission_vector_based/")
def point_emission_vector_based(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_emission_vector_based_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/emission_raster_value/")
def point_emission_raster_value(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_emission_raster_value_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/road_length/")
def point_road_length(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_road_length_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/road_length_lane/")
def point_road_length_lane(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_road_length_lane_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/road_length_lane_width/")
def point_road_length_lane_width(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_road_length_lane_width_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/abstract_mr_length/")
def point_abstract_mr_length(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_abstract_mr_length_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/mr1_length/")
def point_mr1_length(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_mr1_length_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/mr2_length/")
def point_mr2_length(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_mr2_length_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/abstract_mr_length_lane/")
def point_abstract_mr_length_lane(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_abstract_mr_length_lane_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/mr1_length_lane/")
def point_mr1_length_lane(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_mr1_length_lane_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/mr2_length_lane/")
def point_mr2_length_lane(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_mr2_length_lane_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/abstract_mr_length_lane_width/")
def point_abstract_mr_length_lane_width(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_abstract_mr_length_lane_width_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/mr1_length_lane_width/")
def point_mr1_length_lane_width(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_mr1_length_lane_width_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/mr2_length_lane_width/")
def point_mr2_length_lane_width(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_mr2_length_lane_width_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/population/")
def point_population(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_population_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/abstract_ndvi_statistic/")
def point_abstract_ndvi_statistic(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_abstract_ndvi_statistic_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/ndvi_statistic_mean/")
def point_ndvi_statistic_mean(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_ndvi_statistic_mean_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/ndvi_statistic_median/")
def point_ndvi_statistic_median(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_ndvi_statistic_median_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/point/ndvi_statistic_min/")
def point_ndvi_statistic_min(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_ndvi_statistic_min_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/ndvi_statistic_max/")
def point_ndvi_statistic_max(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_ndvi_statistic_max_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/ndvi_statistic_8mdn/")
def point_ndvi_statistic_8mdn(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_ndvi_statistic_8mdn_task.delay(buffer_size.value, year)
    return {"task_id": task.id}


@app.get("/point/jgg_centroid_relative_dem_dsm/")
def point_jgg_centroid_relative_dem_dsm(buffer_size: BufferSize, year: int):
    task = tasks.calculate_point_jgg_centroid_relative_dem_dsm_task.delay(
        buffer_size.value, year
    )
    return {"task_id": task.id}


@app.get("/")
def root():
    return {"message": "Korea GeoVariable FastAPI server is running."}
