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
        Execute the house type count calculation with buffer zones.

        Returns:
            DataFrame containing calculation results with house type count variables
        """
        self.validate_year()
        border_tbl = self.border_tbl
        border_cd = self.border_cd_col
        border_nm = self.border_nm_col
        table_name = self.table_name

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

if __name__ == "__main__":
    print(engine)
    print(conn)

    for border_type in BorderType:
        for year in [2000, 2005, 2010, 2015, 2020]:
            print(border_type.value, year)
            df = RiverCalculator(border_type, year).calculate()
            print(df.sample(3))
