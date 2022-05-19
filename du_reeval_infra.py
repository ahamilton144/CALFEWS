from mpi4py import MPI
import sys
import os
import shutil
import json
import numpy as np
from multiprocessing import Process, Array
import h5py
import time
from datetime import datetime
import main_cy




### function to setup problem for particular infra soln
def setup_problem(results_folder, rank, soln):
    ### setup/initialize model
    sys.stdout.flush()

    try:
        os.mkdir(results_folder)
    except:
        pass

    resultsfile = 'results_arx/infra_moo/overall_ref/overall_clean.csv'
    linenum = soln + 1

    with open(resultsfile, 'r') as f:
        for i, line in enumerate(f):
          if i == 0:
              cols = line
          if i == linenum:
              vals = line
              break

    cols = cols.strip().split(',')
    vals = vals.strip().split(',')
    dv_project = int(vals[2])
    share_cols = [cols[i] for i in range(len(cols)) if 'share' in cols[i]]
    share_vals = [vals[i] for i in range(len(cols)) if 'share' in cols[i]]
    share_vals = [v if v != '' else '0.0' for v in share_vals]
    dv_share_dict = {col.split('_')[1]: float(val) for col, val in zip(share_cols, share_vals)}

    ### apply ownership fractions for FKC expansion based on dvs from dv_share_dict
    scenario = json.load(open('calfews_src/scenarios/FKC_properties__rehab_ownership_all.json'))
    districts = list(scenario['ownership_shares'].keys())
    ### add districts OTL & OFK, which were included in previous Earth's Future study, but excluded from optimization.
    ###    they will only be non-zero for manually added solns from EF study.
    districts.extend(['OTL','OFK'])
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
    with h5py.File(f'{results_folder}/../results_rank{rank}.hdf5', 'a') as open_hdf5:
        if f'soln{soln}' not in list(open_hdf5.keys()):
            d = open_hdf5.create_dataset(f'soln{soln}', (336, num_MC), dtype='float', compression='gzip')
            dvs = [dv_project]
            dv_names = ['proj']
            for k,v in dv_share_dict.items():
                dvs.append(v)
                dv_names.append(k)
            d.attrs['dvs'] = dvs
            d.attrs['dv_names'] = dv_names
            d.attrs['colnames'] = MC_labels



### function to run a single MC trial
def run_sim(results_folder, start_time, model_mode, flow_input_type, flow_input_source, MC_label, uncertainty_dict, MC_count, soln, MC_to_be_run):
#    try:
        if MC_to_be_run[MC_count]:
            main_cy_obj = main_cy.main_cy(results_folder, model_mode=model_mode, flow_input_type=flow_input_type, flow_input_source=flow_input_source, flow_input_addition=MC_label)
            uncertainty_dict['synth_gen_seed'] = int(MC_label)
            a = main_cy_obj.initialize_py(uncertainty_dict)
            a = main_cy_obj.run_sim_py(start_time)
            main_cy_obj.get_district_results(results_folder=results_folder, baseline_folder='', MC_label=MC_label, shared_objs_array=[], MC_count=MC_count, is_baseline=False, is_reeval=True, soln=soln)
 #   except:
 #       print('fail in run sim', results_folder, soln, MC_label)


### run a single MC instance and fill in slot in objective dictionary
def dispatch_MC_to_procs(results_folder, start_time, model_modes, flow_input_types, flow_input_sources, MC_labels, uncertainty_dict, proc, start, stop, soln, MC_to_be_run):
    if stop > start:
        idxs = [i for i in range(len(MC_to_be_run)) if MC_to_be_run[i]]
        for i in range(start, stop):
            MC_count = idxs[i]
            run_sim(results_folder, start_time, model_modes[MC_count], flow_input_types[MC_count], flow_input_sources[MC_count],
                    MC_labels[MC_count], uncertainty_dict, MC_count, soln, MC_to_be_run)



### main body
if __name__ == "__main__":
    overall_start_time = datetime.now()

    base_results_folder = sys.argv[1]
    tasks_total = int(sys.argv[2])
    num_procs = int(sys.argv[3])
    num_solns_total = int(sys.argv[4])
    start_solns_total = int(sys.argv[5])
    num_MC = int(sys.argv[6])
    start_MC = int(sys.argv[7])

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    ### get list of solns assigned to this task
    solns = []
    r = 0
    for i in range(start_solns_total, start_solns_total + num_solns_total):
        if r == rank:
            solns.append(i)
        r += 1
        if r == size:
            r = 0

    ### loop over solns assigned to this task & do MC trial for infrastructure setup
    for soln in solns:
        start_time = datetime.now()

        ### define MC sampling problem/parallelization
        model_modes = ['simulation'] * num_MC
        flow_input_types = ['synthetic'] * num_MC
        flow_input_sources = ['mghmm_30yr_generic'] * num_MC
        MC_labels = [str(i + start_MC) for i in range(num_MC)]  # ['wet','dry']

        ### uncertainties
        uncertainty_dict = {'dry_state_mean_multiplier': 0.9, 'wet_state_mean_multiplier': 1.1,
                            'covariance_matrix_dry_multiplier': 0.9, 'covariance_matrix_wet_multiplier': 1.1,
                            'transition_drydry_addition': 0.1, 'transition_wetwet_addition': 0.2}

        ### setup problem for this soln
        results_folder = f'{base_results_folder}/soln{soln}/'
        setup_problem(results_folder, rank, soln)

        ### figure out which MC samps still need to be run
        MC_to_be_run = []
        with h5py.File(f'{results_folder}/../results_rank{rank}.hdf5', 'a') as open_hdf5:
            d = open_hdf5[f'soln{soln}']
            for MC_count,MC_label in enumerate(MC_labels):
                has_hdf5_results = np.sum(np.abs(d[:, MC_count])) > 1e-9
                json_exists = os.path.exists(f'{results_folder}/soln{soln}_mc{MC_label}.json')
                if not has_hdf5_results and not json_exists:
                    MC_to_be_run.append(True)
                else:
                    MC_to_be_run.append(False)

        ### assign MC trials to processors
        shared_processes = []
        nbase = int(sum(MC_to_be_run) / num_procs)
        remainder = sum(MC_to_be_run) - num_procs * nbase
        start = 0
        for proc in range(num_procs):
            num_trials = nbase if proc >= remainder else nbase + 1
            stop = start + num_trials
            p = Process(target=dispatch_MC_to_procs, args=(results_folder, start_time, model_modes, flow_input_types,
                                                           flow_input_sources, MC_labels, uncertainty_dict,
                                                           proc, start, stop, soln, MC_to_be_run))
            shared_processes.append(p)
            start = stop

        # Start processes
        for sp in shared_processes:
            sp.start()

        # Wait for all processes to finish
        for sp in shared_processes:
            sp.join()

        ### after all MC have finished, go back and write all results for this soln to hdf5
        with h5py.File(f'{results_folder}/../results_rank{rank}.hdf5', 'a') as open_hdf5:
            d = open_hdf5[f'soln{soln}']
            for MC_count, MC_label in enumerate(MC_labels):
                has_hdf5_results = np.sum(np.abs(d[:, MC_count])) > 1e-9
                if not has_hdf5_results:
                    district_results = json.load(open(f'{results_folder}/soln{soln}_mc{MC_label}.json'))           
                    results_list = []
                    for k,v in district_results.items():
                        results_list.extend(v.values())
                    d[:len(results_list), MC_count] = np.array(results_list)
                    ### only need to store rownames once
                    if MC_count == 0:
                        objs_list = []
                        for k, v in district_results.items():
                            objs_list.extend([k + '_' + vk for vk in v.keys()])
                        d.attrs['rownames'] = objs_list

        ### remove directory for this MC trial, since results recorded in main hdf5
        shutil.rmtree(results_folder)
        print(f'solution {soln} finished, rank {rank}, time {datetime.now() - overall_start_time}')

