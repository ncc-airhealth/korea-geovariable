import os
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from functools import reduce

import pandas as pd
from dotenv import load_dotenv
from dou import logger
from sqlalchemy import create_engine, text
from tqdm import tqdm

load_dotenv()


def pdt(s):
    print(f"\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" + "=" * 60)
    print(s)


# Database connection setup
engine = create_engine(os.getenv("DB_URL"))  # type: ignore
conn = engine.connect()


class BorderType(Enum):
    """Valid border type"""

    sgg = "sgg"
    emd = "emd"
    jgg = "jgg"


class BorderAbstractCalculator(ABC):
    """Base class for border-based calculations."""

    def __init__(self, border_type: BorderType, year: int):
        """
        Initialize calculator with year.

        Args:
            year: Reference year for the calculation
        """
        self.border_type = border_type
        self.year = year

        if border_type.value == "sgg":
            self.border_tbl = f"bnd_sigungu_00_{year}_4q"
            self.border_cd_col = "sigungu_cd"
            self.border_nm_col = "sigungu_nm"
        elif border_type.value == "emd":
            self.border_tbl = f"bnd_dong_00_{year}_4q"
            self.border_cd_col = "adm_dr_cd"
            self.border_nm_col = "adm_dr_nm"
        elif border_type.value == "jgg":
            self.border_tbl = "jgg_borders_2023"
            self.border_cd_col = "tot_reg_cd"
            self.border_nm_col = "tot_reg_cd"

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
        Execute the border-based calculation.

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


class RiverCalculator(BorderAbstractCalculator):
    """Calculator for river variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "river"

    @property
    def label_prefix(self) -> str:
        return "river_area_sum"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the river area calculation within border.

        Returns:
            DataFrame containing calculation results with river area variable
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col

        sql = text(
            f"""
                SELECT
                    b.{border_cd} AS {border_cd},
                    SUM(COALESCE(ST_Area(ST_Intersection(r.geometry, b.geom)), 0)) AS {self.label_prefix}
                FROM
                    {border_tbl} AS b
                    LEFT JOIN river r ON ST_Intersects(b.geom, r.geometry)
                GROUP BY
                    b.{border_cd}
                ORDER BY
                    b.{border_cd};
                """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class EmissionCalculator(BorderAbstractCalculator):
    """Calculator for emission variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)
        border_year_map = {2000: 2000, 2005: 2005, 2010: 2010, 2015: 2015, 2020: 2020}
        self.border_tbl = self.border_tbl.replace(f"{year}", f"{border_year_map[year]}")

    @property
    def table_name(self) -> str:
        return "emission"

    @property
    def label_prefix(self) -> str:
        return "EM"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the emission within border.

        Returns:
            DataFrame containing calculation results with emission variables
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        year = self.year
        label = self.label_prefix
        matter_alias = {
            "co": "CO",
            "nox": "NOx",
            "nh3": "NH3",
            "voc": "VOC",
            "pm10": "PM10",
            "sox": "SOx",
            "tsp": "TSP",
        }

        sql = text(
            f"""
            WITH tmp AS (
                SELECT
                    b.{border_cd} AS {border_cd},
                    'emission_point' AS tablename,
                    {",\n".join([f"COALESCE(SUM(ep.{m}),0) AS {m}" for m in matter_alias.keys()])}
                FROM
                    {border_tbl} AS b
                LEFT JOIN "public".emission_point AS ep 
                    ON st_contains(b.geom, ep.geometry)
                    AND ep.year = {year}
                GROUP BY
                    b.{border_cd}
                UNION
                SELECT
                    b.{border_cd},
                    'emission_line' AS tablename,
                    {",\n".join([f"COALESCE(SUM(el.{m}),0) AS {m}" for m in matter_alias.keys()])}
                FROM
                    {border_tbl} AS b
                LEFT JOIN "public".emission_line AS el 
                    ON st_contains(b.geom, el.geometry)
                    AND el.year = {year}
                GROUP BY
                    b.{border_cd}
                UNION
                SELECT
                    b.{border_cd},
                    'emission_area' AS tablename,
                    {",\n".join([f"COALESCE(SUM(ea.{m}),0) AS {m}" for m in matter_alias.keys()])}
                FROM
                    {border_tbl} AS b
                LEFT JOIN "public".emission_area AS ea 
                    ON st_contains(b.geom, ea.geometry)
                    AND ea.year = {year}
                GROUP BY
                    b.{border_cd}
            )
            SELECT
                {border_cd},
                {",\n".join([f'sum({m}) AS "{label}_{M}_{year}"' for m, M in matter_alias.items()])}
            FROM
                tmp
        GROUP BY
            {border_cd}
        ORDER BY
            {border_cd};
        """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class CarRegistrationCalculator(BorderAbstractCalculator):
    """Calculator for car registration number variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "car_registration"

    @property
    def label_prefix(self) -> str:
        return "car_registration"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the car registration variable calculation within border.
        # 해당 지리변수는 읍면동 단위의 원데이터가 없기 때문에 읍면동 단위 지리변수는 시군구의 값을 그대로 사용함
        Returns:
            DataFrame containing calculation results with river area variable
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        year = self.year

        sql = text(
            f"""
            SELECT
                b.{border_cd} AS {border_cd},
                year,
                value as sigungu_car_registration,
                st_area(b.geom) as area,
                st_area(b.geom) / value as area_per_car
            FROM
                {border_tbl} AS b
            JOIN car_registration AS c
                ON LEFT(b.{border_cd}::text, 5) = c.sgg_cd::text
            WHERE c.year = {year}
            ORDER BY {border_cd}
            """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class LanduseAreaCalculator(BorderAbstractCalculator):
    """Calculator for car registration landuse area/ratio variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "landuse"

    @property
    def label_prefix(self) -> str:
        return "lu"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the landuse area/ratio variable calculation within border calculation.
        Returns:
            DataFrame containing calculation results with river area variable
        """
        self.validate_year()
        year = self.year
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        border_nm = self.border_nm_col
        landuse_table = f"landuse_v002_{year}"
        codes = [110, 120, 130, 140, 150, 160, 200, 310, 320, 330, 400, 500, 600, 710]

        df_list = []
        for code in tqdm(codes, desc=f"({year}) landuse area/ratio calculation "):
            area_col_name = f"lu_{code}_area"
            ratio_col_name = f"lu_{code}_ratio"

            sql = text(
                f"""SELECT
                    b.{border_cd} AS {border_cd},
                    sum(ST_Area(ST_Intersection(l.geometry, b.geom))) AS {area_col_name},
                    sum(ST_Area(ST_Intersection(l.geometry, b.geom))) / MAX(ST_Area(b.geom)) AS {ratio_col_name}
                FROM
                    {border_tbl} AS b
                    LEFT JOIN {landuse_table} AS l 
                    ON ST_Intersects(l.geometry, b.geom)
                GROUP BY
                    b.{border_cd}, 
                """
            )
            try:
                result = conn.execute(sql)
                rows = result.all()
                df = pd.DataFrame([dict(row._mapping) for row in rows])
                df_list.append(df)
            except Exception as e:
                logger.error(f"Error in {self.__class__.__name__}: {e}")
                raise

        df_merged = reduce(
            lambda ldf, rdf: pd.merge(ldf, rdf, on=[border_cd, border_nm], how="outer"),
            df_list,
        )
        return df_merged


class CoastlineDistanceCalculator(BorderAbstractCalculator):
    """Calculator for distance from coastline to border centroid variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "coastline"

    @property
    def label_prefix(self) -> str:
        return "centroid_to_coastline"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the distance from coastline to border centroid calculation.

        Returns:
            DataFrame containing calculation results with distance variable
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        year = self.year

        sql = text(
            f"""
            SELECT
                b.{border_cd} AS {border_cd},
                ST_Distance(ST_Centroid(b.geom), ST_Transform(c.geom, 5179)) AS {self.label_prefix}
            FROM
                {border_tbl} AS b, 
                {self.table_name}_{year} AS c
            ORDER BY {border_cd}
            """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class NdviCalculator(BorderAbstractCalculator):
    """Calculator for NDVI variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "ndvi"

    @property
    def label_prefix(self) -> str:
        return "ndvi"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the NDVI calculation.

        Returns:
            DataFrame containing calculation results with ndvi statistics in borders variable
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        year = self.year
        stat_types = ["count", "sum", "mean", "std", "min", "max"]

        sql = text(
            f"""
            WITH ndvi_merged AS (
                SELECT
                    b.{border_cd} AS {border_cd}
                    , ST_Union(ST_Clip (n.rast, b.geom)) AS clipped_rast
                FROM
                    {border_tbl} AS b
                    , {self.table_name} AS n
                WHERE
                    n.year = {year}
                    AND ST_Intersects(n.rast, b.geom)
                GROUP BY
                    b.{border_cd}
            )
            SELECT
                nm.{border_cd} AS {border_cd}
                , ST_SummaryStats(nm.clipped_rast, 1, TRUE) AS stats
            FROM ndvi_merged AS nm
            """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            df = pd.DataFrame([dict(row._mapping) for row in rows])

            str2tuple = lambda x: x[1:-1].split(",")
            for sti, stat_type in enumerate(stat_types):
                df[f"{self.label_prefix}_{stat_type}"] = df["stats"].apply(
                    lambda x: str2tuple(x)[sti]
                )
            df = df.drop(["stats"], axis=1)
            return df
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class AirportDistanceCalculator(BorderAbstractCalculator):
    """Calculator for nearest airport distance variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "airport"

    @property
    def label_prefix(self) -> str:
        return "distance_to_nearest_airport"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the nearest airport distance calculation within border.
        Returns:
            DataFrame containing calculation results with nearest airport distance variable
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        year = self.year

        sql = text(
            f"""
            WITH airport_distance_tbl AS (
                -- calculate distance between border centroid & airport 
                SELECT
                    b.{border_cd} AS {border_cd}
                    , a.name AS airport_name
                    , ST_Distance(ST_Centroid(b.geom), a.geometry) AS airport_distance
                FROM
                    {border_tbl} AS b
                    CROSS JOIN airport AS a
                WHERE a.year = {year}
            ), airport_distance_rank_tbl AS (
                -- calculate distance rank (minimum is 1)
                SELECT 
                    *
                    ,  ROW_NUMBER() OVER (PARTITION BY ad.{border_cd} ORDER BY airport_distance ASC) AS distance_rank
                FROM airport_distance_tbl AS ad
            )
            -- select minimum distance airport
            SELECT 
                {border_cd}
                , airport_name
                , airport_distance AS {self.label_prefix}
            FROM airport_distance_rank_tbl
            WHERE distance_rank = 1
            """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class MilitaryDemarcationLineDistanceCalculator(BorderAbstractCalculator):
    """Calculator for distance from mdl to border centroid variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "mdl"

    @property
    def label_prefix(self) -> str:
        return "mdl"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the distance from mdl to border centroid calculation.

        Returns:
            DataFrame containing calculation results with distance variable
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        year = self.year

        sql = text(
            f"""
            WITH mdl_sel AS (
                SELECT ST_Union(l.geometry) AS geometry
                FROM mdl AS l
                WHERE l.year = {year}
            )
            SELECT 
                b.{border_cd} AS {border_cd}
                , ST_Distance( ST_Centroid(b.geom), ms.geometry ) AS {self.label_prefix}_distance
            FROM
                {border_tbl} AS b
                , mdl_sel AS ms
            ORDER BY {border_cd}
            """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class PortDistanceCalculator(BorderAbstractCalculator):
    """Calculator for distance from port to border centroid variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "ports"

    @property
    def label_prefix(self) -> str:
        return "port"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the distance from port to border centroid calculation.

        Returns:
            DataFrame containing calculation results with distance variable
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        year = self.year

        sql = text(
            f"""
            WITH port_distance_tbl AS (
                -- calculate distance between border centroid & port 
                SELECT
                    b.{border_cd} AS {border_cd}
                    , p.alias AS {self.label_prefix}_alias
                    , ST_Distance(ST_Centroid(b.geom), p.geometry) AS port_distance
                FROM
                    {border_tbl} AS b
                    CROSS JOIN {self.table_name} AS p
                WHERE p.year = {year}
            ), port_distance_rank_tbl AS (
                -- calculate distance rank (minimum is 1)
                SELECT 
                    *
                    ,  ROW_NUMBER() OVER (PARTITION BY pd.{border_cd} ORDER BY {self.label_prefix}_distance ASC) AS distance_rank
                FROM port_distance_tbl AS pd
            )
            -- select minimum distance port
            SELECT 
                {border_cd}
                , {self.label_prefix}_alias
                , {self.label_prefix}_distance
            FROM port_distance_rank_tbl
            WHERE distance_rank = 1
            """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class RailCalculator(BorderAbstractCalculator):
    """Calculator for intersecting rail variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "rails"

    @property
    def label_prefix(self) -> str:
        return "rail"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the rail length calculation within border.

        Returns:
            DataFrame containing calculation results with rail length variable
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        year = self.year
        sql = text(
            f"""
                WITH rail_1year AS ( SELECT * FROM {self.table_name} WHERE year = {year} )
                SELECT
                    b.{border_cd} AS {border_cd},
                    COALESCE(SUM( (ST_Length(ST_Intersection(r.geometry, b.geom)) ), 0) AS {self.label_prefix}_length
                FROM
                    {border_tbl} AS b
                    LEFT JOIN rail_1year r ON ST_Intersects(b.geom, r.geometry)
                GROUP BY
                    b.{border_cd}
                ORDER BY
                    b.{border_cd};
                """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class RoadCalculator(BorderAbstractCalculator):
    """Calculator for intersecting road variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "roads"

    @property
    def label_prefix(self) -> str:
        return "road"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self, verbose=False) -> pd.DataFrame:
        """
        Execute the road length calculation within border.

        Returns:
            DataFrame containing calculation results with road length variable
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        year = self.year
        if year == 2000:
            year = 2005

        try:
            result = conn.execute(text(f"SELECT {border_cd} FROM {border_tbl}"))
            border_id_df = pd.DataFrame([dict(row._mapping) for row in result.all()])
            row_dict_list = []
            for _, border_sr in tqdm(
                border_id_df.iterrows(), total=len(border_id_df), disable=not verbose
            ):
                sel_border_cd = int(border_sr[border_cd])
                # print(type(sel_border_cd), sel_border_cd)
                sql = text(
                    f"""
                        WITH 
                            road_1year AS ( SELECT * FROM {self.table_name} WHERE year = {year} )
                            , border_sel AS ( SELECT * FROM {border_tbl} WHERE CAST({border_cd} AS BIGINT) = {sel_border_cd} ) 
                        SELECT
                            bs.{border_cd} AS {border_cd}
                            , COALESCE(SUM( ST_Length(ST_Intersection(r.geometry, bs.geom))), 0) AS {self.label_prefix}_length
                        FROM
                            border_sel AS bs
                            LEFT JOIN road_1year r ON ST_Intersects(bs.geom, r.geometry)
                        GROUP BY
                            bs.{border_cd}
                    """
                )
                result = conn.execute(sql)
                row_dict_list = row_dict_list + [
                    dict(row._mapping) for row in result.all()
                ]

            return pd.DataFrame(row_dict_list)

        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class TopographicModelCalculator(BorderAbstractCalculator):
    """Calculator for topographic model(dem/dsm) variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "topo"

    @property
    def label_prefix(self) -> str:
        return "topo"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the dem/dsm calculation.

        Returns:
            DataFrame containing calculation results with dsm statistics in borders variable
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        year = self.year
        stat_types = ["count", "sum", "mean", "std", "min", "max"]
        topo_types = ["dem", "dsm"]

        sql_dict = {
            topo_type: text(
                f"""
                WITH {topo_type}_merged AS (
                    SELECT
                        b.{border_cd} AS {border_cd}
                        , ST_Union(ST_Clip (t.rast, b.geom)) AS clipped_rast
                    FROM
                        {border_tbl} AS b
                        , {topo_type} AS t
                    WHERE
                        ST_Intersects(t.rast, b.geom)
                    GROUP BY
                        b.{border_cd}
                )
                SELECT
                    {border_cd}
                    , ST_SummaryStats(clipped_rast, 1, TRUE) AS stats
                FROM 
                    {topo_type}_merged
                """
            )
            for topo_type in topo_types
        }
        try:
            topo_df_dict = {}
            for topo_type, sql in sql_dict.items():
                result = conn.execute(sql)
                rows = result.all()
                df = pd.DataFrame([dict(row._mapping) for row in rows])
                str2tuple = lambda x: x[1:-1].split(",")
                for sti, stat_type in enumerate(stat_types):
                    df[f"{topo_type}_{stat_type}"] = df["stats"].apply(
                        lambda x: str2tuple(x)[sti]
                    )
                df = df.drop(["stats"], axis=1)
                topo_df_dict[topo_type] = df

            df = pd.merge(
                topo_df_dict[topo_types[0]],
                topo_df_dict[topo_types[1]],
                on=[border_cd],
                how="outer",
            )
            return df

        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class RasterEmissionCalculator(BorderAbstractCalculator):
    """Calculator for raster emission variable"""

    def __init__(self, border_type: BorderType, year: int):
        super().__init__(border_type, year)
        border_year_map = {2001: 2000, 2005: 2005, 2010: 2010, 2015: 2015, 2019: 2020}
        self.border_tbl = self.border_tbl.replace(f"{year}", f"{border_year_map[year]}")

    @property
    def table_name(self) -> str:
        return "emission_raster"

    @property
    def label_prefix(self) -> str:
        return "r_emission"

    @property
    def valid_years(self) -> list[int]:
        return [2001, 2005, 2010, 2015, 2019]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the raster emission calculator within border.

        Returns:
            DataFrame containing calculation results with raster emission variables
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        year = self.year
        label = self.label_prefix
        matter_alias = {
            "co": "CO",
            "nox": "NOx",
            "nh3": "NH3",
            "voc": "VOC",
            "pm10": "PM10",
            "sox": "SOx",
            "tsp": "TSP",
        }

        sql = lambda matter: text(
            f"""
            WITH tmp1 AS (
                SELECT *
                FROM {self.table_name} AS e
                WHERE
                    e.year = '{year}'
                    AND e.alias = '{matter}'
            ), tmp2 AS (
                SELECT ST_MapAlgebra(rp, 1, rl, 1, '[rast1] + [rast2]', '32BF'::text) AS rast
                FROM (
                    SELECT
                        (SELECT rast FROM tmp1 WHERE geom_type = 'point') AS rp, 
                        (SELECT rast FROM tmp1 WHERE geom_type = 'line') AS rl
                )
            ), emission_sum AS (
                SELECT ST_MapAlgebra(rpl, 1, ra, 1, '[rast1] + [rast2]', '32BF'::text) AS rast
                FROM (
                    SELECT
                        (SELECT rast FROM tmp2) AS rpl, 
                        (SELECT rast FROM tmp1 WHERE geom_type = 'area') AS ra
                )
            )
            SELECT
                b.{border_cd} AS {border_cd}
                , ( ST_SummaryStats(ST_Clip(es.rast, b.geom), 1) ).sum AS {label}_{matter}
            FROM
                {border_tbl} AS b
                , emission_sum AS es
            WHERE 
                ST_Intersects(es.rast, b.geom)
            ;
            """
        )

        try:
            df_list = []
            for matter in matter_alias.keys():
                result = conn.execute(sql(matter))
                rows = result.all()
                df_list.append(pd.DataFrame([dict(row._mapping) for row in rows]))

            df_merged = reduce(
                lambda ldf, rdf: pd.merge(ldf, rdf, on=[border_cd], how="outer"),
                df_list,
            )
            return df_merged

        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise


class ClinicBorderCalculator(BorderAbstractCalculator):
    """Calculator for clinic count variable within borders."""

    def __init__(self, border_type: BorderType, year: int):
        # Year is needed for border table selection, but not for clinic data filtering
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "clinics"

    @property
    def label_prefix(self) -> str:
        return "clinic_count"

    @property
    def valid_years(self) -> list[int]:
        # Clinic data itself isn't year-specific, but border tables are.
        # Return the years valid for border tables.
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the clinic count calculation within borders.

        Returns:
            DataFrame containing calculation results with clinic count variable.
        """
        # Year validation is for the border table year
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        calculation_year = self.year  # Use the year for filtering clinics

        sql = text(
            f"""
            SELECT
                b.{border_cd} AS {border_cd},
                COUNT(c.*) AS {self.label_prefix}
            FROM
                {border_tbl} AS b
                LEFT JOIN {self.table_name} AS c
                    ON ST_Contains(b.geom, c.geom)
                    AND c.date <= '{calculation_year}-12-31'
                    AND (c.date_c IS NULL OR c.date_c >= '{calculation_year}-01-01')
                    AND c.operation = 1
            GROUP BY
                b.{border_cd}
            ORDER BY
                b.{border_cd};
            """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise

    def validate_year(self) -> None:
        """Validate border year."""
        # Use base class validation which checks against valid_years
        super().validate_year()


class HospitalBorderCalculator(BorderAbstractCalculator):
    """Calculator for hospital count variable within borders."""

    def __init__(self, border_type: BorderType, year: int):
        # Year is needed for border table selection, but not for hospital data filtering
        super().__init__(border_type, year)

    @property
    def table_name(self) -> str:
        return "hospitals"

    @property
    def label_prefix(self) -> str:
        return "hospital_count"

    @property
    def valid_years(self) -> list[int]:
        # Hospital data itself isn't year-specific, but border tables are.
        # Return the years valid for border tables.
        return [2000, 2005, 2010, 2015, 2020]

    def calculate(self) -> pd.DataFrame:
        """
        Execute the hospital count calculation within borders.

        Returns:
            DataFrame containing calculation results with hospital count variable.
        """
        # Year validation is for the border table year
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        calculation_year = self.year  # Use the year for filtering hospitals

        sql = text(
            f"""
            SELECT
                b.{border_cd} AS {border_cd},
                COUNT(h.*) AS {self.label_prefix}
            FROM
                {border_tbl} AS b
                LEFT JOIN {self.table_name} AS h
                    ON ST_Contains(b.geom, h.geom)
                    AND h.date <= '{calculation_year}-12-31'
                    AND (h.date_c IS NULL OR h.date_c >= '{calculation_year}-01-01')
                    AND h.operation = 1
            GROUP BY
                b.{border_cd}
            ORDER BY
                b.{border_cd};
            """
        )
        try:
            result = conn.execute(sql)
            rows = result.all()
            return pd.DataFrame([dict(row._mapping) for row in rows])
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise

    def validate_year(self) -> None:
        """Validate border year."""
        # Use base class validation which checks against valid_years
        super().validate_year()


# test DB connection
# if __name__ == "__main__":
#     pdt(engine)
#     pdt(conn)

# test river variable calculator
# if __name__ == "__main__":
#     for border_type in BorderType:
#         for year in [2000, 2005, 2010, 2015, 2020]:
#             pdt(f"{border_type.value} {year}")
#             df = RiverCalculator(border_type, year).calculate()
#             print(df.sample(3))

# test Emission variable calculator
# if __name__ == "__main__":
#     for border_type in BorderType:
#         for year in [2019, 2005, 2010, 2015, 2019]:
#             pdt(f"{border_type.value} {year}")
#             df = EmissionCalculator(border_type, year).calculate()
#             print(df.sample(3))

# test Car registration number variable calculator
# if __name__ == "__main__":
#     for border_type in BorderType:
#         for year in [2000, 2005, 2010, 2015, 2020]:
#             pdt(f"{border_type.value} {year}")
#             df = CarRegistrationCalculator(border_type, year).calculate()
#             print(df.sample(3))

# test landuse area&ratio variable calculator
# if __name__ == "__main__":
#     for border_type in BorderType:
#         for year in [2000, 2005, 2010, 2015, 2020]:
#             pdt(f"{border_type.value} {year}")
#             df = LanduseAreaCalculator(border_type, year).calculate()
#             print(df.sample())

# test Minumum distance to coastline variable calculator
# if __name__ == "__main__":
#     for border_type in BorderType:
#         for year in [2000, 2005, 2010, 2015, 2020]:
#             pdt(f"{border_type.value} {year}")
#             df = CoastlineDistanceCalculator(border_type, year).calculate()
#             print(df.sample(3))

# test NDVI statistics variable calculator
# if __name__ == "__main__":
#     for border_type in BorderType:
#         for year in [2000, 2005, 2010, 2015, 2020]:
#             pdt(f"{border_type.value} {year}")
#             df = NdviCalculator(border_type, year).calculate()
#             print(df.sample(3))

# test Minumum distance airport variable calculator
# if __name__ == "__main__":
#     for border_type in BorderType:
#         for year in [2000, 2005, 2010, 2015, 2020]:
#             pdt(f"{border_type.value} {year}")
#             df = AirportDistanceCalculator(border_type, year).calculate()
#             print(df.sample(3))

# test Minumum distance mdl variable calculator
# if __name__ == "__main__":
#     for border_type in BorderType:
#         for year in [2000, 2005, 2010, 2015, 2020]:
#             pdt(f"{border_type.value} {year}")
#             df = MilitaryDemarcationLineDistanceCalculator(border_type, year).calculate()
#             print(df.sample(3))

# test Minumum distance port variable calculator
# if __name__ == "__main__":
#     for border_type in BorderType:
#         for year in [2000, 2005, 2010, 2015, 2020]:
#             pdt(f"{border_type.value} {year}")
#             df = PortDistanceCalculator(border_type, year).calculate()
#             print(df.sample(3))

# test Intersecting rail length variable calculator
# if __name__ == "__main__":
#     for border_type in BorderType:
#         for year in [2000, 2005, 2010, 2015, 2020]:
#             pdt(f"{border_type.value} {year}")
#             df = RailCalculator(border_type, year).calculate()
#             print(df.sample(5))

# test Intersecting road length variable calculator
# sigungu   about 17m
# emd       about 13m (faster than sigungu, maybe caused by memory caching)
# jgg       mor than 24 hours expected. if needed, gonna change the logic.
# if __name__ == "__main__":
#     for border_type in BorderType:
#         for year in [2005, 2010, 2015, 2020]:
#             pdt(f"{border_type.value} {year}")
#             df = RoadCalculator(border_type, year).calculate(verbose=True)
#             print(df.sample(5))

# test topo statistics variable calculator
# sigungu   about 6m
# emd       about 2m
# jgg       about 7m
# if __name__ == "__main__":
#     for border_type in BorderType:
#         for year in [2000, 2005, 2010, 2015, 2020]:
#             pdt(f"{border_type.value} {year}")
#             df = TopographicModelCalculator(border_type, year).calculate()
#             print(df.shape)
#             print(df.sample(5))

# test raster emission statistics variable calculator
# sigungu   about 6m
# emd       about 2m
# jgg       about 7m
if __name__ == "__main__":
    for border_type in BorderType:
        for year in [2000, 2005, 2010, 2015, 2020]:
            pdt(f"{border_type.value} {year}")
            df = HospitalBorderCalculator(border_type, year).calculate()
            print(df.shape)
            print(df.sample(5))
