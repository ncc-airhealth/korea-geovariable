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


class BufferCountCalculator(PointAbstractCalculator):
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


class BusStopCountCalculator(BufferCountCalculator):
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


class RailStationCountCalculator(BufferCountCalculator):
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


class ShortestDistanceCalculator(PointAbstractCalculator):
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


class BusStopDistanceCalculator(ShortestDistanceCalculator):
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


class AirportDistanceCalculator(ShortestDistanceCalculator):
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


class RailDistanceCalculator(ShortestDistanceCalculator):
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


class RailStationDistanceCalculator(ShortestDistanceCalculator):
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


class CoastlineDistanceCalculator(ShortestDistanceCalculator):
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


class MdlDistanceCalculator(ShortestDistanceCalculator):
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


class PortDistanceCalculator(ShortestDistanceCalculator):
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


class Mr1DistanceCalculator(ShortestDistanceCalculator):
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


class Mr2DistanceCalculator(ShortestDistanceCalculator):
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


class RoadDistanceCalculator(ShortestDistanceCalculator):
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


class RiverDistanceCalculator(ShortestDistanceCalculator):
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


if __name__ == "__main__":
    # Example usage
    df = BusStopCountCalculator(BufferSize.SMALL, 2023).calculate()
    df.to_csv("c_bus_300.csv")
