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


class BorderType(Enum):
    """Valid border type"""
    emd = "emd"
    sgg = "sgg"


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
        if border_type.value == "emd":
            self.border_tbl = f"bnd_dong_00_{year}_4q"
            self.border_cd_col  = f"adm_dr_cd"
            self.border_nm_col = f"adm_dr_nm"
        elif border_type.value == "sgg":
            self.border_tbl = f"bnd_sigungu_00_{year}_4q"
            self.border_cd_col  = f"sigungu_cd"
            self.border_nm_col = f"sigungu_nm"

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
        border_nm = self.border_nm_col

        sql = text(
            f"""
                SELECT
                    b.{border_cd} AS border_cd,
                    b.{border_nm} AS border_nm,
                    SUM(COALESCE(ST_Area(ST_Intersection(r.geometry, b.geom)), 0)) AS {self.label_prefix}
                FROM
                    {border_tbl} AS b
                    LEFT JOIN river r ON ST_Intersects(b.geom, r.geometry)
                GROUP BY
                    b.{border_cd},
                    b.{border_nm}
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
        border_year_map = {2001: 2000, 2005: 2005, 2010: 2010, 2015:2015, 2019: 2020}
        self.border_tbl = self.border_tbl.replace(f"{year}", f"{border_year_map[year]}") 

    @property
    def table_name(self) -> str:
        return "emission"

    @property
    def label_prefix(self) -> str:
        return "EM"

    @property
    def valid_years(self) -> list[int]:
        return [2001, 2005, 2010, 2015, 2019]
    
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
            "co": "CO", "nox": "NOx", "nh3": "NH3", "voc": "VOC", 
            "pm10": "PM10", "sox": "SOx", "tsp": "TSP"
        }

        sql = text(
            f"""
            WITH tmp AS (
                SELECT
                    b.{border_cd},
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

        sql = text(
            f"""
            SELECT
                b.{border_cd} AS border_id,
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


if __name__ == "__main__":
    print(engine)
    print(conn)

    # for border_type in BorderType:
    #     for year in [2000, 2005, 2010, 2015, 2020]:
    #         print(border_type.value, year)
    #         df = RiverCalculator(border_type, year).calculate()
    #         print(df.sample(3))
    # for border_type in BorderType:
    #     for year in [2019, 2005, 2010, 2015, 2019]:
    #         df = EmissionCalculator(border_type, year).calculate()
    #         print(df.sample(3))
    for border_type in BorderType:
        for year in [2000, 2005, 2010, 2015, 2020]:
            df = CarRegistrationCalculator(border_type, year).calculate()
            print(df.sample(3))