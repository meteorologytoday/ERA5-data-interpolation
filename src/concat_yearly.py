import argparse
import glob
import os
import sys

import numpy as np
import pandas as pd
import xarray as xr


def validate_hourly_timestamps(ds, year):
    """
    Verify the merged dataset has a complete, gap-free hourly time axis for the given year.
    Exits with an error if any problem is found.
    """
    time_name = next(
        (n for n in ("valid_time", "time") if n in ds.coords or n in ds.dims),
        None,
    )
    if time_name is None:
        print("Error: cannot find time coordinate in merged dataset.", file=sys.stderr)
        sys.exit(1)

    times = pd.DatetimeIndex(ds[time_name].values)

    # Expected: every hour from Jan 1 00:00 through Dec 31 23:00
    expected = pd.date_range(
        start=f"{year}-01-01 00:00",
        end=f"{year}-12-31 23:00",
        freq="h",
        inclusive="both",
    )
    n_expected = len(expected)
    n_actual = len(times)

    ok = True

    if n_actual != n_expected:
        print(
            f"Timestamp check FAILED: expected {n_expected} hours, got {n_actual}.",
            file=sys.stderr,
        )
        ok = False

    duplicates = times[times.duplicated()]
    if len(duplicates) > 0:
        print(
            f"Timestamp check FAILED: {len(duplicates)} duplicate timestamp(s), "
            f"first: {duplicates[0]}.",
            file=sys.stderr,
        )
        ok = False

    missing = expected.difference(times)
    if len(missing) > 0:
        print(
            f"Timestamp check FAILED: {len(missing)} missing hour(s), "
            f"first: {missing[0]}.",
            file=sys.stderr,
        )
        ok = False

    if not ok:
        sys.exit(1)

    print(f"Timestamp check passed: {n_actual} hourly steps, no gaps or duplicates.")


def concat_yearly(input_dir, variable, year, output_file,
                  lat_min=None, lat_max=None, lon_min=None, lon_max=None,
                  compress_level=4):
    """
    Concatenate monthly interpolated files for one variable+year into a single yearly file.
    Validates that the merged time axis is complete and hourly.
    If a lat-lon box is provided, grid points outside it are set to NaN (full grid preserved).
    """
    pattern = os.path.join(input_dir, f"{variable}_{year:04d}??.nc")
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No files found matching: {pattern}", file=sys.stderr)
        sys.exit(1)

    print(f"Concatenating {len(files)} file(s) for {variable} {year}...")
    ds = xr.open_mfdataset(files, combine="by_coords")

    validate_hourly_timestamps(ds, year)

    if any(v is not None for v in [lat_min, lat_max, lon_min, lon_max]):
        lat_name = "latitude" if "latitude" in ds.coords else "lat"
        lon_name = "longitude" if "longitude" in ds.coords else "lon"

        lat = ds[lat_name]
        lon = ds[lon_name]

        # 2-D mask that broadcasts over (lat, lon); time axis is preserved.
        lat_mask = (lat >= lat_min) & (lat <= lat_max)
        lon_mask = (lon >= lon_min) & (lon <= lon_max)
        ds = ds.where(lat_mask & lon_mask)

    # Normalise the time dimension name to "time" for downstream compatibility.
    time_name = next(
        (n for n in ("valid_time", "time") if n in ds.dims),
        None,
    )
    if time_name and time_name != "time":
        ds = ds.rename({time_name: "time"})

    output_dir = os.path.dirname(os.path.abspath(output_file))
    os.makedirs(output_dir, exist_ok=True)

    encoding = {}
    if compress_level > 0:
        encoding = {var: {"zlib": True, "complevel": compress_level}
                    for var in ds.data_vars}

    ds.to_netcdf(output_file, encoding=encoding, unlimited_dims=["time"])
    print(f"Saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Concatenate monthly interpolated ERA5 files into a single yearly file."
    )
    parser.add_argument("--input-dir", required=True,
                        help="Root directory containing per-variable interpolated files.")
    parser.add_argument("--variable", required=True,
                        help="ERA5 variable name (e.g. 2m_temperature).")
    parser.add_argument("--year", type=int, required=True,
                        help="Year to concatenate.")
    parser.add_argument("--output-dir", required=True,
                        help="Root directory for yearly output files.")
    parser.add_argument("--lat-min", type=float, default=None, metavar="LAT",
                        help="Southern boundary of mask box.")
    parser.add_argument("--lat-max", type=float, default=None, metavar="LAT",
                        help="Northern boundary of mask box.")
    parser.add_argument("--lon-min", type=float, default=None, metavar="LON",
                        help="Western boundary of mask box.")
    parser.add_argument("--lon-max", type=float, default=None, metavar="LON",
                        help="Eastern boundary of mask box.")
    parser.add_argument("--compress", type=int, default=4, metavar="LEVEL",
                        help="zlib compression level 0-9 (0 = off, default: 4).")

    args = parser.parse_args()

    input_dir = os.path.join(args.input_dir, args.variable)
    output_file = os.path.join(
        args.output_dir, args.variable, f"{args.variable}_{args.year:04d}.nc"
    )

    concat_yearly(
        input_dir, args.variable, args.year, output_file,
        lat_min=args.lat_min, lat_max=args.lat_max,
        lon_min=args.lon_min, lon_max=args.lon_max,
        compress_level=args.compress,
    )


if __name__ == "__main__":
    main()
