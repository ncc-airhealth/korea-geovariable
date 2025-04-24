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
from point_based_calculations import (
    AbstractMrLengthCalculator,
    AbstractMrLengthLaneCalculator,
    AbstractMrLengthLaneWidthCalculator,
    AbstractNdviStatisticCalculator,
    BufferSize,
    BusinessEmployeeCountCalculator,
    BusinessRegistrationCountCalculator,
    BusStopCountCalculator,
    BusStopDistanceCalculator,
    CarMeanCalculator,
    ClinicCountCalculator,
    ClinicDistanceCalculator,
    DemRasterValueCalculator,
    DsmRasterValueCalculator,
    EmissionRasterValueCalculator,
    EmissionVectorBasedCalculator,
    HospitalCountCalculator,
    HouseTypeCountCalculator,
    JggCentroidBufferCountCalculator,
    JggCentroidRasterValueCalculator,
    JggCentroidRelativeDemDsmCalculator,
    JggCentroidShortestDistanceCalculator,
    LanduseCalculator,
    MdlDistanceCalculator,
    Mr1DistanceCalculator,
    Mr1LengthCalculator,
    Mr1LengthLaneCalculator,
    Mr1LengthLaneWidthCalculator,
    Mr2DistanceCalculator,
    Mr2LengthCalculator,
    Mr2LengthLaneCalculator,
    Mr2LengthLaneWidthCalculator,
    NdviStatistic8mdnCalculator,
    NdviStatisticMaxCalculator,
    NdviStatisticMeanCalculator,
    NdviStatisticMedianCalculator,
    NdviStatisticMinCalculator,
    PopulationCalculator,
    RailDistanceCalculator,
    RailStationCountCalculator,
    RailStationDistanceCalculator,
    RiverDistanceCalculator,
    RoadDistanceCalculator,
    RoadLengthCalculator,
    RoadLengthLaneCalculator,
    RoadLengthLaneWidthCalculator,
)
from point_based_calculations import (
    AirportDistanceCalculator as PointAirportDistanceCalculator,
)
from point_based_calculations import (
    CoastlineDistanceCalculator as PointCoastlineDistanceCalculator,
)
from point_based_calculations import (
    HospitalDistanceCalculator as PointHospitalDistanceCalculator,
)
from point_based_calculations import (
    PortDistanceCalculator as PointPortDistanceCalculator,
)


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


@celery_app.task(bind=True)
def calculate_point_clinic_count_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, ClinicCountCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_hospital_count_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, HospitalCountCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_business_registration_count_task(
    self, buffer_size_value: str, year: int
):
    return run_calculation(
        self, BusinessRegistrationCountCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_business_employee_count_task(
    self, buffer_size_value: str, year: int
):
    return run_calculation(
        self, BusinessEmployeeCountCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_house_type_count_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, HouseTypeCountCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_landuse_task(self, buffer_size_value: str, year: int):
    return run_calculation(self, LanduseCalculator, year, buffer_size_value, BufferSize)


@celery_app.task(bind=True)
def calculate_point_jgg_centroid_raster_value_task(
    self, buffer_size_value: str, year: int
):
    return run_calculation(
        self, JggCentroidRasterValueCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_dem_raster_value_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, DemRasterValueCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_dsm_raster_value_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, DsmRasterValueCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_jgg_centroid_buffer_count_task(
    self, buffer_size_value: str, year: int
):
    return run_calculation(
        self, JggCentroidBufferCountCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_bus_stop_count_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, BusStopCountCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_rail_station_count_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, RailStationCountCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_jgg_centroid_shortest_distance_task(
    self, buffer_size_value: str, year: int
):
    return run_calculation(
        self, JggCentroidShortestDistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_bus_stop_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, BusStopDistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_airport_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, PointAirportDistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_rail_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, RailDistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_rail_station_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, RailStationDistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_coastline_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, PointCoastlineDistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_mdl_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, MdlDistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_port_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, PointPortDistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_mr1_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, Mr1DistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_mr2_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, Mr2DistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_road_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, RoadDistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_river_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, RiverDistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_clinic_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, ClinicDistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_hospital_distance_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, PointHospitalDistanceCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_car_mean_task(self, buffer_size_value: str, year: int):
    return run_calculation(self, CarMeanCalculator, year, buffer_size_value, BufferSize)


@celery_app.task(bind=True)
def calculate_point_emission_vector_based_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, EmissionVectorBasedCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_emission_raster_value_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, EmissionRasterValueCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_road_length_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, RoadLengthCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_road_length_lane_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, RoadLengthLaneCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_road_length_lane_width_task(
    self, buffer_size_value: str, year: int
):
    return run_calculation(
        self, RoadLengthLaneWidthCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_abstract_mr_length_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, AbstractMrLengthCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_mr1_length_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, Mr1LengthCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_mr2_length_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, Mr2LengthCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_abstract_mr_length_lane_task(
    self, buffer_size_value: str, year: int
):
    return run_calculation(
        self, AbstractMrLengthLaneCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_mr1_length_lane_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, Mr1LengthLaneCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_mr2_length_lane_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, Mr2LengthLaneCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_abstract_mr_length_lane_width_task(
    self, buffer_size_value: str, year: int
):
    return run_calculation(
        self, AbstractMrLengthLaneWidthCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_mr1_length_lane_width_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, Mr1LengthLaneWidthCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_mr2_length_lane_width_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, Mr2LengthLaneWidthCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_population_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, PopulationCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_abstract_ndvi_statistic_task(
    self, buffer_size_value: str, year: int
):
    return run_calculation(
        self, AbstractNdviStatisticCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_ndvi_statistic_mean_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, NdviStatisticMeanCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_ndvi_statistic_median_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, NdviStatisticMedianCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_ndvi_statistic_min_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, NdviStatisticMinCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_ndvi_statistic_max_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, NdviStatisticMaxCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_ndvi_statistic_8mdn_task(self, buffer_size_value: str, year: int):
    return run_calculation(
        self, NdviStatistic8mdnCalculator, year, buffer_size_value, BufferSize
    )


@celery_app.task(bind=True)
def calculate_point_jgg_centroid_relative_dem_dsm_task(
    self, buffer_size_value: str, year: int
):
    return run_calculation(
        self, JggCentroidRelativeDemDsmCalculator, year, buffer_size_value, BufferSize
    )


# --- End of tasks ---
