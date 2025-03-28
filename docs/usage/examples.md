# Examples

This guide provides practical examples of using the Korea Geovariable library for various use cases.

## Basic Examples

### 1. Calculating Multiple Variables for a Single Point

```python
from point_based_calculations import (
    DemRasterValueCalculator,
    PopulationCalculator,
    LanduseCalculator,
    BufferSize
)

# Calculate DEM
dem_calculator = DemRasterValueCalculator()
dem_results = dem_calculator.calculate()

# Calculate population
pop_calculator = PopulationCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
pop_results = pop_calculator.calculate()

# Calculate land use
landuse_calculator = LanduseCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)
landuse_results = landuse_calculator.calculate()

# Combine results
combined_results = dem_results.merge(
    pop_results,
    on='tot_reg_cd',
    how='outer'
).merge(
    landuse_results,
    on='tot_reg_cd',
    how='outer'
)

# Save results
combined_results.to_csv('combined_results.csv', index=False)
```

### 2. Analyzing Multiple Buffer Sizes

```python
from point_based_calculations import (
    PopulationCalculator,
    BufferSize,
    pandas as pd
)

# List of buffer sizes to analyze
buffer_sizes = [
    BufferSize.VERY_SMALL,
    BufferSize.SMALL,
    BufferSize.MEDIUM,
    BufferSize.LARGE,
    BufferSize.VERY_LARGE
]

# Calculate population for each buffer size
results = {}
for buffer_size in buffer_sizes:
    calculator = PopulationCalculator(
        buffer_size=buffer_size,
        year=2020
    )
    results[buffer_size.value] = calculator.calculate()

# Combine results
combined_df = pd.DataFrame()
for buffer_size, df in results.items():
    # Rename columns to include buffer size
    df.columns = [f"{col}_{buffer_size}" for col in df.columns]
    if combined_df.empty:
        combined_df = df
    else:
        combined_df = combined_df.merge(
            df,
            on='tot_reg_cd',
            how='outer'
        )

# Save results
combined_df.to_csv('population_by_buffer.csv', index=False)
```

## Advanced Examples

### 1. Analyzing Urban Characteristics

```python
from point_based_calculations import (
    PopulationCalculator,
    BusinessRegistrationCountCalculator,
    RoadLengthCalculator,
    BufferSize
)

def analyze_urban_characteristics(year=2020, buffer_size=BufferSize.MEDIUM):
    # Calculate population density
    pop_calculator = PopulationCalculator(
        buffer_size=buffer_size,
        year=year
    )
    pop_results = pop_calculator.calculate()

    # Calculate business density
    business_calculator = BusinessRegistrationCountCalculator(
        buffer_size=buffer_size,
        year=year
    )
    business_results = business_calculator.calculate()

    # Calculate road density
    road_calculator = RoadLengthCalculator(
        buffer_size=buffer_size,
        year=year
    )
    road_results = road_calculator.calculate()

    # Combine results
    results = pop_results.merge(
        business_results,
        on='tot_reg_cd',
        how='outer'
    ).merge(
        road_results,
        on='tot_reg_cd',
        how='outer'
    )

    # Calculate additional metrics
    results['business_density'] = results['B_bnu_500'] / results['POP_500']
    results['road_density'] = results['Road_L_0500'] / results['POP_500']

    return results

# Run analysis
urban_characteristics = analyze_urban_characteristics()
urban_characteristics.to_csv('urban_characteristics.csv', index=False)
```

### 2. Environmental Analysis

```python
from point_based_calculations import (
    EmissionVectorBasedCalculator,
    NdviStatisticMeanCalculator,
    EmissionBufferSize,
    BufferSize
)

def analyze_environmental_factors(year=2020):
    # Calculate emissions
    emission_calculator = EmissionVectorBasedCalculator(
        buffer_size=EmissionBufferSize.MEDIUM,
        year=2019  # Latest available year
    )
    emission_results = emission_calculator.calculate()

    # Calculate NDVI
    ndvi_calculator = NdviStatisticMeanCalculator(
        buffer_size=BufferSize.MEDIUM,
        year=year
    )
    ndvi_results = ndvi_calculator.calculate()

    # Combine results
    results = emission_results.merge(
        ndvi_results,
        on='tot_reg_cd',
        how='outer'
    )

    # Calculate environmental score
    # (example: higher NDVI and lower emissions = better score)
    results['environmental_score'] = (
        results['NDVI_Y1_mean_0500'] * 0.6 -
        (results['EM_CO_10000'] + results['EM_NOx_10000']) * 0.4
    )

    return results

# Run analysis
environmental_factors = analyze_environmental_factors()
environmental_factors.to_csv('environmental_factors.csv', index=False)
```

### 3. Accessibility Analysis

```python
from point_based_calculations import (
    BusStopDistanceCalculator,
    RailStationDistanceCalculator,
    RoadDistanceCalculator
)

def analyze_accessibility(year=2020):
    # Calculate distances to various facilities
    bus_calculator = BusStopDistanceCalculator(year=year)
    rail_calculator = RailStationDistanceCalculator(year=year)
    road_calculator = RoadDistanceCalculator(year=year)

    # Get results
    bus_results = bus_calculator.calculate()
    rail_results = rail_calculator.calculate()
    road_results = road_calculator.calculate()

    # Combine results
    results = bus_results.merge(
        rail_results,
        on='tot_reg_cd',
        how='outer'
    ).merge(
        road_results,
        on='tot_reg_cd',
        how='outer'
    )

    # Calculate accessibility score
    # (example: lower distances = better accessibility)
    results['accessibility_score'] = (
        1 / (results['D_Bus_2023'] + 1) * 0.4 +
        1 / (results['D_Sub_2020'] + 1) * 0.4 +
        1 / (results['D_Road_2020'] + 1) * 0.2
    )

    return results

# Run analysis
accessibility = analyze_accessibility()
accessibility.to_csv('accessibility_analysis.csv', index=False)
```

## Data Analysis Examples

### 1. Temporal Analysis

```python
from point_based_calculations import (
    PopulationCalculator,
    BusinessRegistrationCountCalculator,
    BufferSize
)

def analyze_temporal_changes(start_year=2000, end_year=2020):
    results = {}

    for year in range(start_year, end_year + 1, 5):
        # Calculate population
        pop_calculator = PopulationCalculator(
            buffer_size=BufferSize.MEDIUM,
            year=year
        )
        pop_results = pop_calculator.calculate()

        # Calculate business registration
        business_calculator = BusinessRegistrationCountCalculator(
            buffer_size=BufferSize.MEDIUM,
            year=year
        )
        business_results = business_calculator.calculate()

        # Combine results
        year_results = pop_results.merge(
            business_results,
            on='tot_reg_cd',
            how='outer'
        )

        results[year] = year_results

    return results

# Run analysis
temporal_changes = analyze_temporal_changes()

# Save results for each year
for year, df in temporal_changes.items():
    df.to_csv(f'temporal_analysis_{year}.csv', index=False)
```

### 2. Spatial Analysis

```python
from point_based_calculations import (
    PopulationCalculator,
    LanduseCalculator,
    BufferSize
)

def analyze_spatial_patterns(year=2020):
    # Calculate population
    pop_calculator = PopulationCalculator(
        buffer_size=BufferSize.MEDIUM,
        year=year
    )
    pop_results = pop_calculator.calculate()

    # Calculate land use
    landuse_calculator = LanduseCalculator(
        buffer_size=BufferSize.MEDIUM,
        year=year
    )
    landuse_results = landuse_calculator.calculate()

    # Combine results
    results = pop_results.merge(
        landuse_results,
        on='tot_reg_cd',
        how='outer'
    )

    # Calculate urbanization index
    # (example: high population and built-up area = high urbanization)
    results['urbanization_index'] = (
        results['POP_500'] * 0.6 +
        (results['LS110_0500'] + results['LS120_0500']) * 0.4
    )

    # Group by urbanization level
    results['urbanization_level'] = pd.qcut(
        results['urbanization_index'],
        q=5,
        labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
    )

    return results

# Run analysis
spatial_patterns = analyze_spatial_patterns()
spatial_patterns.to_csv('spatial_patterns.csv', index=False)
```

## Multiple Calculators - Multiple Years

```python
from point_based_calculations import (
    BufferSize,
    BusinessRegistrationCountCalculator,
    BusinessEmployeeCountCalculator
)

# Initialize variables
buffer_size = BufferSize.MEDIUM
years = [2010, 2015, 2020]
calculators = []

# Create calculators for different years
for year in years:
    calculators.append(BusinessRegistrationCountCalculator(buffer_size, year))
    calculators.append(BusinessEmployeeCountCalculator(buffer_size, year))

# Run calculations
results = []
for calculator in calculators:
    results.append(calculator.calculate())

# Merge results (assuming ID column is 'id')
import pandas as pd
from functools import reduce

final_result = reduce(
    lambda left, right: pd.merge(left, right, on='id', how='outer'),
    results
)

print(final_result.head())
```

## Border-Based Calculation Example

```python
from border_based_calculations_by_year import (
    BorderType,
    RiverCalculator,
    EmissionCalculator,
    LanduseAreaCalculator
)

# Initialize variables
border_type = BorderType.sgg  # Use Sigungu (City/County/District) level
year = 2020
emission_year = 2019  # Emission data is available for different years

# Create calculators
river_calc = RiverCalculator(border_type, year)
emission_calc = EmissionCalculator(border_type, emission_year)
landuse_calc = LanduseAreaCalculator(border_type, year)

# Run calculations
river_result = river_calc.calculate()
emission_result = emission_calc.calculate()
landuse_result = landuse_calc.calculate()

# Merge results
import pandas as pd
from functools import reduce

# Identify the common border code column based on border_type
border_cd = river_calc.border_cd_col  # This will be 'sigungu_cd', 'adm_dr_cd', or 'tot_reg_cd'

final_result = reduce(
    lambda left, right: pd.merge(left, right, on=border_cd, how='outer'),
    [river_result, emission_result, landuse_result]
)

print(f"Combined results for {border_type.value} in {year}:")
print(final_result.head())
```

## Multiple Border Types Example

```python
from border_based_calculations_by_year import (
    BorderType,
    TopographicModelCalculator
)

# Initialize variables
year = 2020
results = {}

# Calculate topographic model data for different border types
for border_type in BorderType:
    calculator = TopographicModelCalculator(border_type, year)
    results[border_type.value] = calculator.calculate()
    print(f"Calculated data for {border_type.value}: {len(results[border_type.value])} rows")

# Process results for each border type separately
for border_type, result_df in results.items():
    print(f"\nSummary for {border_type}:")
    for column in result_df.columns:
        if column.startswith('dem_') or column.startswith('dsm_'):
            print(f"{column}: {result_df[column].mean()}")
```

## Next Steps

1. Check [Available Calculators](calculators.md) for more calculation options
2. Refer to [API Reference](../api/point-based-calculations.md) for detailed documentation
3. Read [Basic Usage](basic-usage.md) for general usage patterns
