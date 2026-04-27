#!/bin/bash

variables=(
    2m_temperature
    total_precipitation
    evaporation
)

for variable in "${variables[@]}"; do
    ./run_interpolation.sh -o ERA5_0p5deg -v $variable -i ./ERA5-daily
done
