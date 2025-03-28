# Architecture Guide

This guide explains the architecture and design decisions of the Korea Geovariable project.

## Overview

The Korea Geovariable project is designed to provide a comprehensive set of geospatial variables for analysis of Korean urban areas. The architecture follows a modular, extensible design that allows for easy addition of new variables and calculators.

## Core Components

### 1. Point-Based Calculations

The core functionality revolves around point-based calculations, where each calculation is performed for a specific point location with various buffer sizes. For detailed API documentation, see [Point-Based Calculations API Reference](../api/point-based-calculations.md).

#### Base Calculator
```python
class PointAbstractCalculator:
    """Abstract base class for point-based calculations."""

    def __init__(self, buffer_size: BufferSize, year: int):
        self.buffer_size = buffer_size
        self.year = year

    @abstractmethod
    def calculate(self) -> pd.DataFrame:
        """Calculate variables for the given point."""
        pass
```

#### Calculator Types

1. **Raster Value Calculators**
   - Calculate values from raster data (e.g., DEM, NDVI)
   - Use PostGIS raster functions
   - Example: `DemCalculator`, `NdviCalculator`

2. **Buffer Count Calculators**
   - Count features within buffer zones
   - Use PostGIS spatial queries
   - Example: `BusStopCountCalculator`, `SubwayCountCalculator`

3. **Distance Calculators**
   - Calculate distances to features
   - Use PostGIS distance functions
   - Example: `SubwayDistanceCalculator`, `HospitalDistanceCalculator`

4. **Road Length Calculators**
   - Calculate road lengths within buffers
   - Use PostGIS line functions
   - Example: `RoadLengthCalculator`

5. **Population Calculators**
   - Calculate population statistics
   - Use census data
   - Example: `PopulationCalculator`

6. **Business Calculators**
   - Calculate business-related statistics
   - Use business registration data
   - Example: `BusinessCalculator`

7. **House Type Calculators**
   - Calculate housing statistics
   - Use housing data
   - Example: `HouseTypeCalculator`

8. **Emission Calculators**
   - Calculate emission statistics
   - Use emission data
   - Example: `EmissionCalculator`

### 2. Database Structure

The project uses PostgreSQL with PostGIS extension for spatial data storage and analysis.

#### Core Tables

1. **Spatial Reference Tables**
   ```sql
   -- Administrative boundaries
   CREATE TABLE adm_cd (
       tot_reg_cd VARCHAR(10) PRIMARY KEY,
       name VARCHAR(100),
       geom geometry(MultiPolygon, 5179)
   );

   -- Census tracts
   CREATE TABLE census_tract (
       tract_cd VARCHAR(10) PRIMARY KEY,
       tot_reg_cd VARCHAR(10),
       geom geometry(MultiPolygon, 5179)
   );
   ```

2. **Feature Tables**
   ```sql
   -- Points of interest
   CREATE TABLE poi (
       id SERIAL PRIMARY KEY,
       type VARCHAR(50),
       name VARCHAR(100),
       geom geometry(Point, 5179)
   );

   -- Road network
   CREATE TABLE road (
       id SERIAL PRIMARY KEY,
       type VARCHAR(50),
       name VARCHAR(100),
       geom geometry(LineString, 5179)
   );
   ```

3. **Variable Tables**
   ```sql
   -- Population data
   CREATE TABLE population (
       tot_reg_cd VARCHAR(10),
       year INTEGER,
       population INTEGER,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- Business data
   CREATE TABLE business (
       tot_reg_cd VARCHAR(10),
       year INTEGER,
       count INTEGER,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

### 3. Data Flow

1. **Input Data**
   - Administrative boundaries
   - Census tracts
   - Points of interest
   - Road network
   - Population data
   - Business data
   - Housing data
   - Emission data

2. **Processing Pipeline**
   ```mermaid
   graph TD
       A[Input Data] --> B[Data Validation]
       B --> C[Data Processing]
       C --> D[Database Storage]
       D --> E[Variable Calculation]
       E --> F[Result Output]
   ```

3. **Output Data**
   - CSV files
   - GeoJSON files
   - Database tables

### 4. Configuration Management

The project uses a hierarchical configuration system:

1. **Environment Variables**
   ```bash
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=korea_geovariable
   DB_USER=postgres
   DB_PASSWORD=password
   ```

2. **Configuration Files**
   ```yaml
   # config.yaml
   database:
     host: ${DB_HOST}
     port: ${DB_PORT}
     name: ${DB_NAME}
     user: ${DB_USER}
     password: ${DB_PASSWORD}

   calculations:
     default_buffer_size: MEDIUM
     supported_years: [2015, 2016, 2017, 2018, 2019, 2020]
   ```

### 5. Error Handling

The project implements a comprehensive error handling system:

1. **Custom Exceptions**
   ```python
   class DatabaseError(Exception):
        """Raised when database operations fail."""
        pass

   class ValidationError(Exception):
        """Raised when data validation fails."""
        pass

   class CalculationError(Exception):
        """Raised when calculations fail."""
        pass
   ```

2. **Error Logging**
   ```python
   import logging

   logger = logging.getLogger(__name__)

   def calculate_variable(self):
       try:
           # Calculation logic
           pass
       except Exception as e:
           logger.error(f"Calculation failed: {str(e)}")
           raise CalculationError("Variable calculation failed") from e
   ```

### 6. Testing Strategy

The project uses a multi-level testing approach:

1. **Unit Tests**
   - Test individual components
   - Mock external dependencies
   - Fast execution

2. **Integration Tests**
   - Test component interactions
   - Use test database
   - Slower execution

3. **End-to-End Tests**
   - Test complete workflows
   - Use production-like environment
   - Slowest execution

### 7. Performance Optimization

The project implements several performance optimizations:

1. **Database Indexing**
   ```sql
   -- Spatial indexes
   CREATE INDEX idx_adm_cd_geom ON adm_cd USING GIST (geom);
   CREATE INDEX idx_census_tract_geom ON census_tract USING GIST (geom);

   -- Attribute indexes
   CREATE INDEX idx_population_year ON population (year);
   CREATE INDEX idx_business_year ON business (year);
   ```

2. **Query Optimization**
   - Use materialized views for complex calculations
   - Implement query caching
   - Use batch processing for large datasets

3. **Memory Management**
   - Use generators for large datasets
   - Implement chunking for large calculations
   - Clean up resources properly

## Design Decisions

### 1. Modular Architecture

The project uses a modular architecture to:
- Allow easy addition of new variables
- Maintain separation of concerns
- Enable independent testing
- Support future extensions

### 2. Database-First Approach

The project prioritizes database operations because:
- Spatial data is best handled by PostGIS
- Complex calculations can be optimized
- Data consistency is maintained
- Scalability is improved

### 3. Configuration Management

The project uses a hierarchical configuration system to:
- Support different environments
- Enable easy customization
- Maintain security
- Follow best practices

### 4. Error Handling

The project implements comprehensive error handling to:
- Provide clear error messages
- Enable debugging
- Maintain data integrity
- Support recovery

## Future Considerations

1. **Scalability**
   - Implement distributed processing
   - Add caching layer
   - Optimize database queries
   - Support cloud deployment

2. **Extensibility**
   - Add plugin system
   - Support custom calculators
   - Enable custom data sources
   - Add API endpoints

3. **Performance**
   - Implement parallel processing
   - Add result caching
   - Optimize memory usage
   - Improve query performance

4. **Monitoring**
   - Add performance metrics
   - Implement logging
   - Add health checks
   - Enable alerts

## Next Steps

1. Review the [Contributing Guide](contributing.md)
2. Check [Code Style Guide](code-style.md)
3. Review [API Reference](../api/point-based-calculations.md)
