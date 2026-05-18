#! /bin/sh
##SBATCH --account=next
#SBATCH --job-name=LPJ-Forcing-interp
#
#SBATCH --tasks 64
#SBATCH --nodes 1
#
# Acceptable time formats include "minutes", "minutes:seconds", "hours:minutes:seconds",
#                   "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds"
#SBATCH --qos=short
#SBATCH --time=10:00:00 
#
#SBATCH --account=poem
#SBATCH --output=sbatch.64.%j.out
#SBATCH --error=sbatch.64.%j.err
#SBATCH --mail-type=TIME_LIMIT




eval "$( /home/tienyiao/miniconda3/bin/conda shell.bash hook 2> /dev/null)"
conda activate rainbow
NJOBS=${SLURM_NTASKS:-4}
./run_downscaling.sh -j $NJOBS
