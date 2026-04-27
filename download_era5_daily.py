import argparse
import os
import multiprocessing
import cdsapi

DATASET = "derived-era5-single-levels-daily-statistics"

ALL_MONTHS = [f"{m:02d}" for m in range(1, 13)]
ALL_DAYS = [f"{d:02d}" for d in range(1, 32)]

DEFAULT_VARIABLES = [
    "evaporation",
    "total_precipitation",
    "2m_temperature",
]


def download_month(args):
    variable, year, month, output_root = args

    output_dir = os.path.join(output_root, variable)
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"{variable}_{year}_{month}.nc")

    if os.path.exists(output_file):
        print(f"Skipping {output_file} (already exists)")
        return

    request = {
        "product_type": "reanalysis",
        "variable": [variable],
        "year": str(year),
        "month": month,
        "day": ALL_DAYS,
        "daily_statistic": "daily_mean",
        "time_zone": "utc+00:00",
        "frequency": "1_hourly",
        "format": "netcdf",
    }

    print(f"Downloading {variable} {year}-{month} -> {output_file}")
    client = cdsapi.Client()
    client.retrieve(DATASET, request).download(output_file)
    print(f"Saved {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Download ERA5 daily statistics from CDS to a structured output directory."
    )
    parser.add_argument("--output-root", required=True,
                        help="Root output directory. Files are saved as <output_root>/<variable>/<variable>_<year>_<month>.nc")
    parser.add_argument("--year-start", type=int, required=True,
                        help="First year to download.")
    parser.add_argument("--year-end", type=int, required=True,
                        help="Last year to download (inclusive).")
    parser.add_argument("--variables", nargs="+", default=DEFAULT_VARIABLES,
                        help=f"Variables to download (default: {DEFAULT_VARIABLES})")
    parser.add_argument("--workers", type=int, default=2,
                        help="Number of parallel download workers (default: 2).")

    args = parser.parse_args()

    if args.year_end < args.year_start:
        parser.error("--year-end must be >= --year-start")

    tasks = [
        (variable, year, month, args.output_root)
        for year in range(args.year_start, args.year_end + 1)
        for month in ALL_MONTHS
        for variable in args.variables
    ]

    with multiprocessing.Pool(processes=args.workers) as pool:
        pool.map(download_month, tasks)

    print("All downloads completed.")


if __name__ == "__main__":
    main()
