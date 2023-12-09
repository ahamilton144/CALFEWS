#!/bin/bash

results=results/MOO_results_bridges2/

### provide all combinations of decision variable formulation (dv) and seed, along with the final number of function evals from the last runtime file (nfes_final) and the NFE at the beginning of the simulation
dvs=(2 2 2 2)
seeds=(1 1 2 3)

#### round 1
round=1
nfes_init=(0 3100 0 0)
nfes_final=(3100 42401 40400 42200)
dir_names=('dv2_seed1_round1a' 'dv2_seed1_round1b' 'dv2_seed2_round1' 'dv2_seed3_round1')

### round 2
#round=2

### round 3
#round=3

### run postprocessing for this round
num_results=${#dvs[@]}

mkdir $results/overall_ref

### find objectives & ref sets for each seed
for (( i=0; i<$num_results; i++ )); do
	dv=${dvs[$i]}
	seed=${seeds[$i]}
	nfe_init=${nfes_init[$i]}
	nfe_final=${nfes_final[$i]}
	subdir=$results/${dir_names[$i]}

	### find reference set for this seed
	sh find_refset.sh $subdir $dv $seed $nfe_init $nfe_final
	### get objective values at each runtime write
	sh find_objs.sh $subdir $dv $seed $nfe_init $nfe_final
	### copy to overall ref set directory
	cp $subdir/*.reference $results/overall_ref
done
