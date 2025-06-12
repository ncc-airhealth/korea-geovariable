import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import json
import math
import requests

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


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def _download_csv_from_supabase(bucket: str, path: str) -> pd.DataFrame:
    """Download a CSV file from Supabase Storage into a pandas DataFrame.

    The function expects the *service role key* to be available via the
    ``SUPABASE_SERVICE_ROLE_KEY`` environment variable so that private files can be accessed.  If
    the bucket is public you can omit the key.
    """

    if os.getenv("SUPABASE_URL") is None:
        raise RuntimeError("SUPABASE_URL environment variable not set")

    download_url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/{bucket}/{path}"
    headers = {}
    if os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        headers = {"apikey": os.getenv("SUPABASE_SERVICE_ROLE_KEY"), "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_ROLE_KEY')}"}

    response = requests.get(download_url, headers=headers, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to download CSV from Supabase (status {response.status_code}): {response.text[:200]}…"
        )

    # Use pandas to read CSV from bytes
    from io import StringIO

    csv_buffer = StringIO(response.text)
    df = pd.read_csv(csv_buffer)
    return df


# ---------------------------------------------------------------------------
# Bulk CSV processing task
# ---------------------------------------------------------------------------


def _extract_lat_lon(row: pd.Series) -> tuple[float, float]:
    """Return latitude and longitude from a pandas Series.

    The function tries multiple column name variants and ignores missing / NaN values.  If neither
    coordinate can be located, it raises ``KeyError`` so that the caller can log the error while
    continuing to process the remaining rows.
    """

    lat_columns = ["lat", "latitude", "LAT", "Latitude", "LATITUDE"]
    lon_columns = ["lon", "lng", "longitude", "LON", "LNG", "Longitude", "LONGITUDE"]

    lat_val = None
    for col in lat_columns:
        val = row.get(col, None)
        if val is not None and pd.notna(val):
            lat_val = val
            break

    lon_val = None
    for col in lon_columns:
        val = row.get(col, None)
        if val is not None and pd.notna(val):
            lon_val = val
            break

    if lat_val is None or lon_val is None:
        raise KeyError(
            "Missing latitude/longitude columns. Expected one of "
            f"{lat_columns} and {lon_columns} but found {list(row.index)}"
        )

    return float(lat_val), float(lon_val)


@celery_app.task(bind=True, name="process_csv_airport_distance")
def process_csv_airport_distance_task(
    self,
    bucket: str,
    path: str,
    *,
    year: int = 2020,
):
    """Bulk‐process a CSV file on Supabase and compute *airport distance* for every row.

    Parameters
    ----------
    bucket, path : str
        Location of the CSV file inside Supabase Storage.
    year : int, default 2020
        Reference year for the airport catalogue.

    Returns
    -------
    list[dict]
        One dictionary per input row augmented with a new key ``airport_distance``.

    Progress reporting
    ------------------
    The task metadata contains:
    * ``progress`` – integer percentage [0-100]
    * ``processed`` – rows processed so far
    * ``total`` – total number of rows
    * ``stage`` – textual description of the current phase (download, parsing, calculation, etc.)
    """

    # --------------------------------------------------
    # Stage 1 – download CSV
    # --------------------------------------------------
    self.update_state(state="PROGRESS", meta={"progress": 0, "stage": "download"})

    try:
        df = _download_csv_from_supabase(bucket, path)
    except Exception as e:
        self.update_state(state="FAILURE", meta={"exc_type": type(e).__name__, "exc_message": str(e)})
        raise

    total_rows = len(df)
    if total_rows == 0:
        return []  # nothing to do

    # --------------------------------------------------
    # Stage 2 – compute geovariable for each row
    # --------------------------------------------------
    results: list[dict] = []

    # We'll emit at most 100 progress updates (1 % granularity) to avoid overwhelming Redis.
    last_reported_pct = -1

    for processed, row in enumerate(df.itertuples(index=False, name=None), start=1):
        # ``row`` is now a tuple; convert to dict using the DataFrame's columns for clarity.
        row_dict_original = dict(zip(df.columns, row))

        try:
            lat, lon = _extract_lat_lon(pd.Series(row_dict_original))
        except Exception as e:
            distance = math.nan
            error_info = str(e)
        else:
            try:
                distance = _distance_to_nearest_airport(lat, lon, year)
                error_info = None
            except Exception as e:
                distance = math.nan
                error_info = str(e)

        augmented = {**row_dict_original, "airport_distance": distance, "error": error_info}
        results.append(augmented)

        pct = int((processed / total_rows) * 100)
        if pct != last_reported_pct:
            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": pct,
                    "processed": processed,
                    "total": total_rows,
                    "stage": "processing",
                },
            )
            last_reported_pct = pct

    # --------------------------------------------------
    # Stage 3 – done
    # --------------------------------------------------
    self.update_state(state="PROGRESS", meta={"progress": 100, "processed": total_rows, "total": total_rows})

    # Celery enforces JSON; ensure proper serialisation (e.g., NaN → null)
    return json.loads(pd.DataFrame(results).to_json(orient="records"))


# ---------------------------------------------------------------------------
# Placeholders for additional geovariables
# ---------------------------------------------------------------------------

# In future commits we will add other point-based calculations following the same pattern, e.g.:
#   * coastline_distance
#   * bus_stop_distance
#   * population_within_buffer
# Each will have both single‐point and CSV‐batch variants.  The low-level SQL should be added to
# point_based_calculations.py for maintainability.
