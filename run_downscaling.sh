#!/bin/bash

INPUT_DIR=/p/projects/climate_data_central/reanalysis/ERA5
MAX_CPUS=4
OUTPUT_ROOT=ERA5_0p5deg_hourly
OUTPUT_YEARLY=""   # defaults to ${OUTPUT_ROOT}_yearly
LAT_MIN=""
LAT_MAX=""
LON_MIN=""
LON_MAX=""

usage() {
    echo "Usage: $0 [-j max_cpus] [-o output_root] [-O output_yearly_root]"
    echo "          [--lat-min V] [--lat-max V] [--lon-min V] [--lon-max V]"
    echo ""
    echo "  -j  Maximum parallel interpolation jobs (default: $MAX_CPUS)"
    echo "  -o  Output root for interpolated monthly files (default: $OUTPUT_ROOT)"
    echo "  -O  Output root for yearly concatenated files (default: <output_root>_yearly)"
    echo ""
    echo "  Lat-lon mask box (all four required if any is given):"
    echo "  --lat-min  Southern boundary"
    echo "  --lat-max  Northern boundary"
    echo "  --lon-min  Western boundary"
    echo "  --lon-max  Eastern boundary"
    echo "  Grid points outside the box are set to NaN; full grid dimensions are kept."
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -j) MAX_CPUS="$2"; shift 2 ;;
        -o) OUTPUT_ROOT="$2"; shift 2 ;;
        -O) OUTPUT_YEARLY="$2"; shift 2 ;;
        --lat-min) LAT_MIN="$2"; shift 2 ;;
        --lat-max) LAT_MAX="$2"; shift 2 ;;
        --lon-min) LON_MIN="$2"; shift 2 ;;
        --lon-max) LON_MAX="$2"; shift 2 ;;
        *) usage ;;
    esac
done

[[ -z "$OUTPUT_YEARLY" ]] && OUTPUT_YEARLY="${OUTPUT_ROOT}_yearly"

# Validate lat-lon box: either all four bounds or none.
bbox_count=0
[[ -n "$LAT_MIN" ]] && (( bbox_count++ ))
[[ -n "$LAT_MAX" ]] && (( bbox_count++ ))
[[ -n "$LON_MIN" ]] && (( bbox_count++ ))
[[ -n "$LON_MAX" ]] && (( bbox_count++ ))

if (( bbox_count > 0 && bbox_count < 4 )); then
    echo "Error: --lat-min, --lat-max, --lon-min, --lon-max must all be given or none."
    exit 1
fi

bbox_args=()
if (( bbox_count == 4 )); then
    bbox_args=(--lat-min "$LAT_MIN" --lat-max "$LAT_MAX" --lon-min "$LON_MIN" --lon-max "$LON_MAX")
fi

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

# ---------------------------------------------------------------------------
# Phase 1: Interpolation (parallel)
# ---------------------------------------------------------------------------
echo "Phase 1: Interpolating to 0.5-degree grid (up to $MAX_CPUS parallel jobs)..."

active_jobs=0
for year in $(seq $beg_year $end_year); do
    for variable in "${variables[@]}"; do
        ./main_interpolation.sh -o "$OUTPUT_ROOT" -v "$variable" -i "$INPUT_DIR" -r hourly -y "$year" &
        (( active_jobs++ ))
        if (( active_jobs >= MAX_CPUS )); then
            wait -n 2>/dev/null || wait
            (( active_jobs-- ))
        fi
    done
done
wait
echo "Phase 1 complete."

# ---------------------------------------------------------------------------
# Phase 2: Yearly concatenation (sequential — runs after all interpolation done)
# ---------------------------------------------------------------------------
echo "Phase 2: Concatenating to yearly files in $OUTPUT_YEARLY ..."

for variable in "${variables[@]}"; do
    for year in $(seq $beg_year $end_year); do
        python3 src/concat_yearly.py \
            --input-dir  "$OUTPUT_ROOT" \
            --variable   "$variable" \
            --year       "$year" \
            --output-dir "$OUTPUT_YEARLY" \
            "${bbox_args[@]}"
    done
done

echo "All done. Yearly files written to: $OUTPUT_YEARLY"
