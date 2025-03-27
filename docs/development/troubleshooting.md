# Troubleshooting Guide

This guide explains common issues and their solutions for the Korea Geovariable project.

## Common Issues

### 1. Installation Issues

#### Python Version Mismatch
```bash
# Check Python version
python --version

# Install correct version
brew install python@3.11

# Update PATH
echo 'export PATH="/usr/local/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### Dependency Installation Failures
```bash
# Clear pip cache
pip cache purge

# Update pip
python -m pip install --upgrade pip

# Install dependencies with verbose output
uv sync -v
```

#### PostGIS Installation Issues
```bash
# Check PostgreSQL version
psql --version

# Check PostGIS installation
psql -d korea_geovariable -c "SELECT PostGIS_Version();"

# Reinstall PostGIS
brew uninstall postgis
brew install postgis
```

### 2. Database Issues

#### Connection Errors
```python
# Check database connection
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.scalar())
```

#### Permission Issues
```sql
-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE korea_geovariable TO user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO user;
```

#### Spatial Index Issues
```sql
-- Check spatial indexes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE indexdef LIKE '%USING gist%';

-- Rebuild spatial indexes
REINDEX INDEX idx_adm_cd_geom;
REINDEX INDEX idx_census_tract_geom;
```

### 3. Application Issues

#### Memory Errors
```python
# Check memory usage
import psutil
process = psutil.Process()
print(process.memory_info().rss / 1024 / 1024)  # MB

# Optimize memory usage
import gc
gc.collect()  # Force garbage collection
```

#### Performance Issues
```python
# Profile code
import cProfile
import pstats

def profile_function(func):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func()
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
    return result
```

#### API Errors
```python
# Check API responses
import requests

def check_api_endpoint(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
```

## Debugging Tools

### 1. Logging

```python
# Configure logging
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Use logging
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### 2. Debugger

```python
# Use pdb
import pdb

def complex_function():
    # Set breakpoint
    pdb.set_trace()

    # Code to debug
    result = calculate_something()

    return result

# Common pdb commands
# n: next line
# s: step into
# c: continue
# p variable: print variable
# l: list code
# q: quit
```

### 3. Profiling

```python
# Use line_profiler
from line_profiler import LineProfiler

profiler = LineProfiler()

@profiler
def slow_function():
    # Code to profile
    pass

# Run profiled function
slow_function()

# Print results
profiler.print_stats()
```

## System Monitoring

### 1. Resource Usage

```bash
# Monitor CPU usage
top

# Monitor memory usage
free -h

# Monitor disk usage
df -h

# Monitor network usage
iftop
```

### 2. Process Monitoring

```bash
# List running processes
ps aux | grep python

# Monitor specific process
pidstat -p <PID> 1

# Check process limits
ulimit -a
```

### 3. Database Monitoring

```sql
-- Check active connections
SELECT * FROM pg_stat_activity;

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

## Error Handling

### 1. Custom Exceptions

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

# Use custom exceptions
def calculate_variable():
    try:
        # Calculation logic
        pass
    except Exception as e:
        logger.error(f"Calculation failed: {str(e)}")
        raise CalculationError("Variable calculation failed") from e
```

### 2. Error Recovery

```python
def retry_operation(func, max_retries=3):
    """Retry operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s.")
            time.sleep(wait_time)
```

## Performance Optimization

### 1. Query Optimization

```sql
-- Use EXPLAIN ANALYZE
EXPLAIN ANALYZE
SELECT p.*, b.count
FROM population p
JOIN business b ON p.tot_reg_cd = b.tot_reg_cd
WHERE p.year = 2020;

-- Create materialized views
CREATE MATERIALIZED VIEW population_stats AS
SELECT
    tot_reg_cd,
    year,
    AVG(population) as avg_population
FROM population
GROUP BY tot_reg_cd, year;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW population_stats;
```

### 2. Memory Optimization

```python
# Use generators
def process_large_dataset():
    for item in large_dataset:
        yield process_item(item)

# Use chunking
def process_in_chunks(data, chunk_size=1000):
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        process_chunk(chunk)

# Use context managers
from contextlib import contextmanager

@contextmanager
def database_connection():
    conn = create_connection()
    try:
        yield conn
    finally:
        conn.close()
```

## Security Issues

### 1. Authentication

```python
# Check authentication
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user = verify_token(token)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
```

### 2. Data Validation

```python
# Validate input data
from pydantic import BaseModel, validator

class PopulationData(BaseModel):
    tot_reg_cd: str
    year: int
    population: int

    @validator('population')
    def validate_population(cls, v):
        if v < 0:
            raise ValueError('Population cannot be negative')
        return v

    @validator('year')
    def validate_year(cls, v):
        if v < 2015 or v > 2020:
            raise ValueError('Year must be between 2015 and 2020')
        return v
```

## Next Steps

1. Review the [Contributing Guide](contributing.md)
2. Check [Code Style Guide](code-style.md)
3. Review [Architecture Guide](architecture.md)
