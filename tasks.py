import pandas as pd

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
