# Database Setup Guide

This guide explains how to set up the required database and tables for the Korea Geovariable project. Note that this setup guide is for system administrators only. If you are a user, please refer to the [Basic Usage](../usage/basic-usage.md) guide and request the database URL from the system administrators.

> **Note**: To obtain the database URL, please contact the system administrators:
>
> - [Han Jimin - 한지민](mailto:hangm0101@ncc.re.kr)
> - [Son Dongook - 손동욱](mailto:d@dou.so)


## Database Requirements

- PostgreSQL 12 or higher
- PostGIS extension
- Sufficient disk space for spatial data
- Appropriate user permissions

## Initial Setup

1. **Install PostgreSQL and PostGIS**
   ```bash
   # On macOS with Homebrew
   brew install postgresql postgis
   ```

2. **Start PostgreSQL Service**
   ```bash
   # On macOS
   brew services start postgresql
   ```

3. **Create Database**
   ```sql
   CREATE DATABASE korea_geovariable;
   ```

4. **Enable PostGIS Extension**
   ```sql
   \c korea_geovariable
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

## Required Tables

### 1. JGG Centroid Tables

#### jgg_centroid_adjusted
```sql
CREATE TABLE jgg_centroid_adjusted (
    tot_reg_cd VARCHAR(10) PRIMARY KEY,
    geom geometry(Point, 4326)
);

-- Create spatial index
CREATE INDEX idx_jgg_centroid_adjusted_geom
ON jgg_centroid_adjusted USING GIST (geom);
```

#### jgg_centroid_adjusted_buffered
```sql
CREATE TABLE jgg_centroid_adjusted_buffered (
    tot_reg_cd VARCHAR(10) PRIMARY KEY,
    geom_100 geometry(Polygon, 4326),
    geom_300 geometry(Polygon, 4326),
    geom_500 geometry(Polygon, 4326),
    geom_1000 geometry(Polygon, 4326),
    geom_5000 geometry(Polygon, 4326)
);

-- Create spatial indexes
CREATE INDEX idx_jgg_centroid_adjusted_buffered_geom_100
ON jgg_centroid_adjusted_buffered USING GIST (geom_100);
CREATE INDEX idx_jgg_centroid_adjusted_buffered_geom_300
ON jgg_centroid_adjusted_buffered USING GIST (geom_300);
CREATE INDEX idx_jgg_centroid_adjusted_buffered_geom_500
ON jgg_centroid_adjusted_buffered USING GIST (geom_500);
CREATE INDEX idx_jgg_centroid_adjusted_buffered_geom_1000
ON jgg_centroid_adjusted_buffered USING GIST (geom_1000);
CREATE INDEX idx_jgg_centroid_adjusted_buffered_geom_5000
ON jgg_centroid_adjusted_buffered USING GIST (geom_5000);
```

### 2. Intersection Areas Tables

For each buffer size (100, 300, 500, 1000, 5000), create a table:

```sql
CREATE TABLE intersection_areas_{buffer_size} (
    center_reg_cd VARCHAR(10),
    border_reg_cd VARCHAR(10),
    intersect_area double precision,
    border_area double precision,
    PRIMARY KEY (center_reg_cd, border_reg_cd)
);
```

### 3. Data Tables

The following tables are required for various calculations:

1. **Demographic Data**
   ```sql
   CREATE TABLE jgg_adjusted_sgis_pop (
       tot_reg_cd VARCHAR(10),
       year INTEGER,
       pop INTEGER,
       pop_m INTEGER,
       pop_f INTEGER,
       PRIMARY KEY (tot_reg_cd, year)
   );
   ```

2. **Business Data**
   ```sql
   CREATE TABLE jgg_adjusted_sgis_bnu (
       tot_reg_cd VARCHAR(10),
       year INTEGER,
       cp_bnu_001 INTEGER,
       -- ... other business type columns
       PRIMARY KEY (tot_reg_cd, year)
   );
   ```

3. **Land Use Data**
   ```sql
   CREATE TABLE landuse_v002_{year} (
       code INTEGER,
       geometry geometry(MultiPolygon, 4326)
   );
   ```

## Data Loading

### 1. Load JGG Centroid Data
```sql
-- Example using COPY command
COPY jgg_centroid_adjusted(tot_reg_cd, geom)
FROM '/path/to/centroid_data.csv'
WITH (FORMAT csv, HEADER true);
```

### 2. Create Buffer Zones
```sql
-- Example for 100m buffer
UPDATE jgg_centroid_adjusted_buffered
SET geom_100 = ST_Buffer(geom, 100)
FROM jgg_centroid_adjusted
WHERE jgg_centroid_adjusted_buffered.tot_reg_cd = jgg_centroid_adjusted.tot_reg_cd;
```

### 3. Calculate Intersection Areas
```sql
-- Example for 100m buffer
INSERT INTO intersection_areas_100 (center_reg_cd, border_reg_cd, intersect_area, border_area)
SELECT
    a.tot_reg_cd as center_reg_cd,
    b.tot_reg_cd as border_reg_cd,
    ST_Area(ST_Intersection(a.geom_100, b.geom_100)) as intersect_area,
    ST_Area(b.geom_100) as border_area
FROM jgg_centroid_adjusted_buffered a
CROSS JOIN jgg_centroid_adjusted_buffered b
WHERE ST_Intersects(a.geom_100, b.geom_100);
```

## Maintenance

### Regular Maintenance Tasks

1. **Vacuum and Analyze**
   ```sql
   VACUUM ANALYZE jgg_centroid_adjusted;
   VACUUM ANALYZE jgg_centroid_adjusted_buffered;
   ```

2. **Update Statistics**
   ```sql
   ANALYZE jgg_centroid_adjusted;
   ANALYZE jgg_centroid_adjusted_buffered;
   ```

3. **Check Indexes**
   ```sql
   REINDEX TABLE jgg_centroid_adjusted;
   REINDEX TABLE jgg_centroid_adjusted_buffered;
   ```

## Troubleshooting

### Common Issues

1. **Spatial Index Not Used**
   - Ensure PostGIS extension is enabled
   - Check if spatial indexes are created
   - Verify table statistics are up to date

2. **Performance Issues**
   - Check buffer sizes are appropriate
   - Verify spatial indexes are being used
   - Consider partitioning large tables

3. **Data Integrity**
   - Verify coordinate systems match (SRID 4326)
   - Check for invalid geometries
   - Validate intersection calculations

## Next Steps

After database setup:
1. Configure your [environment variables](configuration.md)
2. Start with [Basic Usage](../usage/basic-usage.md)
3. Explore [Available Calculators](../usage/calculators.md)
