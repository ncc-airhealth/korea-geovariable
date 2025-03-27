# Configuration Guide

This guide explains how to configure the Korea Geovariable project for your specific needs.

## Environment Variables

The project uses environment variables for configuration. These are stored in the `.env` file.

### Required Variables

1. **Database Connection**
   ```env
   DB_URL=postgresql://username:password@localhost:5432/database_name
   ```
   - `username`: Your database username
   - `password`: Your database password
   - `localhost`: Database host (default: localhost)
   - `5432`: PostgreSQL port (default: 5432)
   - `database_name`: Name of your database

> **Note**: To obtain the database URL, please contact the system administrators:
>
> - [Han Jimin - 한지민](mailto:hangm0101@ncc.re.kr)
> - [Son Dongook - 손동욱](mailto:d@dou.so)

### Optional Variables

1. **Logging Configuration**
   ```env
   LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
   LOG_FILE=logs/korea_geovariable.log
   ```

2. **Buffer Sizes**
   ```env
   DEFAULT_BUFFER_SIZE=500  # Default buffer size in meters
   ```

## Database Configuration

### PostGIS Setup

1. **Enable PostGIS Extension**
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

2. **Required Tables**
   The following tables should be present in your database:
   - `jgg_centroid_adjusted`
   - `jgg_centroid_adjusted_buffered`
   - `intersection_areas_{buffer_size}`

### Table Structure

Each table should have specific columns:

1. **jgg_centroid_adjusted**
   ```sql
   CREATE TABLE jgg_centroid_adjusted (
       tot_reg_cd VARCHAR(10) PRIMARY KEY,
       geom geometry(Point, 4326)
   );
   ```

2. **jgg_centroid_adjusted_buffered**
   ```sql
   CREATE TABLE jgg_centroid_adjusted_buffered (
       tot_reg_cd VARCHAR(10) PRIMARY KEY,
       geom_{buffer_size} geometry(Polygon, 4326)
   );
   ```

## Python Configuration

### Virtual Environment

The project uses a virtual environment for dependency management. To activate it:

```bash
# On Unix/macOS
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

### Dependencies

Dependencies are managed using `uv`. To update dependencies:

```bash
uv sync
```

## Development Tools

### Pre-commit Hooks

The project uses pre-commit hooks for code quality. To set them up:

```bash
pre-commit install
```

### Code Style

The project follows specific code style guidelines:
- Line length: 88 characters
- Indentation: 4 spaces
- Quote style: Double quotes

## Testing Configuration

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_point_based_calculations.py

# Run with coverage
python -m pytest --cov=.
```

### Test Database

Tests use a separate test database. Configure it in your `.env` file:

```env
TEST_DB_URL=postgresql://username:password@localhost:5432/test_database
```

## Troubleshooting

### Common Configuration Issues

1. **Database Connection Issues**
   - Verify database credentials
   - Check if PostgreSQL is running
   - Ensure PostGIS extension is installed

2. **Environment Variable Issues**
   - Make sure `.env` file exists
   - Check for correct variable names
   - Verify file permissions

3. **Dependency Issues**
   - Try clearing uv cache: `uv cache clean`
   - Update uv: `pip install --upgrade uv`
   - Check Python version compatibility

## Next Steps

After configuration, you can:
1. Read the [Database Setup Guide](database-setup.md) for detailed database configuration
2. Start with [Basic Usage](../usage/basic-usage.md) to learn how to use the library
3. Check [Available Calculators](../usage/calculators.md) for supported calculations
