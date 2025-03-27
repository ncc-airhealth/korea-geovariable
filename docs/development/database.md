# Database Guide

This guide explains database setup, management, and best practices for the Korea Geovariable project.

## Database Overview

The project uses PostgreSQL with PostGIS extension for spatial data storage and analysis.

### 1. Requirements

- PostgreSQL 14 or later
- PostGIS 3.2 or later
- Python 3.11 or later
- SQLAlchemy 2.0 or later

### 2. Installation

```bash
# Install PostgreSQL
brew install postgresql@14

# Install PostGIS
brew install postgis

# Start PostgreSQL service
brew services start postgresql@14
```

## Database Setup

### 1. Create Database

```sql
-- Create database
CREATE DATABASE korea_geovariable;

-- Enable PostGIS extension
\c korea_geovariable
CREATE EXTENSION postgis;
```

### 2. Create Schema

```sql
-- Create schema
CREATE SCHEMA IF NOT EXISTS public;

-- Set search path
SET search_path TO public;
```

### 3. Create Tables

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
    geom geometry(MultiPolygon, 5179),
    FOREIGN KEY (tot_reg_cd) REFERENCES adm_cd(tot_reg_cd)
);

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

-- Population data
CREATE TABLE population (
    tot_reg_cd VARCHAR(10),
    year INTEGER,
    population INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tot_reg_cd) REFERENCES adm_cd(tot_reg_cd)
);

-- Business data
CREATE TABLE business (
    tot_reg_cd VARCHAR(10),
    year INTEGER,
    count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tot_reg_cd) REFERENCES adm_cd(tot_reg_cd)
);
```

### 4. Create Indexes

```sql
-- Spatial indexes
CREATE INDEX idx_adm_cd_geom ON adm_cd USING GIST (geom);
CREATE INDEX idx_census_tract_geom ON census_tract USING GIST (geom);
CREATE INDEX idx_poi_geom ON poi USING GIST (geom);
CREATE INDEX idx_road_geom ON road USING GIST (geom);

-- Attribute indexes
CREATE INDEX idx_population_year ON population (year);
CREATE INDEX idx_business_year ON business (year);
```

## Database Management

### 1. Connection Management

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create engine
engine = create_engine(
    "postgresql://user:password@localhost:5432/korea_geovariable",
    pool_size=5,
    max_overflow=10
)

# Create session factory
Session = sessionmaker(bind=engine)

# Use session
with Session() as session:
    # Database operations
    pass
```

### 2. Query Optimization

```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:password@localhost:5432/korea_geovariable",
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)

# Use materialized views for complex queries
CREATE MATERIALIZED VIEW population_stats AS
SELECT
    tot_reg_cd,
    year,
    AVG(population) as avg_population,
    MAX(population) as max_population
FROM population
GROUP BY tot_reg_cd, year;

# Refresh materialized view
REFRESH MATERIALIZED VIEW population_stats;
```

### 3. Data Migration

```python
# Create migration script
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add new column
    op.add_column('population', sa.Column('density', sa.Float))

    # Update data
    op.execute("""
        UPDATE population
        SET density = population::float / ST_Area(geom)
    """)

def downgrade():
    # Remove column
    op.drop_column('population', 'density')
```

## Best Practices

### 1. Query Optimization

1. **Use Indexes**
   ```sql
   -- Create appropriate indexes
   CREATE INDEX idx_population_tot_reg_cd ON population (tot_reg_cd);
   CREATE INDEX idx_business_tot_reg_cd ON business (tot_reg_cd);
   ```

2. **Use Spatial Indexes**
   ```sql
   -- Create spatial indexes
   CREATE INDEX idx_poi_geom ON poi USING GIST (geom);
   CREATE INDEX idx_road_geom ON road USING GIST (geom);
   ```

3. **Optimize Queries**
   ```sql
   -- Use EXPLAIN ANALYZE
   EXPLAIN ANALYZE
   SELECT p.*, b.count
   FROM population p
   JOIN business b ON p.tot_reg_cd = b.tot_reg_cd
   WHERE p.year = 2020;
   ```

### 2. Data Integrity

1. **Use Constraints**
   ```sql
   -- Add constraints
   ALTER TABLE population
   ADD CONSTRAINT chk_population_positive
   CHECK (population >= 0);

   ALTER TABLE business
   ADD CONSTRAINT chk_business_positive
   CHECK (count >= 0);
   ```

2. **Use Foreign Keys**
   ```sql
   -- Add foreign keys
   ALTER TABLE census_tract
   ADD CONSTRAINT fk_census_tract_adm_cd
   FOREIGN KEY (tot_reg_cd)
   REFERENCES adm_cd(tot_reg_cd);
   ```

3. **Use Triggers**
   ```sql
   -- Create trigger for data validation
   CREATE OR REPLACE FUNCTION validate_population()
   RETURNS TRIGGER AS $$
   BEGIN
       IF NEW.population < 0 THEN
           RAISE EXCEPTION 'Population cannot be negative';
       END IF;
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER validate_population_trigger
   BEFORE INSERT OR UPDATE ON population
   FOR EACH ROW
   EXECUTE FUNCTION validate_population();
   ```

### 3. Backup and Recovery

1. **Regular Backups**
   ```bash
   # Create backup
   pg_dump -U postgres -d korea_geovariable > backup.sql

   # Restore backup
   psql -U postgres -d korea_geovariable < backup.sql
   ```

2. **Point-in-Time Recovery**
   ```bash
   # Enable WAL archiving
   archive_mode = on
   archive_command = 'cp %p /path/to/archive/%f'

   # Restore to point in time
   pg_restore -U postgres -d korea_geovariable -t population backup.dump
   ```

## Monitoring

### 1. Performance Monitoring

```sql
-- Check table sizes
SELECT
    relname as table_name,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### 2. Query Monitoring

```sql
-- Check slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check table statistics
SELECT
    schemaname,
    tablename,
    seq_scan,
    idx_scan
FROM pg_stat_user_tables
ORDER BY seq_scan DESC;
```

## Troubleshooting

### 1. Common Issues

1. **Connection Issues**
   ```bash
   # Check PostgreSQL status
   brew services list

   # Check logs
   tail -f /usr/local/var/log/postgresql@14.log
   ```

2. **Performance Issues**
   ```sql
   -- Check table bloat
   SELECT
       schemaname,
       tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
   ```

3. **Data Issues**
   ```sql
   -- Check for invalid geometries
   SELECT tot_reg_cd, name
   FROM adm_cd
   WHERE NOT ST_IsValid(geom);

   -- Check for missing data
   SELECT tot_reg_cd
   FROM adm_cd
   WHERE NOT EXISTS (
       SELECT 1
       FROM population
       WHERE population.tot_reg_cd = adm_cd.tot_reg_cd
   );
   ```

### 2. Maintenance

```sql
-- Vacuum tables
VACUUM ANALYZE population;
VACUUM ANALYZE business;

-- Reindex tables
REINDEX TABLE population;
REINDEX TABLE business;

-- Update statistics
ANALYZE population;
ANALYZE business;
```

## Next Steps

1. Review the [Contributing Guide](contributing.md)
2. Check [Code Style Guide](code-style.md)
3. Review [Architecture Guide](architecture.md)
