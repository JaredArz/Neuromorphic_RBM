#!/bin/bash

#SBATCH -J SA          # Job name
#SBATCH -o ./slurm/out/SA.o%j       # Name of stdout output file
#SBATCH -e ./slurm/out/SA.e%j       # Name of stderr error file
#SBATCH -p normal            # Queue (partition) name
#SBATCH -N 1                 # Total # of nodes (must be 1 for serial)
#SBATCH -n 1               # Total # of mpi tasks (should be 1 for serial)
#SBATCH -t 12:00:00          # Run time (hh:mm:ss)
#SBATCH -A OTH21017          # Project allocation
#SBATCH --mail-user=jared.arzate@utexas.edu
#SBATCH --mail-type=all      # Send email at begin and end of job

# Other commands must follow all #SBATCH directives...

pwd
date

# Launch code
srun -c 127 python main.py

