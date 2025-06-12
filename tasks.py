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
from point_based_calculations import (
    BufferSize,
    CustomBusStopCountCalculator,
    CustomHospitalCountCalculator,
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


def run_point_calculation(self, calculator_class, year, coordinates, buffer_size=None):
    """Helper function to run point calculation and handle exceptions."""
    try:
        if buffer_size:
            calc = calculator_class(buffer_size, year, coordinates)
        else:
            calc = calculator_class(year, coordinates)
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


@celery_app.task(bind=True)
def calculate_point_bus_stop_count_task(self, coordinates: list[list[float]], buffer_size_value: int, year: int):
    """Calculate bus stop counts for given coordinates."""
    coord_tuples = [(coord[0], coord[1]) for coord in coordinates]
    buffer_size = BufferSize(buffer_size_value)
    
    return run_point_calculation(self, CustomBusStopCountCalculator, year, coord_tuples, buffer_size)


@celery_app.task(bind=True)
def calculate_point_hospital_count_task(self, coordinates: list[list[float]], buffer_size_value: int, year: int):
    """Calculate hospital counts for given coordinates."""
    coord_tuples = [(coord[0], coord[1]) for coord in coordinates]
    buffer_size = BufferSize(buffer_size_value)
    
    return run_point_calculation(self, CustomHospitalCountCalculator, year, coord_tuples, buffer_size)


@celery_app.task(bind=True)
def calculate_csv_file_task(self, file_id: str, calculator_type: str, buffer_size_value: int, year: int):
    """Process entire CSV file for point-based calculations."""
    from supabase import create_client
    import os
    import pandas as pd
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        file_response = supabase.from_('coordinate_files').select('*').eq('id', file_id).single().execute()
        if not file_response.data:
            raise ValueError(f"File with id {file_id} not found")
        
        file_info = file_response.data
        
        file_data = supabase.storage.from_('csv_files').download(file_info['file_path'])
        
        import io
        csv_content = io.StringIO(file_data.decode('utf-8'))
        df = pd.read_csv(csv_content)
        
        coordinates = [(row['x'], row['y']) for _, row in df.iterrows()]
        
        if calculator_type == 'bus_stop':
            calculator_class = CustomBusStopCountCalculator
        elif calculator_type == 'hospital':
            calculator_class = CustomHospitalCountCalculator
        else:
            raise ValueError(f"Unknown calculator type: {calculator_type}")
        
        buffer_size = BufferSize(buffer_size_value)
        
        batch_size = 100
        total_batches = len(coordinates) // batch_size + (1 if len(coordinates) % batch_size else 0)
        all_results = []
        
        for i in range(0, len(coordinates), batch_size):
            batch_coords = coordinates[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": batch_num,
                    "total": total_batches,
                    "status": f"Processing batch {batch_num} of {total_batches}"
                }
            )
            
            calc = calculator_class(buffer_size, year, batch_coords)
            batch_results = calc.calculate()
            all_results.append(batch_results)
        
        final_df = pd.concat(all_results, ignore_index=True)
        return df_to_json(final_df)
        
    except Exception as e:
        self.update_state(
            state="FAILURE", meta={"exc_type": type(e).__name__, "exc_message": str(e)}
        )
        return {
            "error": str(e),
            "details": f"Failed during CSV processing",
        }
