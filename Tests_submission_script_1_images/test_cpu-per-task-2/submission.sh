#!/bin/env bash 
# SBATCH --partition=shared-cpu 
# SBATCH --time=00:30:00 
# SBATCH --output=kraken-%j.out
# SBATCH --cpus-per-task=2
# SBATCH --ntasks=1
# SBATCH --mem=32G


module load GCCcore/11.3.0 Python/3.10.4

cd /home/users/p/philipm/rtk
source ./env/bin/activate 

echo "====="

echo "============DATETIME========="

srun date

echo "RTK running"
srun python rtk-script-taton.py

echo "============DATETIME========="

srun date

