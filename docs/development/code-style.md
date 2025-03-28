# Code Style Guide

This guide outlines the coding standards and best practices for the Korea Geovariable project.

For examples of our code style in action, see [Examples](../usage/examples.md) and [API Reference](../api/point-based-calculations.md).

## Python Style Guide

### General Guidelines

1. **PEP 8 Compliance**
   - Follow PEP 8 style guide
   - Use 4 spaces for indentation
   - Maximum line length of 88 characters (Black formatter default)
   - Use meaningful variable names
   - Use descriptive function and class names

2. **Type Hints**
   - Use type hints for all function parameters and return values
   - Use type hints for class attributes
   - Use `Optional` for nullable values
   - Use `Union` for multiple possible types

Example:
```python
from typing import Optional, Union, List, Dict
from datetime import datetime

def calculate_population(
    year: int,
    buffer_size: BufferSize,
    include_metadata: bool = False
) -> Dict[str, Union[int, float]]:
    """
    Calculate population statistics.

    Args:
        year: The year to calculate for
        buffer_size: Size of the buffer zone
        include_metadata: Whether to include metadata in results

    Returns:
        Dictionary containing population statistics
    """
    pass
```

3. **Docstrings**
   - Use Google style docstrings
   - Include type information
   - Provide examples for complex functions
   - Document exceptions

Example:
```python
def calculate_ndvi(
    buffer_size: NdviBufferSize,
    year: int
) -> pd.DataFrame:
    """Calculate NDVI (Normalized Difference Vegetation Index).

    Args:
        buffer_size: Size of the buffer zone for calculation
        year: Year to calculate NDVI for

    Returns:
        DataFrame containing NDVI values and metadata

    Raises:
        ValueError: If year is not supported
        DatabaseError: If database query fails
    """
    pass
```

4. **Imports**
   - Group imports in order:
     1. Standard library imports
     2. Third-party imports
     3. Local imports
   - Use absolute imports
   - Import specific items instead of modules

Example:
```python
# Standard library
import os
from typing import List, Optional

# Third-party
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine

# Local
from point_based_calculations import BufferSize, PointAbstractCalculator
```

### Class Design

1. **Class Structure**
   - Use PascalCase for class names
   - Inherit from `object` or appropriate base class
   - Define class attributes first
   - Group methods by type (public, protected, private)

Example:
```python
class PopulationCalculator(PointAbstractCalculator):
    """Calculator for population statistics."""

    def __init__(
        self,
        buffer_size: BufferSize,
        year: int
    ) -> None:
        """Initialize the calculator.

        Args:
            buffer_size: Size of the buffer zone
            year: Year to calculate for
        """
        super().__init__(buffer_size, year)
        self._table_name = "population"
        self._valid_years = range(2015, 2021)

    def calculate(self) -> pd.DataFrame:
        """Calculate population statistics."""
        pass

    def _validate_year(self, year: int) -> None:
        """Validate the year parameter."""
        pass
```

2. **Properties**
   - Use `@property` decorator for read-only attributes
   - Use `@property.setter` for writable attributes
   - Keep property methods simple

Example:
```python
class Calculator:
    @property
    def table_name(self) -> str:
        """Get the table name."""
        return self._table_name

    @table_name.setter
    def table_name(self, value: str) -> None:
        """Set the table name."""
        if not value:
            raise ValueError("Table name cannot be empty")
        self._table_name = value
```

### Function Design

1. **Function Structure**
   - Use snake_case for function names
   - Keep functions focused and small
   - Use descriptive parameter names
   - Return early for error cases

Example:
```python
def calculate_buffer_stats(
    point: Point,
    buffer_size: BufferSize,
    include_metadata: bool = False
) -> Dict[str, float]:
    """Calculate statistics within a buffer zone.

    Args:
        point: Center point of the buffer
        buffer_size: Size of the buffer zone
        include_metadata: Whether to include metadata

    Returns:
        Dictionary of calculated statistics
    """
    if not point.is_valid:
        raise ValueError("Invalid point geometry")

    stats = {}

    # Calculate basic stats
    stats["area"] = calculate_area(point, buffer_size)
    stats["perimeter"] = calculate_perimeter(point, buffer_size)

    if include_metadata:
        stats["metadata"] = get_metadata(point)

    return stats
```

2. **Error Handling**
   - Use specific exceptions
   - Provide meaningful error messages
   - Handle exceptions at appropriate levels
   - Log errors with context

Example:
```python
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    """Process input data.

    Args:
        data: Input DataFrame

    Returns:
        Processed DataFrame

    Raises:
        ValueError: If data is empty or invalid
        ProcessingError: If processing fails
    """
    if data.empty:
        raise ValueError("Input data is empty")

    try:
        # Process data
        result = data.copy()
        result["processed"] = result["value"].apply(process_value)
        return result
    except Exception as e:
        logger.error(f"Failed to process data: {str(e)}")
        raise ProcessingError("Data processing failed") from e
```

### Testing

1. **Test Structure**
   - Use descriptive test names
   - Follow Arrange-Act-Assert pattern
   - Use fixtures for common setup
   - Test edge cases and error conditions

Example:
```python
import pytest
from point_based_calculations import PopulationCalculator

@pytest.fixture
def calculator():
    return PopulationCalculator(
        buffer_size=BufferSize.MEDIUM,
        year=2020
    )

def test_population_calculation(calculator):
    # Arrange
    expected_columns = ["tot_reg_cd", "POP_500"]

    # Act
    result = calculator.calculate()

    # Assert
    assert not result.empty
    assert all(col in result.columns for col in expected_columns)

def test_invalid_year(calculator):
    # Arrange
    calculator.year = 1999

    # Act & Assert
    with pytest.raises(ValueError, match="Year not supported"):
        calculator.calculate()
```

2. **Test Coverage**
   - Aim for high test coverage
   - Test public interfaces thoroughly
   - Include integration tests
   - Mock external dependencies

### Database

1. **SQL Style**
   - Use UPPERCASE for SQL keywords
   - Use snake_case for table and column names
   - Format queries for readability
   - Use parameterized queries

Example:
```python
def get_population_data(year: int) -> pd.DataFrame:
    """Get population data for a specific year.

    Args:
        year: Year to get data for

    Returns:
        DataFrame containing population data
    """
    query = """
        SELECT
            tot_reg_cd,
            population,
            created_at
        FROM population
        WHERE year = :year
        ORDER BY tot_reg_cd
    """

    return pd.read_sql(
        query,
        engine,
        params={"year": year}
    )
```

2. **Database Operations**
   - Use transactions for multiple operations
   - Handle connection errors gracefully
   - Use appropriate indexes
   - Clean up resources

Example:
```python
def update_population_data(data: pd.DataFrame) -> None:
    """Update population data in database.

    Args:
        data: DataFrame containing new data
    """
    try:
        with engine.begin() as connection:
            data.to_sql(
                "population",
                connection,
                if_exists="append",
                index=False
            )
    except Exception as e:
        logger.error(f"Failed to update population data: {str(e)}")
        raise DatabaseError("Population update failed") from e
```

## Next Steps

1. Review the [Contributing Guide](contributing.md)
2. Check [Examples](../usage/examples.md) for usage patterns
3. Review [API Reference](../api/point-based-calculations.md)
