#!/bin/bash

default_input_dir=/p/projects/climate_data_central/reanalysis/ERA5
MAX_CPUS=1

usage() {
    echo "Usage: $0 [-j max_cpus]"
    echo "  -j  Maximum number of parallel jobs (default: $MAX_CPUS)"
    exit 1
}

while getopts "j:" opt; do
    case $opt in
        j) MAX_CPUS="$OPTARG" ;;
        *) usage ;;
    esac
done

variables=(
    2m_temperature
    huss
    total_precipitation
    ps
    10m_u_component_of_wind
    10m_v_component_of_wind
    surface_solar_radiation_downwards
    surface_thermal_radiation_downwards
)

beg_year=1941
end_year=$(( beg_year + 30 - 1 ))

trap 'echo "Interrupted. Killing all child processes..."; kill 0; exit 1' INT TERM

echo "Running with up to $MAX_CPUS parallel jobs."

active_jobs=0

for year in $( seq $beg_year $end_year ); do
    for variable in "${variables[@]}"; do
        ./main_interpolation.sh -o ERA5_0p5deg_hourly -v "$variable" -i "$default_input_dir" -r hourly -y "$year" &
        (( active_jobs++ ))
        if (( active_jobs >= MAX_CPUS )); then
            wait -n 2>/dev/null || wait
            (( active_jobs-- ))
        fi
    done
done

wait
echo "All tasks completed."
