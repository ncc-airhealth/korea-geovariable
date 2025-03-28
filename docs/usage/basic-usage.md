# Basic Usage

This guide explains how to use the Korea Geovariable library for common tasks.

## Getting Started

### Importing the Library

```python
from point_based_calculations import (
    BufferSize,
    DemRasterValueCalculator,
    PopulationCalculator,
    LanduseCalculator
)
```

### Basic Calculator Usage

All calculators follow a similar pattern:

1. Create a calculator instance with required parameters
2. Call the `calculate()` method
3. Process the results

## Common Use Cases

### 1. Calculating DEM Values

```python
# Create calculator instance
calculator = DemRasterValueCalculator()

# Calculate values
results = calculator.calculate()

# View results
print(results.head())
```

### 2. Calculating Population Statistics

```python
# Create calculator with buffer size and year
calculator = PopulationCalculator(
    buffer_size=BufferSize.MEDIUM,  # 500m buffer
    year=2020
)

# Calculate population statistics
results = calculator.calculate()

# View results
print(results.head())
```

### 3. Analyzing Land Use

```python
# Create calculator with buffer size and year
calculator = LanduseCalculator(
    buffer_size=BufferSize.LARGE,  # 1000m buffer
    year=2020
)

# Calculate land use statistics
results = calculator.calculate()

# View results
print(results.head())
```

## Working with Results

### DataFrame Operations

All calculators return pandas DataFrames. You can perform standard pandas operations:

```python
# Filter results
filtered_results = results[results['tot_reg_cd'].str.startswith('11')]

# Sort results
sorted_results = results.sort_values('POP_500')

# Calculate statistics
stats = results.describe()
```

### Saving Results

```python
# Save to CSV
results.to_csv('population_stats.csv', index=False)

# Save to Excel
results.to_excel('population_stats.xlsx', index=False)
```

## Advanced Usage

### 1. Combining Multiple Calculations

```python
# Calculate multiple variables
dem_results = DemRasterValueCalculator().calculate()
pop_results = PopulationCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
).calculate()

# Merge results
combined_results = dem_results.merge(
    pop_results,
    on='tot_reg_cd',
    how='outer'
)
```

### 2. Using Different Buffer Sizes

```python
# Available buffer sizes
buffer_sizes = [
    BufferSize.VERY_SMALL,  # 100m
    BufferSize.SMALL,       # 300m
    BufferSize.MEDIUM,      # 500m
    BufferSize.LARGE,       # 1000m
    BufferSize.VERY_LARGE   # 5000m
]

# Calculate for multiple buffer sizes
for buffer_size in buffer_sizes:
    calculator = PopulationCalculator(
        buffer_size=buffer_size,
        year=2020
    )
    results = calculator.calculate()
    print(f"Results for {buffer_size.value}m buffer:")
    print(results.head())
```

### 3. Error Handling

```python
try:
    calculator = PopulationCalculator(
        buffer_size=BufferSize.MEDIUM,
        year=2020
    )
    results = calculator.calculate()
except Exception as e:
    print(f"Error calculating population statistics: {e}")
```

## Best Practices

1. **Buffer Size Selection**
   - Use smaller buffers (100m-500m) for detailed local analysis
   - Use larger buffers (1000m-5000m) for broader area analysis
   - Consider the scale of your research question

2. **Year Selection**
   - Use the most recent year for current analysis
   - Use historical years for trend analysis
   - Check available years for each calculator

3. **Performance Optimization**
   - Use appropriate buffer sizes to balance accuracy and performance
   - Consider using spatial indexes for large datasets
   - Cache results when performing multiple calculations

4. **Data Validation**
   - Always check results for expected ranges
   - Verify coordinate systems match
   - Validate against known values when possible

## Common Issues and Solutions

### 1. Database Connection Issues

```python
# Check database connection
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DB_URL"))
try:
    with engine.connect() as conn:
        print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")
```

### 2. Missing Data

```python
# Handle missing values
results = calculator.calculate()
results = results.fillna(0)  # Replace NaN with 0
# or
results = results.dropna()    # Remove rows with missing values
```

### 3. Performance Issues

```python
# Use smaller buffer sizes for testing
test_calculator = PopulationCalculator(
    buffer_size=BufferSize.VERY_SMALL,  # 100m buffer
    year=2020
)
test_results = test_calculator.calculate()
```

## Next Steps

1. Explore [Available Calculators](calculators.md) for more calculation options
2. Check [Examples](examples.md) for specific use cases
3. Refer to [API Reference](../api/point-based-calculations.md) for detailed documentation
