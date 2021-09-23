import numpy as np
import problem_infra


### execution params
num_MC = 1
num_procs = 1

### uncertainties
uncertainty_dict = {}
# uncertainty_dict['MDD_multiplier'] = 1.1
# uncertainty_dict['ag_demand_multiplier'] = {'crop': {'maj_orchardvineyard':1.1, 'maj_other':0.8}, 'friant': {'friant': 0.9, 'non_friant': 1.0}}

# uncertainty_dict['env_min_flow_base'] = {'MIL': 150., 'PFT': 150., 'KWH': 35., 'SUC': 15., 'ISB':75, 'SHA': 3000, 'ORO':1500}
# uncertainty_dict['env_min_flow_peak_multiplier'] = {'MIL': 1.1, 'PFT': 1.1, 'KWH': 1.1, 'SUC': 1.1, 'ISB': 1.1, 'SHA': 2, 'ORO':1.5}
# uncertainty_dict['delta_min_outflow_base'] = 3500
# uncertainty_dict['delta_min_outflow_peak_multiplier'] = 1.2



### first run baseline version
### decision variables for problem
dvs = np.zeros(42)

objs = problem_infra.problem_infra(dvs, num_MC, num_procs, uncertainty_dict, is_baseline=True)

print()
print()
print(objs)



# ### now run for infrastructure scenario
# dvs = np.zeros(42)
# dvs[0] = 3
# dvs[11] = 0.33
# dvs[17] = 0.34
# dvs[26] = 0.33

# objs = problem_infra.problem_infra(dvs, num_MC, num_procs, uncertainty_dict, is_baseline=False)

# print()
# print()
# print(objs)