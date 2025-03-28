#!/bin/bash

# This script imports raster TIF files from emission directories into a single partitioned PostGIS table
# Usage: ./raster_to_postgis.sh [optional: path_to_data_directory]

# Load environment variables
source .env

# Set default data directory or use command line argument if provided
DATA_DIR=${1:-"/Users/dongookson/Downloads/emission"}
TABLE_NAME="emission_raster"
# Set a timeout for database operations (in seconds)
TIMEOUT=5

# Check if DB_URL is set in the .env file
if [ -z "${DB_URL}" ]; then
    echo "ERROR: DB_URL is not set in .env file"
    echo "Please set DB_URL in the .env file with format: 'postgresql://username:password@localhost:5432/dbname'"
    exit 1
fi

# Verify DATA_DIR exists
if [ ! -d "${DATA_DIR}" ]; then
    echo "ERROR: Directory ${DATA_DIR} does not exist"
    exit 1
fi

# Test database connection before proceeding
echo "Testing database connection..."
if ! timeout $TIMEOUT psql "${DB_URL}" -c "SELECT 1;" > /dev/null 2>&1; then
    echo "ERROR: Could not connect to the database using URL: ${DB_URL}"
    echo "Please check that:"
    echo "  1. Your database server is running"
    echo "  2. The DB_URL in .env is correct"
    echo "  3. Network connectivity to the database server is available"
    echo "  4. Authentication credentials are correct"
    echo ""
    echo "DB_URL format should be: postgresql://username:password@hostname:port/dbname"
    exit 1
else
    echo "Database connection successful."
fi

echo "Starting import of raster files from ${DATA_DIR} to PostGIS database..."

# Function to safely run PostgreSQL commands with timeout
safe_psql() {
    local query=$1
    local error_msg=${2:-"Database operation failed"}

    if ! timeout $TIMEOUT psql "${DB_URL}" -c "$query"; then
        echo "ERROR: $error_msg"
        echo "Query: $query"
        return 1
    fi
    return 0
}

# Create master partitioned table if it doesn't exist
create_master_table() {
    echo "Checking if master table $TABLE_NAME exists..."

    # Check if table exists with timeout
    if ! table_exists=$(timeout $TIMEOUT psql "${DB_URL}" -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '${TABLE_NAME}');" 2>/dev/null); then
        echo "ERROR: Timeout checking if table exists. Database connection might be slow or not working properly."
        exit 1
    fi

    if ! echo "$table_exists" | grep -q t; then
        echo "Creating master partitioned table: $TABLE_NAME"

        # Create the parent partitioned table with metadata columns - partition by year first
        if ! safe_psql "
        CREATE TABLE public.${TABLE_NAME} (
            rid SERIAL,
            rast raster,
            filename TEXT,
            year INTEGER,
            emission_type TEXT,
            pollutant_type TEXT
        ) PARTITION BY LIST (year);" "Failed to create master table"; then
            exit 1
        fi

        echo "Master table created successfully."
    else
        echo "Master table $TABLE_NAME already exists."
    fi
}

# Create year partition if it doesn't exist
create_year_partition() {
    local year=$1

    # Year partition name
    local year_partition="${TABLE_NAME}_${year}"

    # Check if year partition exists
    if ! partition_exists=$(timeout $TIMEOUT psql "${DB_URL}" -t -c "SELECT EXISTS (SELECT FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = '${year_partition}' AND n.nspname = 'public');" 2>/dev/null); then
        echo "ERROR: Timeout checking if year partition exists."
        return 1
    fi

    if ! echo "$partition_exists" | grep -q t; then
        echo "Creating year partition: $year_partition"

        # Create the year partition
        if ! safe_psql "
        CREATE TABLE public.${year_partition}
        PARTITION OF public.${TABLE_NAME}
        FOR VALUES IN (${year})
        PARTITION BY LIST (emission_type);" "Failed to create year partition"; then
            return 1
        fi

        echo "Year partition created successfully."
    else
        echo "Year partition $year_partition already exists."
    fi
    return 0
}

# Create emission type partition
create_type_partition() {
    local year=$1
    local emission_type=$2

    # Type partition name
    local year_partition="${TABLE_NAME}_${year}"
    local type_partition="${year_partition}_${emission_type}"

    # Check if type partition exists
    if ! partition_exists=$(timeout $TIMEOUT psql "${DB_URL}" -t -c "SELECT EXISTS (SELECT FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = '${type_partition}' AND n.nspname = 'public');" 2>/dev/null); then
        echo "ERROR: Timeout checking if type partition exists."
        return 1
    fi

    if ! echo "$partition_exists" | grep -q t; then
        echo "Creating type partition: $type_partition"

        # Create the type partition
        if ! safe_psql "
        CREATE TABLE public.${type_partition}
        PARTITION OF public.${year_partition}
        FOR VALUES IN ('${emission_type}')
        PARTITION BY LIST (pollutant_type);" "Failed to create type partition"; then
            return 1
        fi

        echo "Type partition created successfully."
    else
        echo "Type partition $type_partition already exists."
    fi
    return 0
}

# Create pollutant partition
create_pollutant_partition() {
    local year=$1
    local emission_type=$2
    local pollutant_type=$3

    # Pollutant partition name - this is the final leaf partition
    local year_partition="${TABLE_NAME}_${year}"
    local type_partition="${year_partition}_${emission_type}"
    local pollutant_partition="${type_partition}_${pollutant_type}"

    # Check if pollutant partition exists
    if ! partition_exists=$(timeout $TIMEOUT psql "${DB_URL}" -t -c "SELECT EXISTS (SELECT FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = '${pollutant_partition}' AND n.nspname = 'public');" 2>/dev/null); then
        echo "ERROR: Timeout checking if pollutant partition exists."
        return 1
    fi

    if ! echo "$partition_exists" | grep -q t; then
        echo "Creating pollutant partition: $pollutant_partition"

        # Create the pollutant partition
        if ! safe_psql "
        CREATE TABLE public.${pollutant_partition}
        PARTITION OF public.${type_partition}
        FOR VALUES IN ('${pollutant_type}');" "Failed to create pollutant partition"; then
            return 1
        fi

        echo "Pollutant partition created successfully."
    else
        echo "Pollutant partition $pollutant_partition already exists."
    fi
    return 0
}

# Create partition for a specific combination of year, emission type, and pollutant type
create_partition() {
    local year=$1
    local emission_type=$2
    local pollutant_type=$3

    # Create hierarchical partitions
    create_year_partition "$year"
    create_type_partition "$year" "$emission_type"
    create_pollutant_partition "$year" "$emission_type" "$pollutant_type"
}

# Function to import a raster file into the appropriate partition
import_raster() {
    local filepath=$1
    local year=$2
    local filename=$(basename "$filepath")

    echo "Analyzing filename: $filename"

    # Extract emission type (p=point, l=line, a=area) from filename
    local emission_type=""
    if [[ $filename =~ emission\.([pla])\. ]]; then
        case "${BASH_REMATCH[1]}" in
            "p") emission_type="point" ;;
            "l") emission_type="line" ;;
            "a") emission_type="area" ;;
        esac
        echo "  Detected emission type: $emission_type from pattern match: ${BASH_REMATCH[0]}"
    else
        echo "WARNING: Could not determine emission type for $filename"
        echo "  Filename doesn't match the expected pattern 'emission.[p|l|a].*'"
        emission_type="unknown"
    fi

    # Extract pollutant type from filename (e.g., co, nh3, pm10)
    local pollutant_type=""

    # Try multiple regex patterns to extract pollutant type

    # Pattern 1: emission.p.co.tif or emission.a.nh3.tif - simple case with no year
    if [[ $filename =~ emission\.[pla]\.([a-zA-Z0-9_]+)\.tif$ ]]; then
        pollutant_type="${BASH_REMATCH[1]}"
        echo "  Detected pollutant type (pattern 1): $pollutant_type from match: ${BASH_REMATCH[0]}"

    # Pattern 2: emission.p.2001_co.tif - year prefix in pollutant
    elif [[ $filename =~ emission\.[pla]\.([0-9]{4})_([a-zA-Z0-9_]+)\.tif$ ]]; then
        pollutant_type="${BASH_REMATCH[2]}"  # Use capture group 2 (the part after year_)
        echo "  Detected pollutant type (pattern 2): $pollutant_type from match: ${BASH_REMATCH[0]}"
        echo "  (Removed year prefix ${BASH_REMATCH[1]} from pollutant)"

    # Pattern 3: emission.p.2001_co_extra.tif - year prefix with extra parts
    elif [[ $filename =~ emission\.[pla]\.([0-9]{4})_([a-zA-Z0-9_]+)_ ]]; then
        pollutant_type="${BASH_REMATCH[2]}"  # Use capture group 2 (the part after year_)
        echo "  Detected pollutant type (pattern 3): $pollutant_type from match: ${BASH_REMATCH[0]}"
        echo "  (Removed year prefix ${BASH_REMATCH[1]} from pollutant)"

    # Pattern 4: emission.p.co.other.tif - any other format
    elif [[ $filename =~ emission\.[pla]\.([a-zA-Z0-9_]+)\. ]]; then
        pollutant_type="${BASH_REMATCH[1]}"

        # Check if pollutant has a year prefix (like 2001_voc)
        if [[ $pollutant_type =~ ^([0-9]{4})_(.+)$ ]]; then
            pollutant_type="${BASH_REMATCH[2]}"  # Extract just the part after year_
            echo "  Detected pollutant type (pattern 4): $pollutant_type from match: ${BASH_REMATCH[0]}"
            echo "  (Removed year prefix ${BASH_REMATCH[1]} from pollutant)"
        else
            echo "  Detected pollutant type (pattern 4): $pollutant_type from match: ${BASH_REMATCH[0]}"
        fi

    else
        echo "WARNING: Could not determine pollutant type for $filename"
        echo "  Filename format not recognized. Please check the filenames."
        # Display all parts of the filename for debugging
        IFS='.' read -ra PARTS <<< "$filename"
        echo "  Filename parts: ${PARTS[@]}"
        pollutant_type="unknown"
    fi

    # Final cleanup - ensure the pollutant type doesn't contain year prefix
    if [[ $pollutant_type =~ ^[0-9]{4}_(.+)$ ]]; then
        echo "  Removing year prefix from pollutant type"
        pollutant_type="${BASH_REMATCH[1]}"
    fi

    echo "Processing: Year=$year, Type=$emission_type, Pollutant=$pollutant_type, File=$filename"

    # Create partition for this combination if it doesn't exist
    if ! create_partition "$year" "$emission_type" "$pollutant_type"; then
        echo "ERROR: Failed to create partitions for $filename"
        return 1
    fi

    # Final leaf partition name
    local year_partition="${TABLE_NAME}_${year}"
    local type_partition="${year_partition}_${emission_type}"
    local pollutant_partition="${type_partition}_${pollutant_type}"

    # Clear existing data in the partition
    echo "Clearing existing data in partition $pollutant_partition..."
    if ! safe_psql "DELETE FROM public.${pollutant_partition} WHERE filename='${filename}';" "Failed to clear existing data"; then
        echo "WARNING: Could not clear existing data. Continuing anyway..."
    fi

    # Import raster data into the partition
    echo "Importing data into partition: $pollutant_partition"

    # Create a temporary table for the import with a unique name
    local temp_table="temp_import_${RANDOM}_${RANDOM}"
    echo "Creating temporary table: $temp_table"

    # Use timeout with raster2pgsql
    echo "Running raster2pgsql..."
    raster2pgsql_output=$(mktemp)
    if ! timeout $((TIMEOUT*2)) raster2pgsql -F -I -C -c -s 5179 -t 100x100 "$filepath" "public.${temp_table}" > "$raster2pgsql_output"; then
        echo "ERROR: raster2pgsql timed out or failed"
        rm -f "$raster2pgsql_output"
        return 1
    fi

    # Import to database with timeout
    echo "Importing raster to temporary table..."
    if ! timeout $((TIMEOUT*3)) psql "${DB_URL}" < "$raster2pgsql_output"; then
        echo "ERROR: Failed to import raster to temporary table"
        rm -f "$raster2pgsql_output"
        return 1
    fi
    rm -f "$raster2pgsql_output"

    # Insert from temp table into the partition with metadata
    echo "Copying data from temporary table to partition..."
    if ! safe_psql "
    INSERT INTO public.${TABLE_NAME} (rast, filename, year, emission_type, pollutant_type)
    SELECT rast, '${filename}', ${year}, '${emission_type}', '${pollutant_type}'
    FROM public.${temp_table};" "Failed to copy data from temporary table"; then
        echo "ERROR: Failed to copy data from temporary table"
        # Try to clean up
        safe_psql "DROP TABLE IF EXISTS public.${temp_table};" "Failed to drop temporary table"
        return 1
    fi

    # Drop the temporary table
    echo "Dropping temporary table..."
    if ! safe_psql "DROP TABLE IF EXISTS public.${temp_table};" "Failed to drop temporary table"; then
        echo "WARNING: Failed to drop temporary table ${temp_table}"
    fi

    echo "Successfully imported $filename to partition $pollutant_partition"
    return 0
}

# Create the master partitioned table
create_master_table || exit 1

# Loop over directories matching the pattern "YYYY_emission"
echo "Scanning for emission directories..."
count=0
error_count=0

for dir in "${DATA_DIR}"/*_emission/; do
    # Check if it is a directory.
    if [[ -d $dir ]]; then
        # Extract the directory name and then the year (substring before the underscore)
        dirname=$(basename "$dir")
        year=${dirname%%_*}  # e.g. "2001_emission" becomes "2001"
        # Optionally, validate that $year is numeric.
        if [[ $year =~ ^[0-9]{4}$ ]]; then
            echo "Importing files from year $year in directory $dirname"
            # Loop over all TIFF files in the directory.
            file_count=0
            dir_error_count=0
            for file in "$dir"/*.tif; do
                # Skip if no files match.
                [[ -e $file ]] || continue
                echo "Importing file $file..."
                if import_raster "$file" "$year"; then
                    ((file_count++))
                else
                    echo "ERROR: Failed to import $file"
                    ((dir_error_count++))
                    ((error_count++))
                fi
            done
            echo "Processed $file_count files in $dirname (with $dir_error_count errors)"
            ((count++))
        else
            echo "Skipping directory $dirname (year not recognized)"
        fi
    fi
done

# Add spatial indexes to improve query performance
echo "Creating spatial indexes on the raster column..."
if ! safe_psql "SELECT AddRasterConstraints('public', '${TABLE_NAME}', 'rast');" "Failed to add raster constraints"; then
    echo "WARNING: Failed to add raster constraints. This might affect query performance."
fi

echo "Import process completed. Processed $count emission directories with $error_count errors."
echo "All data is now available in the partitioned table: public.${TABLE_NAME}"
echo "You can query data using SQL like:"
echo "  SELECT * FROM public.${TABLE_NAME} WHERE year=2020 AND emission_type='point' AND pollutant_type='co';"
echo ""
echo "If you're seeing 'unknown' pollutant types, check your filename format."
echo "Expected filename format: emission.[p|l|a].[pollutant].tif"
echo "Examples: emission.p.co.tif, emission.a.nh3.tif, emission.l.pm10.tif"
