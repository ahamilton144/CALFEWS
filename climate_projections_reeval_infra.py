import sys
import os
import shutil
import json
from datetime import datetime
from glob import glob
import numpy as np
import h5py

import main_cy


### function to setup problem for particular infra soln
def setup_problem(results_folder, soln_label, flow_input_sources):
    ### setup/initialize model
    sys.stdout.flush()

    try:
        os.makedirs(results_folder)
    except:
        pass

    resultsfile = 'results_arx/infra_wcu/objs_wcu_pareto_withStatusQuo.csv'

    min_share = 0.01

    with open(resultsfile, 'r') as f:
        for i, line in enumerate(f):
            if i == 0:
                cols = line
            elif i == 1 and soln_label == 'baseline':
                vals = line
                break
            elif soln_label in line:
                vals = line
                break

        cols = cols.strip().replace(' ','').split(',')
        vals = vals.strip().replace(' ','').split(',')
        share_cols = [cols[i] for i in range(len(cols)) if 'share' in cols[i]]
        if soln_label == 'baseline':
            dv_project = 0
            share_vals = ['0.0' for i in range(len(cols)) if 'share' in cols[i]]
        else:
            dv_project = int(float(vals[1]))
            share_vals = [vals[i] for i in range(len(cols)) if 'share' in cols[i]]
        share_vals = [v if v != '' else '0.0' for v in share_vals]
        dv_share_dict = {col.split('_')[1]: float(val) for col, val in zip(share_cols, share_vals)}

    ### Like in optimization, normalize shares to sum to 1, then set all districts below min_share to 0, then renormalize.
    if soln_label not in ['baseline', 'statusquo/soln0']:
        sum_shares = sum(dv_share_dict.values())
        dv_share_dict = {k: v / sum_shares for k,v in dv_share_dict.items()}
        loop = 0
        while (loop < 5) and sum([1 for s in dv_share_dict.values() if s < min_share and s > 0]) > 0:
            dv_share_dict = {k: 0. if v < min_share else v for k,v in dv_share_dict.items()}
            sum_shares = sum(dv_share_dict.values())
            dv_share_dict = {k: v / sum_shares for k,v in dv_share_dict.items()}
            loop += 1

    ### apply ownership fractions for FKC expansion based on dvs from dv_share_dict
    scenario = json.load(open('calfews_src/scenarios/FKC_properties__rehab_ownership_all.json'))
    districts = list(scenario['ownership_shares'].keys())
    ### add aggregated district OFK which is included in status quo friant solution but was not part of optimization
    districts.extend(['OFK'])
    for i, k in enumerate(districts):
        if dv_project in [1,3]:   #1=FKC only, 3=FKC+CFWB
            scenario['ownership_shares'][k] = dv_share_dict[k]
        else:                     #2=CFWB only, so set FKC ownership params to 0
            scenario['ownership_shares'][k] = 0.
    ### save new scenario to results folder
    with open(results_folder + '/FKC_scenario.json', 'w') as o:
        json.dump(scenario, o, indent=4)

    ### apply ownership fractions for CFWB based on dvs, plus capacity params for CFWB
    scenario = json.load(open('calfews_src/scenarios/CFWB_properties__large_all.json'))
    removeddistricts = []
    for i, k in enumerate(districts):
        if dv_project in [2,3]:   #2=CFWB only, 3=FKC+CFWB
            share = dv_share_dict[k]
        else:                     #1=FKC only
            share = 0.
        if share > 0.0:
            scenario['ownership'][k] = share
            scenario['bank_cap'][k] = 99999.9
            if k not in scenario['participant_list']:
                scenario['participant_list'].append(k)
        else:
            removeddistricts.append(k)
    for k in removeddistricts:
        ### remove zero-ownership shares from other banking ownership lists. remove will fail for OTL/OFK since not originally included.
        try:
            scenario['participant_list'].remove(k)
            del scenario['ownership'][k]
            del scenario['bank_cap'][k]
        except:
            pass
    scenario['initial_recharge'] = 300.
    scenario['tot_storage'] = 0.6
    scenario['recovery'] = 0.2
    scenario['proj_type'] = dv_project
    with open(results_folder + '/CFWB_scenario.json', 'w') as o:
        json.dump(scenario, o, indent=4)


    ### create new sheet in results hdf5 file, and save dvs
    with h5py.File(f'{base_results_folder}/results_climate_reeval.hdf5', 'a') as open_hdf5:
        d = open_hdf5.create_dataset(soln_label, (168, len(flow_input_sources)), dtype='float', compression='gzip')
        dvs = [dv_project]
        dv_names = ['proj']
        for k,v in dv_share_dict.items():
            dvs.append(v)
            dv_names.append(k)
        d.attrs['dvs'] = dvs
        d.attrs['dv_names'] = dv_names
        d.attrs['colnames'] = flow_input_sources



### main body
if __name__ == "__main__":
    overall_start_time = datetime.now()

    base_results_folder = 'results/climate_reeval_infra_bridges2/'

    solns = ['baseline', 'statusquo/soln0', 's3/soln212']
    soln_num = 0 #just used for labeling results, not needed here
    ### loop over solns assigned to this task & run climate projection scenarios
    for soln_label in solns:
        start_time = datetime.now()

        ### define climate projections
        scenarios = glob('calfews_src/data/CA_FNF_climate_change/CA_FNF_*.csv')
        ### drop canesm2 scenarios, which have a data inconsistency issue
        scenarios = [s for s in scenarios if 'canesm2' not in s]
        scenarios = scenarios[:1]

        num_scenarios = len(scenarios)
        model_modes = ['simulation'] * num_scenarios
        flow_input_types = ['downscaled_19502100'] * num_scenarios
        flow_input_sources = [s.split('/')[-1].replace('CA_FNF_','').replace('_r1i1p1.csv','') for s in scenarios]

        ### uncertainties
        uncertainty_dict = {}

        ### setup problem for this soln
        results_folder = f'{base_results_folder}/{soln_label}/'
        setup_problem(results_folder, soln_label, flow_input_sources)

        ### loop over climate scenarios & run separate climate scenario for each
        for i, flow_input_source in enumerate(flow_input_sources):
            print(f'Starting {soln_label}, {flow_input_source}, {datetime.now() - start_time}')
            results_folder_inner = f'{results_folder}/{flow_input_source}/'
            os.mkdir(results_folder_inner)
            shutil.copy2(f'{results_folder}/CFWB_scenario.json', f'{results_folder_inner}/CFWB_scenario.json')
            shutil.copy2(f'{results_folder}/FKC_scenario.json', f'{results_folder_inner}/FKC_scenario.json')

            main_cy_obj = main_cy.main_cy(results_folder_inner, model_mode=model_modes[i],
                                          flow_input_type=flow_input_types[i], flow_input_source=flow_input_source)
            a = main_cy_obj.initialize_py(uncertainty_dict)
            a = main_cy_obj.run_sim_py(start_time)
            a = main_cy_obj.output_results()
            main_cy_obj.get_district_results(results_folder=results_folder_inner,
                                             baseline_folder=f'{base_results_folder}/baseline/{flow_input_source}/',
                                             MC_label=flow_input_source, shared_objs_array=[], MC_count=i,
                                             is_baseline=soln_label=='baseline', is_reeval=True, soln=soln_num)

        ### after all MC have finished, go back and write all results for this soln to hdf5
        with h5py.File(f'{base_results_folder}/results_climate_reeval.hdf5', 'a') as open_hdf5:
            d = open_hdf5[soln_label]
            for i, flow_input_source in enumerate(flow_input_sources):
                if soln_label == 'baseline':
                    filename = f'{base_results_folder}/{soln_label}/{flow_input_source}/{flow_input_source}_baseline.json'
                else:
                    filename = f'{base_results_folder}/{soln_label}/{flow_input_source}/soln{soln_num}_mc{flow_input_source}.json'
                district_results = json.load(open(filename))
                results_list = []
                for k,v in district_results.items():
                    results_list.extend(v.values())
                d[:len(results_list), i] = np.array(results_list)
                ### only need to store rownames once
                if i == 0:
                    objs_list = []
                    for k, v in district_results.items():
                        objs_list.extend([k + '_' + vk for vk in v.keys()])
                    d.attrs['rownames'] = objs_list
