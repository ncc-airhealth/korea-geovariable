# Point Based Calculations API Reference

This document provides detailed API documentation for the point-based calculations module.

For usage examples, see [Basic Usage](../usage/basic-usage.md), [Available Calculators](../usage/calculators.md), and [Examples](../usage/examples.md).

## Enums

### BufferSize
```python
class BufferSize(Enum):
    """Valid buffer sizes in meters."""
    VERY_SMALL = 100
    SMALL = 300
    MEDIUM = 500
    LARGE = 1000
    VERY_LARGE = 5000
```

### NdviBufferSize
```python
class NdviBufferSize(Enum):
    """Valid buffer sizes in meters."""
    LARGE = 1000
    VERY_LARGE = 5000
```

### EmissionBufferSize
```python
class EmissionBufferSize(Enum):
    """Valid buffer sizes in meters."""
    SMALL = 3000
    MEDIUM = 10000
    LARGE = 20000
```

## Base Classes

### PointAbstractCalculator
```python
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
```

## Raster Value Calculators

### DemRasterValueCalculator
```python
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
```

### DsmRasterValueCalculator
```python
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
```

## Buffer Count Calculators

### BusStopCountCalculator
```python
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
```

### RailStationCountCalculator
```python
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
```

## Distance Calculators

### BusStopDistanceCalculator
```python
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
        return [2023]
```

### AirportDistanceCalculator
```python
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
        return [2000, 2005, 2010, 2015, 2020]
```

## Road Length Calculators

### RoadLengthCalculator
```python
class RoadLengthCalculator(PointAbstractCalculator):
    """Calculator for road length."""

    def __init__(self, buffer_size: BufferSize, year: int):
        super().__init__(year)
        self.buffer_size = buffer_size

    @property
    def table_name(self) -> str:
        return "roads"

    @property
    def label_prefix(self) -> str:
        return f"Road_L_{str(self.buffer_size.value).zfill(4)}"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

### RoadLengthLaneCalculator
```python
class RoadLengthLaneCalculator(PointAbstractCalculator):
    """Calculator for road length with lanes."""

    def __init__(self, buffer_size: BufferSize, year: int):
        super().__init__(year)
        self.buffer_size = buffer_size

    @property
    def table_name(self) -> str:
        return "roads"

    @property
    def label_prefix(self) -> str:
        return f"Road_LL_{str(self.buffer_size.value).zfill(4)}"

    @property
    def valid_years(self) -> list[int]:
        return [2005, 2010, 2015, 2020]
```

## Population Calculator

### PopulationCalculator
```python
class PopulationCalculator(PointAbstractCalculator):
    """Calculator for population statistics."""

    def __init__(self, buffer_size: BufferSize, year: int):
        super().__init__(year)
        self.buffer_size = buffer_size

    @property
    def table_name(self) -> str:
        return "jgg_adjusted_sgis_pop"

    @property
    def label_prefix(self) -> str:
        return "POP_"

    @staticmethod
    def valid_years() -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

## Business Calculators

### BusinessRegistrationCountCalculator
```python
class BusinessRegistrationCountCalculator(PointAbstractCalculator):
    """Calculator for business registration count."""

    def __init__(self, buffer_size: BufferSize, year: int):
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
        return [2000, 2005, 2010, 2015, 2020]
```

### BusinessEmployeeCountCalculator
```python
class BusinessEmployeeCountCalculator(PointAbstractCalculator):
    """Calculator for business employee count."""

    def __init__(self, buffer_size: BufferSize, year: int):
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
        return [2000, 2005, 2010, 2015, 2020]
```

## House Type Calculator

### HouseTypeCountCalculator
```python
class HouseTypeCountCalculator(PointAbstractCalculator):
    """Calculator for counting types of houses."""

    def __init__(self, buffer_size: BufferSize, year: int):
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
        return [2000, 2005, 2010, 2015, 2020]
```

## Emission Calculators

### EmissionVectorBasedCalculator
```python
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
```

## NDVI Calculators

### NdviStatisticMeanCalculator
```python
class NdviStatisticMeanCalculator(AbstractNdviStatisticCalculator):
    """Calculator for NDVI mean statistics."""

    @property
    def statistic_type(self) -> Literal["mean", "median", "min", "max", "8mdn"]:
        return "mean"
```

### NdviStatisticMedianCalculator
```python
class NdviStatisticMedianCalculator(AbstractNdviStatisticCalculator):
    """Calculator for NDVI median statistics."""

    @property
    def statistic_type(self) -> Literal["mean", "median", "min", "max", "8mdn"]:
        return "median"
```

### NdviStatisticMinCalculator
```python
class NdviStatisticMinCalculator(AbstractNdviStatisticCalculator):
    """Calculator for NDVI minimum statistics."""

    @property
    def statistic_type(self) -> Literal["mean", "median", "min", "max", "8mdn"]:
        return "min"
```

### NdviStatisticMaxCalculator
```python
class NdviStatisticMaxCalculator(AbstractNdviStatisticCalculator):
    """Calculator for NDVI maximum statistics."""

    @property
    def statistic_type(self) -> Literal["mean", "median", "min", "max", "8mdn"]:
        return "max"
```

### NdviStatistic8mdnCalculator
```python
class NdviStatistic8mdnCalculator(AbstractNdviStatisticCalculator):
    """Calculator for NDVI 8mdn statistics."""

    @property
    def statistic_type(self) -> Literal["mean", "median", "min", "max", "8mdn"]:
        return "8mdn"
```

## Land Use Calculator

### LanduseCalculator
```python
class LanduseCalculator(PointAbstractCalculator):
    """Calculator for land use statistics."""

    def __init__(self, buffer_size: BufferSize, year: int):
        super().__init__(year)
        self.buffer_size = buffer_size

    @property
    def table_name(self) -> str:
        if self.year == 2020:
            return "landuse_v004_2020_simplified"
        else:
            return f"landuse_v002_{self.year}"

    @property
    def label_prefix(self) -> str:
        return "LS"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

## Utility Functions

### merge_dataframes_by_id
```python
def merge_dataframes_by_id(
    dataframes: list[pd.DataFrame],
    id_column: str = "id"
) -> pd.DataFrame:
    """
    Merge multiple dataframes on a common ID column.

    Args:
        dataframes: List of dataframes to merge
        id_column: Name of the ID column to merge on

    Returns:
        Merged dataframe with columns reordered to put ID first
    """
```

## Next Steps

1. Check [Examples](../usage/examples.md) for practical use cases
2. Read [Basic Usage](../usage/basic-usage.md) for general usage patterns
3. Review [Available Calculators](../usage/calculators.md) for a complete list of calculators
