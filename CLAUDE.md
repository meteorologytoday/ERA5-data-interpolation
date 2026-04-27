# ERA5 forcing data for POEM LPJmL

## Environment
The conda environment please use the miniconda3 that lives in `$HOME/miniconda3` with the environment `gemini_env`. Do not proceed if you cannot find this environment

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

- `interpolate_era5.py`: The main engine that interpolates ERA5 climate data
- `run_interpolation.sh`: The script that user can run like a command to execute interpolation.
- `activate_env.sh`: Sources this file to activate the `gemini_env` conda environment before running any scripts.
- `download_era5_daily.py`: Downloads ERA5 daily statistics from CDS for selected variables and year range. Skips files that already exist. Output structure: `<output_root>/<variable>/<variable>_<year>.nc`.

