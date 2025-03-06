import os
from abc import ABC, abstractmethod
from enum import Enum

import pandas as pd
from dotenv import load_dotenv
from dou import logger
from sqlalchemy import create_engine, text

load_dotenv()

# Database connection setup
engine = create_engine(os.getenv("DB_URL"))  # type: ignore
conn = engine.connect()


class BufferSize(Enum):
    """Valid buffer sizes in meters."""

    VERY_SMALL = 100
    SMALL = 300
    MEDIUM = 500
    LARGE = 1000
    VERY_LARGE = 5000


class EmissionBufferSize(Enum):
    """Valid buffer sizes in meters."""

    SMALL = 3000
    MEDIUM = 10000
    LARGE = 20000


def merge_dataframes_by_id(
    dataframes: list[pd.DataFrame], id_column: str = "id"
) -> pd.DataFrame:
    """
    Merge multiple dataframes on a common ID column.

    Args:
        dataframes: List of dataframes to merge
        id_column: Name of the ID column to merge on

    Returns:
        Merged dataframe with columns reordered to put ID first
    """
    if not dataframes:
        raise ValueError("No dataframes provided for merging")

    merged_df = dataframes[0]
    for df in dataframes[1:]:
        merged_df = merged_df.merge(df, on=id_column, how="outer")

    columns = merged_df.columns.tolist()
    columns.remove(id_column)
    columns = [id_column] + columns

    return merged_df[columns]


class PointAbstractCalculator(ABC):
    """Base class for point-based calculations."""

    def __init__(self, year: int):
        """
        Initialize calculator with year.

        Args:
            year: Reference year for the calculation
        """
        self.year = year

    @property
    @abstractmethod
    def table_name(self) -> str:
        """Name of the table to query."""
        pass

    @property
    @abstractmethod
    def label_prefix(self) -> str:
        """Prefix for the count column label."""
        pass

    @property
    @abstractmethod
    def valid_years(self) -> list[int]:
        """List of valid years for this calculator."""
        pass

    @abstractmethod
    def calculate(self) -> pd.DataFrame:
        """
        Execute the point-based calculation.

        Returns:
            DataFrame containing calculation results
        """
        pass

    def validate_year(self) -> None:
        """
        Validate if the year is valid for this calculation.

        Raises:
            ValueError: If the year is invalid
        """
        if self.year not in self.valid_years:
            valid_years_str = ", ".join(map(str, self.valid_years))
            raise ValueError(
                f"Invalid year {self.year}. Valid years are: {valid_years_str}"
            )


class JggCentroidRasterValueCalculator(PointAbstractCalculator):
    """Calculator for raster value."""

    def __init__(self):
        pass

    def calculate(self) -> pd.DataFrame:
        """
        Execute the point-based calculation.

        Returns:
            DataFrame containing calculation results
        """
        if self.table_name == "dem":
            column_name = "Altitude_k"
        elif self.table_name == "dsm":
            column_name = "Altitude_a"
        else:
            raise ValueError(f"Invalid table name: {self.table_name}")

        sql = text(
            f"""SELECT src.tot_reg_cd, ST_Value(dst.rast, 1, src.geom) AS "{column_name}"
            FROM jgg_centroid_adjusted AS src, {self.table_name} AS dst
            WHERE ST_Intersects(src.geom, dst.rast)
            ORDER BY src.tot_reg_cd;
            """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class DemRasterValueCalculator(JggCentroidRasterValueCalculator):
    """Calculator for dem raster value."""

    @property
    def table_name(self) -> str:
        return "dem"

    @property
    def label_prefix(self):
        pass

    @property
    def valid_years(self):
        pass


class DsmRasterValueCalculator(JggCentroidRasterValueCalculator):
    """Calculator for dsm raster value."""

    @property
    def table_name(self) -> str:
        return "dsm"

    @property
    def label_prefix(self):
        pass

    @property
    def valid_years(self):
        pass


class JggCentroidBufferCountCalculator(PointAbstractCalculator):
    """Calculator for buffer count."""

    def __init__(self, buffer_size: BufferSize, year: int):
        super().__init__(year)
        self.buffer_size = buffer_size

    def calculate(self) -> pd.DataFrame:
        """
        Execute the point-based calculation.

        Returns:
            DataFrame containing calculation results
        """
        self.validate_year()
        column_name = f"{self.label_prefix}_{str(self.buffer_size.value).zfill(4)}"

        sql = text(
            f"""
            SELECT
                jb.tot_reg_cd,
                COUNT(t.*) as "{column_name}"
            FROM
                public.jgg_centroid_adjusted_buffered jb
                LEFT JOIN public.{self.table_name} t
                    ON ST_Within(t.geometry, jb.geom_{self.buffer_size.value})
                    AND t.year = {self.year}
            GROUP BY
                jb.tot_reg_cd;
            """
        )

        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class BusStopCountCalculator(JggCentroidBufferCountCalculator):
    """Calculator for bus stop points."""

    @property
    def table_name(self) -> str:
        return "bus_stop"

    @property
    def label_prefix(self) -> str:
        return "C_Bus"

    @property
    def valid_years(self) -> list[int]:
        return [2023]


class RailStationCountCalculator(JggCentroidBufferCountCalculator):
    """Calculator for rail station points."""

    @property
    def table_name(self) -> str:
        return "railstation"

    @property
    def label_prefix(self) -> str:
        return "C_Railstation"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def validate_year(self) -> None:
        if self.year == 2000:
            logger.warning("Year 2000 will be calculated as 2005!")
            self.year = 2005
        super().validate_year()


class JggCentroidShortestDistanceCalculator(PointAbstractCalculator):
    """Calculator for shortest distance to the nearest point."""

    def __init__(self, year: int):
        """
        Initialize calculator with year.

        Args:
            year: Reference year for the calculation
        """
        self.year = year

    def calculate(self) -> pd.DataFrame:
        """
        Execute the point-based calculation.

        Returns:
            DataFrame containing calculation results
        """
        self.validate_year()
        column_name = f"{self.label_prefix}_{self.year}"

        sql = text(
            f"""
            SELECT
                src.tot_reg_cd,
                min(ST_Distance(src.geom, dst.geometry)) AS "{column_name}"
            FROM
                public.jgg_centroid_adjusted AS src
                JOIN public."{self.table_name}" AS dst ON dst.year = {self.year}
            GROUP BY
                src.tot_reg_cd
            ORDER BY
                src.tot_reg_cd;
            """
        )

        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class BusStopDistanceCalculator(JggCentroidShortestDistanceCalculator):
    """Calculator for shortest distance to the nearest bus stop."""

    @property
    def table_name(self) -> str:
        return "bus_stop"

    @property
    def label_prefix(self) -> str:
        return "D_Bus"

    @property
    def valid_years(self) -> list[int]:
        """Return list of valid years for bus stop data.

        Returns:
            List containing valid years (currently only 2023)
        """
        return [2023]


class AirportDistanceCalculator(JggCentroidShortestDistanceCalculator):
    """Calculator for shortest distance to the nearest airport."""

    @property
    def table_name(self) -> str:
        return "airport"

    @property
    def label_prefix(self) -> str:
        return "D_Airport"

    @property
    def valid_years(self) -> list[int]:
        """Return list of valid years for airport data.

        Returns:
            List containing valid years (currently only 2023)
        """
        return [2000, 2005, 2010, 2015, 2020]


class RailDistanceCalculator(JggCentroidShortestDistanceCalculator):
    """Calculator for shortest distance to the nearest rail."""

    @property
    def table_name(self) -> str:
        return "rails"

    @property
    def label_prefix(self) -> str:
        return "D_Rail"

    @property
    def valid_years(self) -> list[int]:
        """Return list of valid years for rail data.

        Returns:
            List containing valid years (You can use 2005 to calculate 2000)
        """
        return [2000, 2005, 2010, 2015, 2020]

    def validate_year(self) -> None:
        if self.year == 2000:
            logger.warning("Year 2000 will be calculated as 2005!")
            self.year = 2005
        super().validate_year()


class RailStationDistanceCalculator(JggCentroidShortestDistanceCalculator):
    """Calculator for shortest distance to the nearest rail station."""

    @property
    def table_name(self) -> str:
        return "railstation"

    @property
    def label_prefix(self) -> str:
        return "D_Sub"

    @property
    def valid_years(self) -> list[int]:
        """Return list of valid years for rail data.

        Returns:
            List containing valid years (You can use 2005 to calculate 2000)
        """
        return [2000, 2005, 2010, 2015, 2020]

    def validate_year(self) -> None:
        if self.year == 2000:
            logger.warning("Year 2000 will be calculated as 2005!")
            self.year = 2005
        super().validate_year()


class CoastlineDistanceCalculator(JggCentroidShortestDistanceCalculator):
    """Calculator for shortest distance to the nearest coastline."""

    @property
    def table_name(self) -> str:
        return "coastline"

    @property
    def label_prefix(self) -> str:
        return "D_Coast"

    @property
    def valid_years(self) -> list[int]:
        """Return list of valid years for rail data.

        Returns:
            List containing valid years
        """
        return [2000, 2005, 2010, 2015, 2020]


class MdlDistanceCalculator(JggCentroidShortestDistanceCalculator):
    """Calculator for shortest distance to the nearest coastline."""

    @property
    def table_name(self) -> str:
        return "mdl"

    @property
    def label_prefix(self) -> str:
        return "D_North"

    @property
    def valid_years(self) -> list[int]:
        """Return list of valid years for rail data.

        Returns:
            List containing valid years
        """
        return [2000, 2005, 2010, 2015, 2020]


class PortDistanceCalculator(JggCentroidShortestDistanceCalculator):
    """Calculator for shortest distance to the nearest port."""

    @property
    def table_name(self) -> str:
        return "port"

    @property
    def label_prefix(self) -> str:
        return "D_Port"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]


class Mr1DistanceCalculator(JggCentroidShortestDistanceCalculator):
    """Calculator for shortest distance to the nearest mr1."""

    @property
    def table_name(self) -> str:
        return "mr1"

    @property
    def label_prefix(self) -> str:
        return "D_MR1"

    @property
    def valid_years(self) -> list[int]:
        return [2005, 2010, 2015, 2020]


class Mr2DistanceCalculator(JggCentroidShortestDistanceCalculator):
    """Calculator for shortest distance to the nearest mr2."""

    @property
    def table_name(self) -> str:
        return "mr2"

    @property
    def label_prefix(self) -> str:
        return "D_MR2"

    @property
    def valid_years(self) -> list[int]:
        return [2005, 2010, 2015, 2020]


class RoadDistanceCalculator(JggCentroidShortestDistanceCalculator):
    """Calculator for shortest distance to the nearest road."""

    @property
    def table_name(self) -> str:
        return "roads"

    @property
    def label_prefix(self) -> str:
        return "D_Road"

    @property
    def valid_years(self) -> list[int]:
        return [2005, 2010, 2015, 2020]


class RiverDistanceCalculator(JggCentroidShortestDistanceCalculator):
    """Calculator for shortest distance to the nearest river."""

    @property
    def table_name(self) -> str:
        return "river"

    @property
    def label_prefix(self) -> str:
        return "D_River"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]


class CarMeanCalculator(PointAbstractCalculator):
    """Calculator for car mean."""

    @property
    def table_name(self) -> str:
        return "car_registration"

    @property
    def label_prefix(self) -> str:
        return "C_Car"

    @property
    def valid_years(self) -> list[int]:
        """List of valid years for this calculator."""
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the point-based calculation.

        Returns:
            DataFrame containing calculation results
        """
        self.validate_year()
        column_name = self.label_prefix
        sql = text(
            f"""
            SELECT
                a.tot_reg_cd,
                b.value as "{column_name}_sigungu_mean_registration"
            FROM
                jgg_centroid_adjusted a
                LEFT JOIN {self.table_name} b
                    ON LEFT(a.tot_reg_cd::text, 5) = b.sgg_cd::text
            WHERE b.year = {self.year}
            ORDER BY
                a.tot_reg_cd;
            """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class BusinessRegistrationCountCalculator(PointAbstractCalculator):
    """Calculator for business registration count."""

    def __init__(self, buffer_size: BufferSize, year: int):
        """
        Initialize calculator with buffer size and year.

        Args:
            buffer_size: Size of the buffer zone
            year: Reference year for the calculation
        """
        super().__init__(year)
        self.buffer_size = buffer_size

    @property
    def table_name(self) -> str:
        return "jgg_adjusted_sgis_bnu"

    @property
    def label_prefix(self) -> str:
        return "B_bnu"

    @property
    def valid_years(self) -> list[int]:
        """Return list of valid years for business registration data."""
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the business registration count calculation with buffer zones.

        Returns:
            DataFrame containing calculation results with business registration count variables
        """
        self.validate_year()
        buffer_value = self.buffer_size.value

        # Generate column expressions for all 19 business registration types
        bnu_columns = [
            f'COALESCE(SUM(p.cp_bnu_{str(i).zfill(3)}::float * ia.intersect_area / ia.border_area), 0) AS "{self.label_prefix}_{i}_{str(buffer_value).zfill(4)}"'
            for i in range(1, 20)
        ]

        # Add expression for sum of all business registration count values
        sum_expr = " + ".join(
            [
                f"COALESCE(SUM(p.cp_bnu_{str(i).zfill(3)}::float * ia.intersect_area / ia.border_area), 0)"
                for i in range(1, 20)
            ]
        )
        bnu_columns.append(f'{sum_expr} AS "B_bnu_{str(buffer_value).zfill(4)}"')

        column_expr = ",\n    ".join(bnu_columns)

        sql = text(
            f"""
            SELECT
                ia.center_reg_cd as tot_reg_cd,
                {column_expr}
            FROM
                intersection_areas_{buffer_value} ia
            LEFT JOIN
                {self.table_name} p
                ON p.tot_reg_cd = ia.border_reg_cd
                AND p.year = {self.year}
            GROUP BY
                ia.center_reg_cd
            ORDER BY
                ia.center_reg_cd;
            """
        )

        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class BusinessEmployeeCountCalculator(PointAbstractCalculator):
    """Calculator for business employee count."""

    def __init__(self, buffer_size: BufferSize, year: int):
        """
        Initialize calculator with buffer size and year.

        Args:
            buffer_size: Size of the buffer zone
            year: Reference year for the calculation
        """
        super().__init__(year)
        self.buffer_size = buffer_size

    @property
    def table_name(self) -> str:
        return "jgg_adjusted_sgis_bem"

    @property
    def label_prefix(self) -> str:
        return "B_bem"

    @property
    def valid_years(self) -> list[int]:
        """Return list of valid years for business employee data."""
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the business Employee count calculation with buffer zones.

        Returns:
            DataFrame containing calculation results with business employee count variables
        """
        self.validate_year()
        buffer_value = self.buffer_size.value

        # Generate column expressions for all 19 business employee types
        bem_columns = [
            f'COALESCE(SUM(p.cp_bem_{str(i).zfill(3)}::float * ia.intersect_area / ia.border_area), 0) AS "{self.label_prefix}_{i}_{str(buffer_value).zfill(4)}"'
            for i in range(1, 20)
        ]

        # Add expression for sum of all business employee count values
        sum_expr = " + ".join(
            [
                f"COALESCE(SUM(p.cp_bem_{str(i).zfill(3)}::float * ia.intersect_area / ia.border_area), 0)"
                for i in range(1, 20)
            ]
        )
        bem_columns.append(f'{sum_expr} AS "B_bem_{str(buffer_value).zfill(4)}"')

        column_expr = ",\n    ".join(bem_columns)

        sql = text(
            f"""
            SELECT
                ia.center_reg_cd as tot_reg_cd,
                {column_expr}
            FROM
                intersection_areas_{buffer_value} ia
            LEFT JOIN
                {self.table_name} p
                ON p.tot_reg_cd = ia.border_reg_cd
                AND p.year = {self.year}
            GROUP BY
                ia.center_reg_cd
            ORDER BY
                ia.center_reg_cd;
            """
        )

        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class HouseTypeCountCalculator(PointAbstractCalculator):
    """Calculator for counting types of houses."""

    def __init__(self, buffer_size: BufferSize, year: int):
        """
        Initialize calculator with buffer size and year.

        Args:
            buffer_size: Size of the buffer zone
            year: Reference year for the calculation
        """
        super().__init__(year)
        self.buffer_size = buffer_size

    @property
    def table_name(self) -> str:
        return "jgg_adjusted_sgis_ho_gb"

    @property
    def label_prefix(self) -> str:
        return "H_gb"

    @property
    def valid_years(self) -> list[int]:
        """Return list of valid years for house type data."""
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the house type count calculation with buffer zones.

        Returns:
            DataFrame containing calculation results with house type count variables
        """
        self.validate_year()
        buffer_value = self.buffer_size.value

        # Generate column expressions for all 6 house type types
        gb_columns = [
            f'COALESCE(SUM(p.ho_gb_{str(i).zfill(3)}::float * ia.intersect_area / ia.border_area), 0) AS "{self.label_prefix}_{i}_{str(buffer_value).zfill(4)}"'
            for i in range(1, 7)
        ]

        # Add expression for sum of all house type count values
        sum_expr = " + ".join(
            [
                f"COALESCE(SUM(p.ho_gb_{str(i).zfill(3)}::float * ia.intersect_area / ia.border_area), 0)"
                for i in range(1, 7)
            ]
        )
        gb_columns.append(f'{sum_expr} AS "H_gb_{str(buffer_value).zfill(4)}"')

        column_expr = ",\n    ".join(gb_columns)

        sql = text(
            f"""
            SELECT
                ia.center_reg_cd as tot_reg_cd,
                {column_expr}
            FROM
                intersection_areas_{buffer_value} ia
            LEFT JOIN
                {self.table_name} p
                ON p.tot_reg_cd = ia.border_reg_cd
                AND p.year = {self.year}
            GROUP BY
                ia.center_reg_cd
            ORDER BY
                ia.center_reg_cd;
            """
        )

        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class EmissionVectorBasedCalculator(PointAbstractCalculator):
    """Calculator for emission based on vector data."""

    def __init__(self, buffer_size: EmissionBufferSize, year: int):
        super().__init__(year)
        self.buffer_size = buffer_size

    @property
    def table_name(self) -> list[str]:
        return ["emission_point", "emission_line", "emission_area"]

    @property
    def label_prefix(self) -> str:
        return "EM"

    @property
    def valid_years(self) -> list[int]:
        return [2010, 2015, 2019]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the emission calculation.

        Returns:
            DataFrame containing calculation results with emission variables
        """
        self.validate_year()
        buffer = self.buffer_size.value
        emission_year = self.year
        label_postfix = str(self.buffer_size.value).zfill(5)

        sql = text(
            f"""
                WITH tmp AS (
                    SELECT
                        a.tot_reg_cd,
                        'emission_area' AS tablename,
                        COALESCE(SUM(b.co),
                            0) AS co,
                        COALESCE(SUM(b.nox),
                            0) AS nox,
                        COALESCE(SUM(b.nh3),
                            0) AS nh3,
                        COALESCE(SUM(b.voc),
                            0) AS voc,
                        COALESCE(SUM(b.pm10),
                            0) AS pm10,
                        COALESCE(SUM(b.sox),
                            0) AS sox,
                        COALESCE(SUM(b.tsp),
                            0) AS tsp
                    FROM
                        "jgg_centroid_adjusted" AS a
                    LEFT JOIN emission_point AS b ON ST_Contains(ST_Buffer(a.geom,
                            {buffer}),
                        b.geometry)
                        AND b.year = {emission_year}
                GROUP BY
                    a.tot_reg_cd
                UNION
                SELECT
                    a.tot_reg_cd,
                    'emission_line' AS tablename,
                    COALESCE(SUM(b.co),
                        0) AS co,
                    COALESCE(SUM(b.nox),
                        0) AS nox,
                    COALESCE(SUM(b.nh3),
                        0) AS nh3,
                    COALESCE(SUM(b.voc),
                        0) AS voc,
                    COALESCE(SUM(b.pm10),
                        0) AS pm10,
                    COALESCE(SUM(b.sox),
                        0) AS sox,
                    COALESCE(SUM(b.tsp),
                        0) AS tsp
                FROM
                    "jgg_centroid_adjusted" AS a
                LEFT JOIN emission_line AS b ON ST_Contains(ST_Buffer(a.geom,
                        {buffer}),
                    b.geometry)
                        AND b.year = {emission_year}
                GROUP BY
                    a.tot_reg_cd
                UNION
                SELECT
                    a.tot_reg_cd,
                    'emission_point' AS tablename,
                    COALESCE(SUM(b.co),
                        0) AS co,
                    COALESCE(SUM(b.nox),
                        0) AS nox,
                    COALESCE(SUM(b.nh3),
                        0) AS nh3,
                    COALESCE(SUM(b.voc),
                        0) AS voc,
                    COALESCE(SUM(b.pm10),
                        0) AS pm10,
                    COALESCE(SUM(b.sox),
                        0) AS sox,
                    COALESCE(SUM(b.tsp),
                        0) AS tsp
                FROM
                    "jgg_centroid_adjusted" AS a
                    LEFT JOIN emission_area AS b ON ST_Contains(ST_Buffer(a.geom,
                            {buffer}),
                        b.geometry)
                        AND b.year = {emission_year}
                GROUP BY
                    a.tot_reg_cd
                )
                SELECT
                    tmp.tot_reg_cd,
                    sum(co) as "{self.label_prefix}_CO_{label_postfix}",
                    sum(nox) as "{self.label_prefix}_NOx_{label_postfix}",
                    sum(nh3) as "{self.label_prefix}_NH3_{label_postfix}",
                    sum(voc) as "{self.label_prefix}_VOC_{label_postfix}",
                    sum(pm10) as "{self.label_prefix}_PM10_{label_postfix}",
                    sum(sox) as "{self.label_prefix}_SOx_{label_postfix}",
                    sum(tsp) as "{self.label_prefix}_TSP_{label_postfix}"
                FROM
                    tmp
                GROUP BY
                    tot_reg_cd;
                    """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class EmissionRasterValueCalculator(PointAbstractCalculator):
    # TODO: data is corrupted
    """Calculator for emission raster values."""

    def __init__(self, buffer_size: EmissionBufferSize, year: int):
        """
        Initialize calculator with buffer size and year.

        Args:
            year: Reference year for the calculation
            emission_type: Type of emission (area, line, point)
            pollutant_type: Type of pollutant (co, nox, nh3, voc, pm10, sox, tsp)
        """
        super().__init__(year)
        self.buffer_size = buffer_size
        self.emission_type = emission_type.lower()
        self.pollutant_type = pollutant_type.lower()

    @property
    def table_name(self) -> str:
        return "emission_raster"

    @property
    def label_prefix(self) -> str:
        return "EM"

    @property
    def valid_years(self) -> list[int]:
        return [2001, 2005, 2010]  # Example valid years, adjust as needed

    def validate_emission_type(self) -> None:
        """
        Validate if the emission type is valid.

        Raises:
            ValueError: If the emission type is invalid
        """
        valid_emission_types = ["area", "line", "point"]
        if self.emission_type not in valid_emission_types:
            valid_types_str = ", ".join(valid_emission_types)
            raise ValueError(
                f"Invalid emission type '{self.emission_type}'. Valid types are: {valid_types_str}"
            )

    def validate_pollutant_type(self) -> None:
        """
        Validate if the pollutant type is valid.

        Raises:
            ValueError: If the pollutant type is invalid
        """
        valid_pollutant_types = ["co", "nox", "nh3", "voc", "pm10", "sox", "tsp"]
        if self.pollutant_type not in valid_pollutant_types:
            valid_types_str = ", ".join(valid_pollutant_types)
            raise ValueError(
                f"Invalid pollutant type '{self.pollutant_type}'. Valid types are: {valid_types_str}"
            )

    def calculate(self) -> pd.DataFrame:
        """
        Execute the emission raster value calculation.

        Returns:
            DataFrame containing calculation results with emission raster values
        """
        self.validate_year()
        self.validate_emission_type()
        self.validate_pollutant_type()

        column_name = f"{self.label_prefix}_{self.emission_type}_{self.pollutant_type}_{self.year}"

        sql = text(
            f"""
            SELECT src.tot_reg_cd,
                   ST_Value(dst.rast, 1, src.geom) AS "{column_name}"
            FROM jgg_centroid_adjusted AS src,
                 {self.table_name} AS dst
            WHERE ST_Intersects(src.geom, dst.rast)
              AND dst.year = {self.year}
              AND dst.emission_type = '{self.emission_type}'
              AND dst.pollutant_type = '{self.pollutant_type}'
            ORDER BY src.tot_reg_cd;

                WITH tmp AS (
                    SELECT
                        a.tot_reg_cd,
                        'emission_area' AS tablename,
                        COALESCE(SUM(b.co),
                            0) AS co,
                        COALESCE(SUM(b.nox),
                            0) AS nox,
                        COALESCE(SUM(b.nh3),
                            0) AS nh3,
                        COALESCE(SUM(b.voc),
                            0) AS voc,
                        COALESCE(SUM(b.pm10),
                            0) AS pm10,
                        COALESCE(SUM(b.sox),
                            0) AS sox,
                        COALESCE(SUM(b.tsp),
                            0) AS tsp
                    FROM
                        "jgg_centroid_adjusted" AS a
                    LEFT JOIN emission_point AS b ON ST_Contains(ST_Buffer(a.geom,
                            {buffer}),
                        b.geometry)
                        AND b.year = {emission_year}
                GROUP BY
                    a.tot_reg_cd
                UNION
                SELECT
                    a.tot_reg_cd,
                    'emission_line' AS tablename,
                    COALESCE(SUM(b.co),
                        0) AS co,
                    COALESCE(SUM(b.nox),
                        0) AS nox,
                    COALESCE(SUM(b.nh3),
                        0) AS nh3,
                    COALESCE(SUM(b.voc),
                        0) AS voc,
                    COALESCE(SUM(b.pm10),
                        0) AS pm10,
                    COALESCE(SUM(b.sox),
                        0) AS sox,
                    COALESCE(SUM(b.tsp),
                        0) AS tsp
                FROM
                    "jgg_centroid_adjusted" AS a
                LEFT JOIN emission_line AS b ON ST_Contains(ST_Buffer(a.geom,
                        {buffer}),
                    b.geometry)
                        AND b.year = {emission_year}
                GROUP BY
                    a.tot_reg_cd
                UNION
                SELECT
                    a.tot_reg_cd,
                    'emission_point' AS tablename,
                    COALESCE(SUM(b.co),
                        0) AS co,
                    COALESCE(SUM(b.nox),
                        0) AS nox,
                    COALESCE(SUM(b.nh3),
                        0) AS nh3,
                    COALESCE(SUM(b.voc),
                        0) AS voc,
                    COALESCE(SUM(b.pm10),
                        0) AS pm10,
                    COALESCE(SUM(b.sox),
                        0) AS sox,
                    COALESCE(SUM(b.tsp),
                        0) AS tsp
                FROM
                    "jgg_centroid_adjusted" AS a
                    LEFT JOIN emission_area AS b ON ST_Contains(ST_Buffer(a.geom,
                            {buffer}),
                        b.geometry)
                        AND b.year = {emission_year}
                GROUP BY
                    a.tot_reg_cd
                )
                SELECT
                    tmp.tot_reg_cd,
                    sum(co) as "{self.label_prefix}_CO_{label_postfix}",
                    sum(nox) as "{self.label_prefix}_NOx_{label_postfix}",
                    sum(nh3) as "{self.label_prefix}_NH3_{label_postfix}",
                    sum(voc) as "{self.label_prefix}_VOC_{label_postfix}",
                    sum(pm10) as "{self.label_prefix}_PM10_{label_postfix}",
                    sum(sox) as "{self.label_prefix}_SOx_{label_postfix}",
                    sum(tsp) as "{self.label_prefix}_TSP_{label_postfix}"
                FROM
                    tmp
                GROUP BY
                    tot_reg_cd;
            """
        )

        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


# TODO: Traffic
# TODO: Population
# TODO: NDVI
# TODO: Landuse
# TODO: Relative DEM, DSM


if __name__ == "__main__":
    for buffer_size in EmissionBufferSize:
        for year in [2010, 2015, 2019]:
            df = EmissionVectorBasedCalculator(buffer_size, year).calculate()
            df.to_csv(f"emission_{buffer_size.value}_{year}.csv")
