"""
Check that every variable under a yearly-concat ERA5 directory has complete
hourly data for each year in a given range.

Expected layout:
    <data_dir>/<variable>/<variable>_<YYYY>.nc

For each file the script verifies:
  - The file exists.
  - It can be opened by xarray.
  - The time axis contains exactly the expected number of hourly steps
    (8760 for common years, 8784 for leap years) with no gaps or duplicates.

Exit code: 0 if all checks pass, 1 otherwise.
"""

import argparse
import os
import sys

import pandas as pd
import xarray as xr


START_YEAR = 1941
END_YEAR = 1970


def expected_hours(year):
    start = pd.Timestamp(f"{year}-01-01 00:00")
    end = pd.Timestamp(f"{year}-12-31 23:00")
    return pd.date_range(start=start, end=end, freq="h", inclusive="both")


def check_file(filepath, year):
    """
    Open a yearly NetCDF file and validate its hourly time axis.

    Returns a list of problem strings (empty list means OK).
    """
    problems = []

    if not os.path.exists(filepath):
        problems.append("file missing")
        return problems

    try:
        ds = xr.open_dataset(filepath)
    except Exception as exc:
        problems.append(f"cannot open: {exc}")
        return problems

    time_name = next(
        (n for n in ("valid_time", "time") if n in ds.coords or n in ds.dims),
        None,
    )
    if time_name is None:
        problems.append("no time coordinate found")
        ds.close()
        return problems

    times = pd.DatetimeIndex(ds[time_name].values)
    ds.close()

    expected = expected_hours(year)
    n_expected = len(expected)
    n_actual = len(times)

    if n_actual != n_expected:
        problems.append(f"expected {n_expected} hours, got {n_actual}")

    duplicates = times[times.duplicated()]
    if len(duplicates):
        problems.append(f"{len(duplicates)} duplicate timestamp(s), first: {duplicates[0]}")

    missing = expected.difference(times)
    if len(missing):
        problems.append(f"{len(missing)} missing hour(s), first: {missing[0]}")

    return problems


def check_variable(data_dir, variable, years):
    """
    Check all yearly files for one variable.

    Returns a dict mapping year -> list-of-problems (empty list = OK).
    """
    results = {}
    var_dir = os.path.join(data_dir, variable)
    for year in years:
        filepath = os.path.join(var_dir, f"{variable}_{year:04d}.nc")
        results[year] = check_file(filepath, year)
    return results


def discover_variables(data_dir):
    """Return sorted list of subdirectory names (one per variable)."""
    try:
        entries = os.listdir(data_dir)
    except FileNotFoundError:
        print(f"Error: data directory not found: {data_dir}", file=sys.stderr)
        sys.exit(1)
    return sorted(e for e in entries if os.path.isdir(os.path.join(data_dir, e)))


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Verify that every ERA5 variable has complete hourly yearly files "
            f"for {START_YEAR}–{END_YEAR}."
        )
    )
    parser.add_argument(
        "--data-dir",
        default="ERA5_0p5deg_hourly_concat_to_yearly_data",
        help="Root directory containing per-variable yearly NetCDF files.",
    )
    parser.add_argument(
        "--start-year", type=int, default=START_YEAR,
        help=f"First year to check (default: {START_YEAR}).",
    )
    parser.add_argument(
        "--end-year", type=int, default=END_YEAR,
        help=f"Last year to check (default: {END_YEAR}).",
    )
    args = parser.parse_args()

    data_dir = os.path.abspath(args.data_dir)
    years = list(range(args.start_year, args.end_year + 1))
    n_years = len(years)

    variables = discover_variables(data_dir)
    if not variables:
        print(f"No variable subdirectories found in: {data_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Data directory : {data_dir}")
    print(f"Variables found: {len(variables)}")
    print(f"Years to check : {args.start_year}–{args.end_year} ({n_years} years)")
    print()

    all_ok = True

    for variable in variables:
        results = check_variable(data_dir, variable, years)
        failed_years = {yr: probs for yr, probs in results.items() if probs}

        if not failed_years:
            print(f"[OK]  {variable}  ({n_years}/{n_years} years pass)")
        else:
            all_ok = False
            n_ok = n_years - len(failed_years)
            print(f"[FAIL] {variable}  ({n_ok}/{n_years} years pass)")
            for yr in sorted(failed_years):
                for problem in failed_years[yr]:
                    print(f"       {yr}: {problem}")

    print()
    if all_ok:
        print("All checks passed.")
        sys.exit(0)
    else:
        print("Some checks FAILED — see details above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
