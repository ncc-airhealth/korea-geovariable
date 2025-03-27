# Korea Geovariable

A Python library for calculating geospatial variables for Korean urban areas.

## Overview

Korea Geovariable is a comprehensive library for calculating various geospatial variables for Korean urban areas. It provides a set of calculators for analyzing population, business, housing, environmental, and accessibility characteristics within buffer zones.

## Features

- Point-based calculations with various buffer sizes
- Support for multiple data sources:
  - Administrative boundaries
  - Census tracts
  - Points of interest
  - Road network
  - Population data
  - Business data
  - Housing data
  - Environmental data
- Efficient spatial analysis using PostGIS
- Comprehensive documentation
- Extensive test coverage

## Installation

### Prerequisites

- Python 3.11 or later
- PostgreSQL 14 or later with PostGIS extension
- `uv` package manager

### Quick Start

```bash
# Clone repository
git clone https://github.com/ncc-airhealth/korea-geovariable
cd korea-geovariable

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
uv sync

# Set up environment variables
cp .env.template .env
# Edit .env with your configuration
```

### Database Setup

> **Note**: To obtain the database URL, please contact the system administrators:
>
> - [Han Jimin - 한지민](mailto:hangm0101@ncc.re.kr)
> - [Son Dongook - 손동욱](mailto:d@dou.so)

## Usage

### Basic Example

```python
from point_based_calculations import PopulationCalculator, BufferSize

# Create calculator
calculator = PopulationCalculator(
    buffer_size=BufferSize.MEDIUM,
    year=2020
)

# Calculate population statistics
results = calculator.calculate()

# Print results
print(results)
```

### Advanced Example

```python
from point_based_calculations import (
    PopulationCalculator,
    BusinessCalculator,
    RoadLengthCalculator,
    BufferSize
)

# Create calculators
calculators = [
    PopulationCalculator(BufferSize.MEDIUM, 2020),
    BusinessCalculator(BufferSize.MEDIUM, 2020),
    RoadLengthCalculator(BufferSize.MEDIUM)
]

# Calculate multiple variables
results = {}
for calculator in calculators:
    results[calculator.__class__.__name__] = calculator.calculate()

# Combine results
combined_results = pd.concat(results.values(), axis=1)
```

## Documentation

- [Installation Guide](docs/getting-started/installation.md)
- [Configuration Guide](docs/getting-started/configuration.md)
- [Database Setup](docs/getting-started/database.md)
- [Basic Usage](docs/usage/basic-usage.md)
- [Available Calculators](docs/usage/calculators.md)
- [Examples](docs/usage/examples.md)
- [API Reference](docs/api/point-based-calculations.md)

## Development

- [Contributing Guide](docs/development/contributing.md)
- [Code Style Guide](docs/development/code-style.md)
- [Architecture Guide](docs/development/architecture.md)
- [Testing Guide](docs/development/testing.md)
- [Database Guide](docs/development/database.md)
- [Deployment Guide](docs/development/deployment.md)
- [Troubleshooting Guide](docs/development/troubleshooting.md)

## Testing

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_point_based_calculations.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

See [Contributing Guide](docs/development/contributing.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
