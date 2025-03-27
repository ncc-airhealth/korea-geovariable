# Available Calculators

This guide provides an overview of all available calculators in the Korea Geovariable library.

## Buffer Size Enums

### Standard Buffer Sizes
```python
from point_based_calculations import BufferSize

# Available buffer sizes
BufferSize.VERY_SMALL  # 100m
BufferSize.SMALL      # 300m
BufferSize.MEDIUM     # 500m
BufferSize.LARGE      # 1000m
BufferSize.VERY_LARGE # 5000m
```

### Special Buffer Sizes
```python
from point_based_calculations import NdviBufferSize, EmissionBufferSize

# NDVI buffer sizes
NdviBufferSize.LARGE      # 1000m
NdviBufferSize.VERY_LARGE # 5000m

# Emission buffer sizes
EmissionBufferSize.SMALL  # 3000m
EmissionBufferSize.MEDIUM # 10000m
EmissionBufferSize.LARGE  # 20000m
```

## Raster Value Calculators

### DEM Calculator
```python
from point_based_calculations import DemRasterValueCalculator

calculator = DemRasterValueCalculator()
results = calculator.calculate()
```

### DSM Calculator
```python
from point_based_calculations import DsmRasterValueCalculator

calculator = DsmRasterValueCalculator()
results = calculator.calculate()
```

## Buffer Count Calculators

### Bus Stop Count Calculator
```python
from point_based_calculations import BusStopCountCalculator, BufferSize

calculator = BusStopCountCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2023
)
results = calculator.calculate()
```

### Rail Station Count Calculator
```python
from point_based_calculations import RailStationCountCalculator, BufferSize

calculator = RailStationCountCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

## Distance Calculators

### Bus Stop Distance Calculator
```python
from point_based_calculations import BusStopDistanceCalculator

calculator = BusStopDistanceCalculator(year=2023)
results = calculator.calculate()
```

### Airport Distance Calculator
```python
from point_based_calculations import AirportDistanceCalculator

calculator = AirportDistanceCalculator(year=2020)
results = calculator.calculate()
```

### Rail Distance Calculator
```python
from point_based_calculations import RailDistanceCalculator

calculator = RailDistanceCalculator(year=2020)
results = calculator.calculate()
```

### Rail Station Distance Calculator
```python
from point_based_calculations import RailStationDistanceCalculator

calculator = RailStationDistanceCalculator(year=2020)
results = calculator.calculate()
```

### Coastline Distance Calculator
```python
from point_based_calculations import CoastlineDistanceCalculator

calculator = CoastlineDistanceCalculator(year=2020)
results = calculator.calculate()
```

### MDL Distance Calculator
```python
from point_based_calculations import MdlDistanceCalculator

calculator = MdlDistanceCalculator(year=2020)
results = calculator.calculate()
```

### Port Distance Calculator
```python
from point_based_calculations import PortDistanceCalculator

calculator = PortDistanceCalculator(year=2020)
results = calculator.calculate()
```

### MR1 Distance Calculator
```python
from point_based_calculations import Mr1DistanceCalculator

calculator = Mr1DistanceCalculator(year=2020)
results = calculator.calculate()
```

### MR2 Distance Calculator
```python
from point_based_calculations import Mr2DistanceCalculator

calculator = Mr2DistanceCalculator(year=2020)
results = calculator.calculate()
```

### Road Distance Calculator
```python
from point_based_calculations import RoadDistanceCalculator

calculator = RoadDistanceCalculator(year=2020)
results = calculator.calculate()
```

### River Distance Calculator
```python
from point_based_calculations import RiverDistanceCalculator

calculator = RiverDistanceCalculator(year=2020)
results = calculator.calculate()
```

## Road Length Calculators

### Road Length Calculator
```python
from point_based_calculations import RoadLengthCalculator, BufferSize

calculator = RoadLengthCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

### Road Length Lane Calculator
```python
from point_based_calculations import RoadLengthLaneCalculator, BufferSize

calculator = RoadLengthLaneCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

### Road Length Lane Width Calculator
```python
from point_based_calculations import RoadLengthLaneWidthCalculator, BufferSize

calculator = RoadLengthLaneWidthCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

## MR Length Calculators

### MR1 Length Calculator
```python
from point_based_calculations import Mr1LengthCalculator, BufferSize

calculator = Mr1LengthCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

### MR2 Length Calculator
```python
from point_based_calculations import Mr2LengthCalculator, BufferSize

calculator = Mr2LengthCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

### MR1 Length Lane Calculator
```python
from point_based_calculations import Mr1LengthLaneCalculator, BufferSize

calculator = Mr1LengthLaneCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

### MR2 Length Lane Calculator
```python
from point_based_calculations import Mr2LengthLaneCalculator, BufferSize

calculator = Mr2LengthLaneCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

### MR1 Length Lane Width Calculator
```python
from point_based_calculations import Mr1LengthLaneWidthCalculator, BufferSize

calculator = Mr1LengthLaneWidthCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

### MR2 Length Lane Width Calculator
```python
from point_based_calculations import Mr2LengthLaneWidthCalculator, BufferSize

calculator = Mr2LengthLaneWidthCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

## Population Calculator

```python
from point_based_calculations import PopulationCalculator, BufferSize

calculator = PopulationCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

## Business Calculators

### Business Registration Count Calculator
```python
from point_based_calculations import BusinessRegistrationCountCalculator, BufferSize

calculator = BusinessRegistrationCountCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

### Business Employee Count Calculator
```python
from point_based_calculations import BusinessEmployeeCountCalculator, BufferSize

calculator = BusinessEmployeeCountCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

## House Type Calculator

```python
from point_based_calculations import HouseTypeCountCalculator, BufferSize

calculator = HouseTypeCountCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

## Emission Calculators

### Emission Vector Based Calculator
```python
from point_based_calculations import EmissionVectorBasedCalculator, EmissionBufferSize

calculator = EmissionVectorBasedCalculator(
    buffer_size=EmissionBufferSize.MEDIUM,
    year=2019
)
results = calculator.calculate()
```

## NDVI Calculators

### NDVI Statistic Calculators
```python
from point_based_calculations import (
    NdviStatisticMeanCalculator,
    NdviStatisticMedianCalculator,
    NdviStatisticMinCalculator,
    NdviStatisticMaxCalculator,
    NdviStatistic8mdnCalculator,
    BufferSize
)

# Mean
calculator = NdviStatisticMeanCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()

# Median
calculator = NdviStatisticMedianCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()

# Min
calculator = NdviStatisticMinCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()

# Max
calculator = NdviStatisticMaxCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()

# 8mdn
calculator = NdviStatistic8mdnCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

## Land Use Calculator

```python
from point_based_calculations import LanduseCalculator, BufferSize

calculator = LanduseCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
results = calculator.calculate()
```

## Next Steps

1. Check [Examples](examples.md) for specific use cases
2. Refer to [API Reference](../api/point-based-calculations.md) for detailed documentation
3. Read [Basic Usage](basic-usage.md) for general usage patterns
