#!/bin/bash

# This script imports vector SHP files from a specified directory into PostGIS tables.
# Usage: ./vector_to_postgis.sh [optional: path_to_data_directory]

# Load environment variables
source .env

# assume the data is in the storage/publichealth directory
shp2pgsql -D -s 5179 storage/publichealth/hospitals.shp hospitals | psql ${DB_URL}
shp2pgsql -D -s 5179 storage/publichealth/clinics.shp clinics | psql ${DB_URL}