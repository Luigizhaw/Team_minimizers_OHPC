#!/bin/bash
#SBATCH --job-name=solar_model_103
#SBATCH --output=output_%j.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB
#SBATCH --time=12:00:00

# Load Python environment
module load python/3.9
source ohpc/bin/activate

# Run the simulation with the parameter set
python simulate.py --params "(1955.0, 1.0, 16.25)"