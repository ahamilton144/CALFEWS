#!/bin/bash

#SBATCH -J b_infra
#SBATCH -o results/infra_moo/baseline.out
#SBATCH -e results/infra_moo/baseline.err
#SBATCH -p RM-shared
#SBATCH -t 00:30:00
#SBATCH --nodes 1
#SBATCH --ntasks-per-node 1
#SBATCH --cpus-per-task 50

numMC=100
numProcs=50
sed -i "s:dv_formulation = .*:dv_formulation = 0:g" problem_infra.py
sed -i "s:num_MC = .*:num_MC = "$numMC":g" problem_infra.py 
sed -i "s:num_procs = .*:num_procs = "$numProcs":g" problem_infra.py 

time srun python -W ignore run_baselines.py
