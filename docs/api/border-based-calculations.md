# Border Based Calculations API Reference

This document provides detailed API documentation for the border-based calculations module.

For usage examples, see [Basic Usage](../usage/basic-usage.md), [Available Calculators](../usage/calculators.md), and [Examples](../usage/examples.md).

## Enums

### BorderType
```python
class BorderType(Enum):
    """Valid border type"""
    sgg = "sgg"  # Sigungu (City/County/District)
    emd = "emd"  # Eup/Myeon/Dong (Town/Township/Neighborhood)
    jgg = "jgg"  # Custom research grid
```

## Base Classes

### BorderAbstractCalculator
```python
class BorderAbstractCalculator(ABC):
    """Base class for border-based calculations."""

    def __init__(self, border_type: BorderType, year: int):
        """
        Initialize calculator with border type and year.

        Args:
            border_type: Type of administrative border to use
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
```

## Geographical Features Calculators

### RiverCalculator
```python
class RiverCalculator(BorderAbstractCalculator):
    """Calculator for river variable"""

    @property
    def table_name(self) -> str:
        return "river"

    @property
    def label_prefix(self) -> str:
        return "river_area_sum"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

### LanduseAreaCalculator
```python
class LanduseAreaCalculator(BorderAbstractCalculator):
    """Calculator for car registration landuse area/ratio variable"""

    @property
    def table_name(self) -> str:
        return "landuse"

    @property
    def label_prefix(self) -> str:
        return "lu"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

### NdviCalculator
```python
class NdviCalculator(BorderAbstractCalculator):
    """Calculator for NDVI variable"""

    @property
    def table_name(self) -> str:
        return "ndvi"

    @property
    def label_prefix(self) -> str:
        return "ndvi"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

### TopographicModelCalculator
```python
class TopographicModelCalculator(BorderAbstractCalculator):
    """Calculator for topographic model(dem/dsm) variable"""

    @property
    def table_name(self) -> str:
        return "topo"

    @property
    def label_prefix(self) -> str:
        return "topo"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

## Transport Feature Calculators

### RailCalculator
```python
class RailCalculator(BorderAbstractCalculator):
    """Calculator for intersecting rail variable"""

    @property
    def table_name(self) -> str:
        return "rails"

    @property
    def label_prefix(self) -> str:
        return "rail"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

### RoadCalculator
```python
class RoadCalculator(BorderAbstractCalculator):
    """Calculator for intersecting road variable"""

    @property
    def table_name(self) -> str:
        return "roads"

    @property
    def label_prefix(self) -> str:
        return "road"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

### CarRegistrationCalculator
```python
class CarRegistrationCalculator(BorderAbstractCalculator):
    """Calculator for car registration number variable"""

    @property
    def table_name(self) -> str:
        return "car_registration"

    @property
    def label_prefix(self) -> str:
        return "car_registration"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

## Distance Calculators

### CoastlineDistanceCalculator
```python
class CoastlineDistanceCalculator(BorderAbstractCalculator):
    """Calculator for distance from coastline to border centroid variable"""

    @property
    def table_name(self) -> str:
        return "coastline"

    @property
    def label_prefix(self) -> str:
        return "centroid_to_coastline"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

### AirportDistanceCalculator
```python
class AirportDistanceCalculator(BorderAbstractCalculator):
    """Calculator for nearest airport distance variable"""

    @property
    def table_name(self) -> str:
        return "airport"

    @property
    def label_prefix(self) -> str:
        return "distance_to_nearest_airport"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

### MilitaryDemarcationLineDistanceCalculator
```python
class MilitaryDemarcationLineDistanceCalculator(BorderAbstractCalculator):
    """Calculator for distance from mdl to border centroid variable"""

    @property
    def table_name(self) -> str:
        return "mdl"

    @property
    def label_prefix(self) -> str:
        return "mdl"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

### PortDistanceCalculator
```python
class PortDistanceCalculator(BorderAbstractCalculator):
    """Calculator for distance from port to border centroid variable"""

    @property
    def table_name(self) -> str:
        return "ports"

    @property
    def label_prefix(self) -> str:
        return "port"

    @property
    def valid_years(self) -> list[int]:
        return [2000, 2005, 2010, 2015, 2020]
```

## Emission Calculators

### EmissionCalculator
```python
class EmissionCalculator(BorderAbstractCalculator):
    """Calculator for emission variable"""

    @property
    def table_name(self) -> str:
        return "emission"

    @property
    def label_prefix(self) -> str:
        return "EM"

    @property
    def valid_years(self) -> list[int]:
        return [2001, 2005, 2010, 2015, 2019]
```

### RasterEmissionCalculator
```python
class RasterEmissionCalculator(BorderAbstractCalculator):
    """Calculator for raster emission variable"""

    @property
    def table_name(self) -> str:
        return "emission_raster"

    @property
    def label_prefix(self) -> str:
        return "r_emission"

    @property
    def valid_years(self) -> list[int]:
        return [2001, 2005, 2010, 2015, 2019]
```

## Next Steps

1. Check [Examples](../usage/examples.md) for practical use cases
2. Read [Basic Usage](../usage/basic-usage.md) for general usage patterns
3. Review [Available Calculators](../usage/calculators.md) for a complete list of calculators 