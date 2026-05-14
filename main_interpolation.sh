#!/bin/bash

# Default values
INPUT_ROOT="/p/projects/climate_data_central/reanalysis/ERA5"
OUTPUT_ROOT=""
VARIABLE=""
TEMPORAL_RES="hourly"
YEAR=""

# Function to show usage
usage() {
    echo "Usage: $0 -o <output_root> -v <variable> [-r <resolution>] [-y <year>] [-i <input_root>]"
    echo "  -o  Output root folder (required)"
    echo "  -v  ERA5 variable name (e.g., 2m_temperature) (required)"
    echo "  -r  Temporal resolution: hourly, daily, monthly (default: hourly)"
    echo "  -y  Filter by year (optional)"
    echo "  -i  Input root folder (default: $INPUT_ROOT)"
    exit 1
}

# Parse arguments
while getopts "o:v:r:y:i:" opt; do
    case $opt in
        o) OUTPUT_ROOT="$OPTARG" ;;
        v) VARIABLE="$OPTARG" ;;
        r) TEMPORAL_RES="$OPTARG" ;;
        y) YEAR="$OPTARG" ;;
        i) INPUT_ROOT="$OPTARG" ;;
        *) usage ;;
    esac
done

# Check required arguments
if [[ -z "$OUTPUT_ROOT" || -z "$VARIABLE" ]]; then
    usage
fi

# Input directory for the specific variable
INPUT_DIR="${INPUT_ROOT}/${VARIABLE}"

if [[ ! -d "$INPUT_DIR" ]]; then
    echo "Error: Input directory $INPUT_DIR does not exist."
    exit 1
fi

# Loop through files in the input directory
for input_file in "${INPUT_DIR}"/*.nc; do
    filename=$(basename "$input_file")
    
    # Filter by year if specified
    if [[ -n "$YEAR" ]]; then
        if [[ ! "$filename" =~ $YEAR ]]; then
            continue
        fi
    fi
    
    # Define output file path (mimicking original structure)
    output_file="${OUTPUT_ROOT}/${VARIABLE}/${filename}"
   
    if [ -f "$output_file" ]; then
        echo "The file already exists. Skip: $filename"
    else
        echo "Processing $filename ..."
        python3 interpolate_era5.py "$input_file" "$output_file" --res "$TEMPORAL_RES"
    fi
done

echo "All tasks completed."
