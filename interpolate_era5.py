import argparse
import os
import sys
import numpy as np
import xarray as xr


def interpolate_and_resample(input_file, output_file, temporal_res, compress_level=4):
    """
    Interpolates ERA5 data to 0.5 degree grid and resamples to desired temporal resolution.
    """
    try:
        # Load dataset
        ds = xr.open_dataset(input_file)

        # Identify coordinate names
        lat_name = 'latitude' if 'latitude' in ds.coords else 'lat'
        lon_name = 'longitude' if 'longitude' in ds.coords else 'lon'
        time_name = 'valid_time' if 'valid_time' in ds.coords else ('time' if 'time' in ds.coords else None)

        if time_name is None:
            # Check dimensions if not in coords
            time_name = 'valid_time' if 'valid_time' in ds.dims else ('time' if 'time' in ds.dims else None)

        if not time_name:
             raise ValueError(f"Could not find time dimension in {input_file}")

        # Define target grid: 0.5 degree

        target_lat = np.arange(90, -90.5, -0.5)
        target_lon = np.arange(0, 360, 0.5)

        # Interpolate
        interp_coords = {lat_name: target_lat, lon_name: target_lon}
        ds_interp = ds.interp(**interp_coords, method="linear")

        # Resample temporal resolution
        if temporal_res == 'daily':
            ds_resampled = ds_interp.resample({time_name: '1D'}).mean()
        elif temporal_res == 'monthly':
            ds_resampled = ds_interp.resample({time_name: '1MS'}).mean()
        elif temporal_res == 'hourly':
            ds_resampled = ds_interp
        else:
            raise ValueError(f"Unsupported temporal resolution: {temporal_res}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Save to netcdf with optional zlib compression
        encoding = {}
        if compress_level > 0:
            encoding = {var: {"zlib": True, "complevel": compress_level}
                        for var in ds_resampled.data_vars}
        ds_resampled.to_netcdf(output_file, encoding=encoding)
        print(f"Successfully processed {input_file} -> {output_file}")

    except Exception as e:
        print(f"Error processing {input_file}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Interpolate ERA5 data to 0.5 degree grid and aggregate temporally.")
    parser.add_argument("input_file", help="Path to the input ERA5 NetCDF file.")
    parser.add_argument("output_file", help="Path to the output NetCDF file.")
    parser.add_argument("--res", choices=['hourly', 'daily', 'monthly'], default='hourly',
                        help="Target temporal resolution (default: hourly).")
    parser.add_argument("--compress", type=int, default=4, metavar="LEVEL",
                        help="zlib compression level 0–9 (0 = off, default: 4).")

    args = parser.parse_args()

    interpolate_and_resample(args.input_file, args.output_file, args.res, args.compress)

if __name__ == "__main__":
    main()
