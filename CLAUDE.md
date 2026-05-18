# ERA5 forcing data for POEM LPJmL

## Environment
The conda environment please use the miniconda3 that lives in `$HOME/miniconda3` with the environment `rainbow`. Do not proceed if you cannot find this environment

## Character
You are a very disciplined programmer, so you will keep the code flexible, easy to read, and reusable.

## Project Overview
This project provides tools to interpolate ERA5 climate reanalysis data to a 0.5-degree latitude/longitude grid and aggregate it to various temporal resolutions (hourly, daily, or monthly).

## Core Mandates -- strictly enforced

1. **File Permission**: Only allow writting or modifying files in this workspace (same folder where this `CLAUDE.md` lives.
2. **Data Source**: The original ERA5 data is located at `/p/projects/climate_data_central/reanalysis/ERA5/`.
3. **Interpolation**: Data must be interpolated to a 0.5-degree lat/lon grid.
4. **Temporal Resolution**: Users must be able to choose between hourly, daily, or monthly temporal aggregation.
5. **Output Structure**: The output directory structure must mimic the original ERA5 data structure within a user-specified root folder.
6. **Implementation**: 
    - Use Python 3 for the core interpolation logic.
    - Required Python packages: `xarray`, `argparse`, and `netCDF4` (implied for xarray).
    - Use `argparse` for handling command-line arguments in Python.
    - Python scripts must be executed via customizable bash scripts.
7. **GIT**: Do not commit without permission.

## Conventions
- Python code should follow PEP 8 standards.
- Bash scripts should be well-documented and include error handling.
- Maintain consistency with the original ERA5 file naming and directory conventions in the output.

## Files and descriptions

All Python scripts live under `src/`. Bash scripts live in the project root and are the intended entry points.

### Bash scripts (project root)
- `run_downscaling.sh`: Top-level orchestrator — runs interpolation in parallel (Phase 1), then yearly concatenation (Phase 2). Supports `-j`, `-o`, `-O`, and optional `--lat-min/max`, `--lon-min/max` bbox mask.
- `main_interpolation.sh`: Processes one variable+year — loops over monthly source files and calls `src/interpolate_era5.py` for each.
- `activate_env.sh`: Activates the conda environment before running any scripts.

### Python scripts (`src/`)
- `src/interpolate_era5.py`: Interpolates a single ERA5 NetCDF file to the 0.5-degree grid and resamples to the target temporal resolution.
- `src/concat_yearly.py`: Concatenates monthly interpolated files into a single yearly file (`[variable]_[YYYY].nc`). Validates the hourly time axis and optionally masks outside a lat-lon box with NaN (full grid preserved, compressed output).
- `src/download_era5_daily.py`: Downloads ERA5 daily statistics from CDS for selected variables and year range. Skips files that already exist. Output structure: `<output_root>/<variable>/<variable>_<year>.nc`.
- `src/download_example.py`: Example script demonstrating CDS download usage.

