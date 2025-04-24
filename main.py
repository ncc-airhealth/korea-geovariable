import pandas as pd
from fastapi import FastAPI, HTTPException

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

app = FastAPI()


def df_to_json(df: pd.DataFrame):
    return df.to_dict(orient="records")


# --- Border-based endpoints ---
@app.get("/border/river/")
def border_river(border_type: BorderType, year: int):
    try:
        calc = RiverCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/emission/")
def border_emission(border_type: BorderType, year: int):
    try:
        calc = EmissionCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/car_registration/")
def border_car_registration(border_type: BorderType, year: int):
    try:
        calc = CarRegistrationCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/landuse_area/")
def border_landuse_area(border_type: BorderType, year: int):
    try:
        calc = LanduseAreaCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/coastline_distance/")
def border_coastline_distance(border_type: BorderType, year: int):
    try:
        calc = CoastlineDistanceCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/ndvi/")
def border_ndvi(border_type: BorderType, year: int):
    try:
        calc = NdviCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/airport_distance/")
def border_airport_distance(border_type: BorderType, year: int):
    try:
        calc = AirportDistanceCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/mdl_distance/")
def border_mdl_distance(border_type: BorderType, year: int):
    try:
        calc = MilitaryDemarcationLineDistanceCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/port_distance/")
def border_port_distance(border_type: BorderType, year: int):
    try:
        calc = PortDistanceCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/rail/")
def border_rail(border_type: BorderType, year: int):
    try:
        calc = RailCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/road/")
def border_road(border_type: BorderType, year: int):
    try:
        calc = RoadCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/topographic_model/")
def border_topographic_model(border_type: BorderType, year: int):
    try:
        calc = TopographicModelCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/raster_emission/")
def border_raster_emission(border_type: BorderType, year: int):
    try:
        calc = RasterEmissionCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/clinic_count/")
def border_clinic_count(border_type: BorderType, year: int):
    try:
        calc = ClinicBorderCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/border/hospital_count/")
def border_hospital_count(border_type: BorderType, year: int):
    try:
        calc = HospitalBorderCalculator(border_type, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Point-based endpoints ---
@app.get("/point/clinic_count/")
def point_clinic_count(buffer_size: BufferSize, year: int):
    try:
        calc = ClinicCountCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/point/hospital_count/")
def point_hospital_count(buffer_size: BufferSize, year: int):
    try:
        calc = HospitalCountCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/point/business_registration_count/")
def point_business_registration_count(buffer_size: BufferSize, year: int):
    try:
        calc = BusinessRegistrationCountCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/point/business_employee_count/")
def point_business_employee_count(buffer_size: BufferSize, year: int):
    try:
        calc = BusinessEmployeeCountCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/point/house_type_count/")
def point_house_type_count(buffer_size: BufferSize, year: int):
    try:
        calc = HouseTypeCountCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/point/landuse/")
def point_landuse(buffer_size: BufferSize, year: int):
    try:
        calc = LanduseCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Additional Point-based endpoints ---
@app.get("/point/jgg_centroid_raster_value/")
def point_jgg_centroid_raster_value(buffer_size: BufferSize, year: int):
    try:
        calc = JggCentroidRasterValueCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/dem_raster_value/")
def point_dem_raster_value(buffer_size: BufferSize, year: int):
    try:
        calc = DemRasterValueCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/dsm_raster_value/")
def point_dsm_raster_value(buffer_size: BufferSize, year: int):
    try:
        calc = DsmRasterValueCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/jgg_centroid_buffer_count/")
def point_jgg_centroid_buffer_count(buffer_size: BufferSize, year: int):
    try:
        calc = JggCentroidBufferCountCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/bus_stop_count/")
def point_bus_stop_count(buffer_size: BufferSize, year: int):
    try:
        calc = BusStopCountCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/rail_station_count/")
def point_rail_station_count(buffer_size: BufferSize, year: int):
    try:
        calc = RailStationCountCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/jgg_centroid_shortest_distance/")
def point_jgg_centroid_shortest_distance(buffer_size: BufferSize, year: int):
    try:
        calc = JggCentroidShortestDistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/bus_stop_distance/")
def point_bus_stop_distance(buffer_size: BufferSize, year: int):
    try:
        calc = BusStopDistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/airport_distance/")
def point_airport_distance(buffer_size: BufferSize, year: int):
    try:
        calc = PointAirportDistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/rail_distance/")
def point_rail_distance(buffer_size: BufferSize, year: int):
    try:
        calc = RailDistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/rail_station_distance/")
def point_rail_station_distance(buffer_size: BufferSize, year: int):
    try:
        calc = RailStationDistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/coastline_distance/")
def point_coastline_distance(buffer_size: BufferSize, year: int):
    try:
        calc = PointCoastlineDistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/mdl_distance/")
def point_mdl_distance(buffer_size: BufferSize, year: int):
    try:
        calc = MdlDistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/port_distance/")
def point_port_distance(buffer_size: BufferSize, year: int):
    try:
        calc = PointPortDistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/mr1_distance/")
def point_mr1_distance(buffer_size: BufferSize, year: int):
    try:
        calc = Mr1DistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/mr2_distance/")
def point_mr2_distance(buffer_size: BufferSize, year: int):
    try:
        calc = Mr2DistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/road_distance/")
def point_road_distance(buffer_size: BufferSize, year: int):
    try:
        calc = RoadDistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/river_distance/")
def point_river_distance(buffer_size: BufferSize, year: int):
    try:
        calc = RiverDistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/clinic_distance/")
def point_clinic_distance(buffer_size: BufferSize, year: int):
    try:
        calc = ClinicDistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/hospital_distance/")
def point_hospital_distance(buffer_size: BufferSize, year: int):
    try:
        calc = PointHospitalDistanceCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/car_mean/")
def point_car_mean(buffer_size: BufferSize, year: int):
    try:
        calc = CarMeanCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/emission_vector_based/")
def point_emission_vector_based(buffer_size: BufferSize, year: int):
    try:
        calc = EmissionVectorBasedCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/emission_raster_value/")
def point_emission_raster_value(buffer_size: BufferSize, year: int):
    try:
        calc = EmissionRasterValueCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/road_length/")
def point_road_length(buffer_size: BufferSize, year: int):
    try:
        calc = RoadLengthCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/road_length_lane/")
def point_road_length_lane(buffer_size: BufferSize, year: int):
    try:
        calc = RoadLengthLaneCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/road_length_lane_width/")
def point_road_length_lane_width(buffer_size: BufferSize, year: int):
    try:
        calc = RoadLengthLaneWidthCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/abstract_mr_length/")
def point_abstract_mr_length(buffer_size: BufferSize, year: int):
    try:
        calc = AbstractMrLengthCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/mr1_length/")
def point_mr1_length(buffer_size: BufferSize, year: int):
    try:
        calc = Mr1LengthCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/mr2_length/")
def point_mr2_length(buffer_size: BufferSize, year: int):
    try:
        calc = Mr2LengthCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/abstract_mr_length_lane/")
def point_abstract_mr_length_lane(buffer_size: BufferSize, year: int):
    try:
        calc = AbstractMrLengthLaneCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/mr1_length_lane/")
def point_mr1_length_lane(buffer_size: BufferSize, year: int):
    try:
        calc = Mr1LengthLaneCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/mr2_length_lane/")
def point_mr2_length_lane(buffer_size: BufferSize, year: int):
    try:
        calc = Mr2LengthLaneCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/abstract_mr_length_lane_width/")
def point_abstract_mr_length_lane_width(buffer_size: BufferSize, year: int):
    try:
        calc = AbstractMrLengthLaneWidthCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/mr1_length_lane_width/")
def point_mr1_length_lane_width(buffer_size: BufferSize, year: int):
    try:
        calc = Mr1LengthLaneWidthCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/mr2_length_lane_width/")
def point_mr2_length_lane_width(buffer_size: BufferSize, year: int):
    try:
        calc = Mr2LengthLaneWidthCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/population/")
def point_population(buffer_size: BufferSize, year: int):
    try:
        calc = PopulationCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/abstract_ndvi_statistic/")
def point_abstract_ndvi_statistic(buffer_size: BufferSize, year: int):
    try:
        calc = AbstractNdviStatisticCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/ndvi_statistic_mean/")
def point_ndvi_statistic_mean(buffer_size: BufferSize, year: int):
    try:
        calc = NdviStatisticMeanCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/ndvi_statistic_median/")
def point_ndvi_statistic_median(buffer_size: BufferSize, year: int):
    try:
        calc = NdviStatisticMedianCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/ndvi_statistic_min/")
def point_ndvi_statistic_min(buffer_size: BufferSize, year: int):
    try:
        calc = NdviStatisticMinCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/ndvi_statistic_max/")
def point_ndvi_statistic_max(buffer_size: BufferSize, year: int):
    try:
        calc = NdviStatisticMaxCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/ndvi_statistic_8mdn/")
def point_ndvi_statistic_8mdn(buffer_size: BufferSize, year: int):
    try:
        calc = NdviStatistic8mdnCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/point/jgg_centroid_relative_dem_dsm/")
def point_jgg_centroid_relative_dem_dsm(buffer_size: BufferSize, year: int):
    try:
        calc = JggCentroidRelativeDemDsmCalculator(buffer_size, year)
        df = calc.calculate()
        return df_to_json(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.get("/")
def root():
    return {"message": "Korea GeoVariable FastAPI server is running."}
