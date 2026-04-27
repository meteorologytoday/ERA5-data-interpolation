#!/bin/bash
# Source this file to activate the project environment:
#   source activate_env.sh

eval "$(/home/tienyiao/miniconda3/bin/conda shell.bash hook 2> /dev/null)" || { echo "Error: could not initialize conda"; return 1; }
conda activate gemini_env || { echo "Error: could not activate gemini_env"; return 1; }

echo "Environment 'gemini_env' activated."
