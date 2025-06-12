import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from border_based_calculations_by_year import (
    AirportDistanceCalculator,
    BorderType,
    CarRegistrationCalculator,
    ClinicBorderCalculator,
    CoastlineDistanceCalculator,
    EmissionCalculator,
    HospitalBorderCalculator,
    LanduseAreaCalculator,
    MilitaryDemarcationLineDistanceCalculator,
    NdviCalculator,
    PortDistanceCalculator,
    RailCalculator,
    RasterEmissionCalculator,
    RiverCalculator,
    RoadCalculator,
    TopographicModelCalculator,
)
from celery_app import celery_app


def df_to_json(df: pd.DataFrame):
    # Celery needs serializable results, so we convert DataFrame to JSON here
    return df.to_dict(orient="records")


def run_calculation(self, calculator_class, year, identifier_value, identifier_enum):
    """Helper function to run calculation and handle exceptions."""
    try:
        identifier = identifier_enum(identifier_value)
        calc = calculator_class(identifier, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        self.update_state(
            state="FAILURE", meta={"exc_type": type(e).__name__, "exc_message": str(e)}
        )
        return {
            "error": str(e),
            "details": f"Failed during {calculator_class.__name__}",
        }


# --- Border-based tasks --- BORDER


@celery_app.task(bind=True)
def calculate_border_river_task(self, border_type_value: str, year: int):
    return run_calculation(self, RiverCalculator, year, border_type_value, BorderType)


@celery_app.task(bind=True)
def calculate_border_emission_task(self, border_type_value: str, year: int):
    return run_calculation(
        self, EmissionCalculator, year, border_type_value, BorderType
    )


@celery_app.task(bind=True)
def calculate_border_car_registration_task(self, border_type_value: str, year: int):
    return run_calculation(
        self, CarRegistrationCalculator, year, border_type_value, BorderType
    )


@celery_app.task(bind=True)
def calculate_border_landuse_area_task(self, border_type_value: str, year: int):
    # TODO: error found need to fix query
    return run_calculation(
        self, LanduseAreaCalculator, year, border_type_value, BorderType
    )


@celery_app.task(bind=True)
def calculate_border_coastline_distance_task(self, border_type_value: str, year: int):
    return run_calculation(
        self, CoastlineDistanceCalculator, year, border_type_value, BorderType
    )


@celery_app.task(bind=True)
def calculate_border_ndvi_task(self, border_type_value: str, year: int):
    return run_calculation(self, NdviCalculator, year, border_type_value, BorderType)


@celery_app.task(bind=True)
def calculate_border_airport_distance_task(self, border_type_value: str, year: int):
    return run_calculation(
        self, AirportDistanceCalculator, year, border_type_value, BorderType
    )


@celery_app.task(bind=True)
def calculate_border_mdl_distance_task(self, border_type_value: str, year: int):
    return run_calculation(
        self,
        MilitaryDemarcationLineDistanceCalculator,
        year,
        border_type_value,
        BorderType,
    )


@celery_app.task(bind=True)
def calculate_border_port_distance_task(self, border_type_value: str, year: int):
    return run_calculation(
        self, PortDistanceCalculator, year, border_type_value, BorderType
    )


@celery_app.task(bind=True)
def calculate_border_rail_task(self, border_type_value: str, year: int):
    return run_calculation(self, RailCalculator, year, border_type_value, BorderType)


@celery_app.task(bind=True)
def calculate_border_road_task(self, border_type_value: str, year: int):
    return run_calculation(self, RoadCalculator, year, border_type_value, BorderType)


@celery_app.task(bind=True)
def calculate_border_topographic_model_task(self, border_type_value: str, year: int):
    return run_calculation(
        self, TopographicModelCalculator, year, border_type_value, BorderType
    )


@celery_app.task(bind=True)
def calculate_border_raster_emission_task(self, border_type_value: str, year: int):
    return run_calculation(
        self, RasterEmissionCalculator, year, border_type_value, BorderType
    )


@celery_app.task(bind=True)
def calculate_border_clinic_count_task(self, border_type_value: str, year: int):
    return run_calculation(
        self, ClinicBorderCalculator, year, border_type_value, BorderType
    )


@celery_app.task(bind=True)
def calculate_border_hospital_count_task(self, border_type_value: str, year: int):
    return run_calculation(
        self, HospitalBorderCalculator, year, border_type_value, BorderType
    )


# --- Point-based tasks --- POINT
#
# The initial implementation focuses on one example geovariable: distance from a given point to the
# nearest airport for a given year.  This pattern can later be extended to other variables (e.g.
# distance to coastline, counts within a buffer, etc.).
#
# The task updates its state twice – once at the start (0 %) and once at completion (100 %) – so that
# API clients can poll `/job_status/` and render progress bars.  For long‐running, row-by-row
# computations (e.g. CSV batch processing) we will increment this value more frequently in a
# follow-up commit.
#

load_dotenv()

# Separate lightweight connection just for point-based helpers.  Re-using the same URL keeps the
# behaviour identical to the border-based calculators while avoiding tight coupling between modules.
_point_engine = create_engine(os.getenv("DB_URL"))  # type: ignore
_point_conn = _point_engine.connect()


def _distance_to_nearest_airport(lat: float, lon: float, year: int) -> float | None:
    """Return the planar distance (metres) to the nearest airport built in *year*.

    If the underlying table stores geometries in EPSG:5179 (common for Korean national mapping), we
    transform the incoming WGS-84 coordinate accordingly before measuring.  The SQL still works if
    the airport geometry is already in 4326 because redundant transforms are ignored by PostGIS.
    """

    sql = text(
        """
        SELECT
            MIN(
                ST_Distance(
                    ST_Transform(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 5179),
                    ST_Transform(geometry, 5179)
                )
            ) AS distance
        FROM public.airport
        WHERE year = :year;
        """
    )
    result = _point_conn.execute(sql, {"lat": lat, "lon": lon, "year": year}).scalar()
    # ``scalar()`` can return ``None`` if the query produced no rows (e.g., year out of range).
    return float(result) if result is not None else None


@celery_app.task(bind=True, name="calculate_point_airport_distance")
def calculate_point_airport_distance_task(self, lat: float, lon: float, year: int = 2020):
    """Celery task: distance from a single *lat/lon* to the nearest airport (in *year*).

    The task emits progress updates so that callers can show a progress bar while polling the status
    endpoint.  Even though this calculation is usually fast, we keep the pattern consistent for all
    point-based tasks.
    """

    # 0 % – task accepted
    self.update_state(state="PROGRESS", meta={"progress": 0})

    try:
        distance = _distance_to_nearest_airport(lat, lon, year)
        # 100 % – calculation complete
        self.update_state(state="PROGRESS", meta={"progress": 100})
        return {
            "lat": lat,
            "lon": lon,
            "year": year,
            "geovariable": "airport_distance",
            "value": distance,
        }
    except Exception as e:
        # Propagate rich error information to clients
        self.update_state(
            state="FAILURE",
            meta={"exc_type": type(e).__name__, "exc_message": str(e)},
        )
        # Celery will mark the task as failed when we raise again
        raise
