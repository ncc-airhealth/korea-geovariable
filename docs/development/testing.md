# Testing Guide

This guide explains how to write and run tests for the Korea Geovariable project.

## Testing Overview

The project uses pytest for testing and follows these principles:
- Test-driven development (TDD) when possible
- Comprehensive test coverage
- Clear test organization
- Efficient test execution

## Test Structure

### 1. Test Directory Layout

```
tests/
├── conftest.py           # Shared fixtures
├── test_point_based_calculations/
│   ├── __init__.py
│   ├── test_dem.py
│   ├── test_population.py
│   └── test_business.py
├── test_database/
│   ├── __init__.py
│   ├── test_connection.py
│   └── test_queries.py
└── test_utils/
    ├── __init__.py
    └── test_helpers.py
```

### 2. Test File Organization

```python
# test_population.py
import pytest
from point_based_calculations import PopulationCalculator, BufferSize

# Fixtures
@pytest.fixture
def calculator():
    return PopulationCalculator(
        buffer_size=BufferSize.MEDIUM,
        year=2020
    )

# Test classes
class TestPopulationCalculator:
    """Test suite for PopulationCalculator."""

    def test_initialization(self, calculator):
        """Test calculator initialization."""
        assert calculator.buffer_size == BufferSize.MEDIUM
        assert calculator.year == 2020

    def test_calculation(self, calculator):
        """Test population calculation."""
        result = calculator.calculate()
        assert not result.empty
        assert "tot_reg_cd" in result.columns
        assert "POP_500" in result.columns

    def test_invalid_year(self):
        """Test invalid year handling."""
        with pytest.raises(ValueError):
            PopulationCalculator(
                buffer_size=BufferSize.MEDIUM,
                year=1999
            )
```

## Test Types

### 1. Unit Tests

Test individual components in isolation:

```python
def test_buffer_size_enum():
    """Test BufferSize enum values."""
    assert BufferSize.SMALL.value == 100
    assert BufferSize.MEDIUM.value == 500
    assert BufferSize.LARGE.value == 1000

def test_calculator_validation():
    """Test calculator validation."""
    calculator = PopulationCalculator(
        buffer_size=BufferSize.MEDIUM,
        year=2020
    )
    assert calculator._validate_year(2020) is None
    with pytest.raises(ValueError):
        calculator._validate_year(1999)
```

### 2. Integration Tests

Test component interactions:

```python
def test_database_connection():
    """Test database connection."""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

def test_calculator_database():
    """Test calculator database operations."""
    calculator = PopulationCalculator(
        buffer_size=BufferSize.MEDIUM,
        year=2020
    )
    result = calculator.calculate()
    assert not result.empty
    assert "tot_reg_cd" in result.columns
```

### 3. End-to-End Tests

Test complete workflows:

```python
def test_full_calculation_pipeline():
    """Test complete calculation pipeline."""
    # Setup
    point = Point(127.0, 37.5)
    calculators = [
        PopulationCalculator(BufferSize.MEDIUM, 2020),
        BusinessCalculator(BufferSize.MEDIUM, 2020),
        RoadLengthCalculator(BufferSize.MEDIUM)
    ]

    # Execute
    results = {}
    for calculator in calculators:
        results[calculator.__class__.__name__] = calculator.calculate()

    # Verify
    assert all(not df.empty for df in results.values())
    assert all("tot_reg_cd" in df.columns for df in results.values())
```

## Test Fixtures

### 1. Shared Fixtures

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from point_based_calculations import BufferSize

@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    return create_engine(TEST_DATABASE_URL)

@pytest.fixture(scope="function")
def calculator():
    """Create calculator instance."""
    return PopulationCalculator(
        buffer_size=BufferSize.MEDIUM,
        year=2020
    )

@pytest.fixture(scope="function")
def test_data():
    """Create test data."""
    return pd.DataFrame({
        "tot_reg_cd": ["11010", "11020"],
        "population": [1000, 2000]
    })
```

### 2. Parameterized Tests

```python
@pytest.mark.parametrize("buffer_size,year", [
    (BufferSize.SMALL, 2020),
    (BufferSize.MEDIUM, 2020),
    (BufferSize.LARGE, 2020)
])
def test_different_buffer_sizes(buffer_size, year):
    """Test different buffer sizes."""
    calculator = PopulationCalculator(
        buffer_size=buffer_size,
        year=year
    )
    result = calculator.calculate()
    assert not result.empty
```

## Mocking

### 1. Database Mocking

```python
from unittest.mock import patch

def test_calculator_with_mock_db():
    """Test calculator with mocked database."""
    mock_data = pd.DataFrame({
        "tot_reg_cd": ["11010"],
        "population": [1000]
    })

    with patch("sqlalchemy.create_engine") as mock_engine:
        mock_engine.return_value.connect.return_value.execute.return_value.fetchall.return_value = mock_data

        calculator = PopulationCalculator(
            buffer_size=BufferSize.MEDIUM,
            year=2020
        )
        result = calculator.calculate()

        assert not result.empty
        assert result.equals(mock_data)
```

### 2. External Service Mocking

```python
def test_external_api():
    """Test external API integration."""
    mock_response = {
        "status": "success",
        "data": {"value": 42}
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response

        result = fetch_external_data()
        assert result == mock_response["data"]
```

## Test Coverage

### 1. Coverage Configuration

```ini
# .coveragerc
[run]
source = point_based_calculations
omit =
    */tests/*
    */migrations/*
    */docs/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
```

### 2. Running Coverage

```bash
# Run tests with coverage
python -m pytest --cov=.

# Generate HTML report
python -m pytest --cov=. --cov-report=html

# Check minimum coverage
python -m pytest --cov=. --cov-report=term-missing --cov-fail-under=80
```

## Performance Testing

### 1. Benchmark Tests

```python
def test_calculation_performance(benchmark):
    """Test calculation performance."""
    calculator = PopulationCalculator(
        buffer_size=BufferSize.MEDIUM,
        year=2020
    )

    result = benchmark(calculator.calculate)
    assert not result.empty
```

### 2. Load Testing

```python
def test_concurrent_calculations():
    """Test concurrent calculations."""
    from concurrent.futures import ThreadPoolExecutor

    calculators = [
        PopulationCalculator(BufferSize.MEDIUM, 2020)
        for _ in range(10)
    ]

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda c: c.calculate(), calculators))

    assert all(not df.empty for df in results)
```

## Running Tests

### 1. Basic Commands

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_population.py

# Run specific test class
python -m pytest tests/test_population.py::TestPopulationCalculator

# Run specific test method
python -m pytest tests/test_population.py::TestPopulationCalculator::test_calculation

# Run with verbose output
python -m pytest -v

# Run with print statements
python -m pytest -s
```

### 2. Advanced Options

```bash
# Run tests in parallel
python -m pytest -n auto

# Run tests matching pattern
python -m pytest -k "test_calculation"

# Run tests with markers
python -m pytest -m "not slow"

# Run tests and generate report
python -m pytest --html=report.html
```

## Test Maintenance

### 1. Test Documentation

```python
def test_complex_calculation():
    """Test complex calculation workflow.

    This test verifies that:
    1. The calculator correctly initializes
    2. The calculation produces expected results
    3. Error cases are handled properly
    4. Edge cases are considered
    """
    pass
```

### 2. Test Organization

- Group related tests in classes
- Use descriptive test names
- Keep tests focused and small
- Use fixtures for common setup

### 3. Test Review

- Review test coverage
- Check test quality
- Update tests with code changes
- Remove obsolete tests

## Next Steps

1. Review the [Contributing Guide](contributing.md)
2. Check [Code Style Guide](code-style.md)
3. Review [Architecture Guide](architecture.md)
