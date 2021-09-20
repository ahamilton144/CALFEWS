import sys
import os
import shutil
import json
import math
import numpy as np
import pandas as pd
from configobj import ConfigObj
from distutils.util import strtobool
from datetime import datetime
import main_cy



def prep_sim(exp_name, results_folder, print_log):
  ### setup/initialize model
  sys.stdout.flush()

  ### remove any old results
#  try:
#    shutil.rmtree(results_folder)
#  except:
#    pass
  try:
    os.mkdir(results_folder)  
  except:
    pass

  if print_log:
    sys.stdout = open(results_folder + '/log.txt', 'w')

  print('#######################################################')
  print('Experiment ', exp_name)
  print('#######################################################')
  print('Begin initialization...')    




def run_sim(results_folder, runtime_file, start_time):
  ### setup new model
  main_cy_obj = main_cy.main_cy(results_folder, runtime_file)
  a = main_cy_obj.initialize_py()

  if a == 0:
    print('Initialization complete, ', datetime.now() - start_time)
    sys.stdout.flush()
    ### main simulation loop
    a = main_cy_obj.run_sim_py(start_time)

    if a == 0:
      print ('Simulation complete,', datetime.now() - start_time)
      sys.stdout.flush()
      ### calculate objectives
      main_cy_obj.calc_objectives()
      print ('Objective calculation complete,', datetime.now() - start_time)

      ### output results
      main_cy_obj.output_results()
      print ('Data output complete,', datetime.now() - start_time)
      sys.stdout.flush()



########################################################################
### main experiment
########################################################################

rerun_baselines = int(sys.argv[1]) ### 1 if we want to rerun zero-ownership & full-ownership cases
start_scenarios = int(sys.argv[2])  ### number of random ownership configs to run
end_scenarios = int(sys.argv[3])
nscenarios = end_scenarios - start_scenarios

#rank = int(sys.argv[4])
#nprocs = int(sys.argv[5])
#count = int(math.floor(nscenarios/nprocs))
#remainder = nscenarios % nprocs
## Use the processor rank to determine the chunk of work each processor will do
#if rank < remainder:
#  start = rank*(count+1) + start_scenarios
#  stop = start + count + 1 
#else:
#  start = remainder*(count+1) + (rank-remainder)*count + start_scenarios
#  stop = start + count 
start = start_scenarios
stop = end_scenarios

#print('Hello from processor ',rank, ' out of ', nprocs, ', running samples ', start, '-', stop-1)

# get runtime params from config file
try:
  runtime_file = sys.argv[4]
except:
  runtime_file = 'runtime_params.ini'

config = ConfigObj(runtime_file)
# parallel_mode = bool(strtobool(config['parallel_mode']))
cluster_mode = bool(strtobool(config['cluster_mode']))
print_log = bool(strtobool(config['print_log']))
flow_input_source = config['flow_input_source']
scratch_dir = config['scratch_dir']

if cluster_mode:
  results_base = scratch_dir + '/FKC_experiment/'
else:
  results_base = 'results/'



### run basline without FKC or CFWB, if argv1 == 1 and processor rank == last
#if rerun_baselines == 1 and rank == (nprocs - 1):
if rerun_baselines == 1:

#  results_folder = results_base + 'FKC_experiment_' + flow_input_source + '_none'
#  start_time = datetime.now()

#  if not os.path.exists(results_folder):

#    try:
#    prep_sim('None', results_folder, print_log)

#    scenario = json.load(open('calfews_src/scenarios/FKC_properties__rehab_ownership_all.json'))
#    for i, k in enumerate(scenario['ownership_shares'].keys()):
#      scenario['ownership_shares'][k] = 0.0
#    with open(results_folder + '/FKC_scenario.json', 'w') as o:
#      json.dump(scenario, o)

#    scenario = json.load(open('calfews_src/scenarios/CFWB_properties__large_all.json'))
#    scenario['participant_list'] = []
#    scenario['ownership'] = {}
#    scenario['bank_cap'] = {}
#    scenario['initial_recharge'] = 0.0
#    scenario['tot_storage'] = 0.0
#    scenario['recovery'] = 0.0
#    with open(results_folder + '/CFWB_scenario.json', 'w') as o:
#      results_folder + '/CFWB_scenario.json'
#      json.dump(scenario, o)

#    run_sim(results_folder, runtime_file, start_time)
#    except:
#      print('EXPERIMENT FAIL: ', results_folder)


  ### now get baseline with all districts given access to FKC
#  results_folder = results_base + 'FKC_experiment_' + flow_input_source + '_all'
#  start_time = datetime.now()
#
#  if not os.path.exists(results_folder):

#    try:
#    prep_sim('All', results_folder, print_log)

#    scenario = json.load(open('calfews_src/scenarios/FKC_properties__rehab_ownership_all.json'))
#    for i, k in enumerate(scenario['ownership_shares'].keys()):
#      scenario['ownership_shares'][k] = 1.0
#    with open(results_folder + '/FKC_scenario.json', 'w') as o:
#      json.dump(scenario, o)

#    scenario = json.load(open('calfews_src/scenarios/CFWB_properties__large_all.json'))
#    scenario['participant_list'] = []
#    scenario['ownership'] = {}
#    scenario['bank_cap'] = {}
#    scenario['initial_recharge'] = 0.0
#    scenario['tot_storage'] = 0.0
#    scenario['recovery'] = 0.0
#    with open(results_folder + '/CFWB_scenario.json', 'w') as o:
#      results_folder + '/CFWB_scenario.json'
#      json.dump(scenario, o)

#    run_sim(results_folder, runtime_file, start_time)

  ### baseline - equal ownership across friant contractors
  results_folder = results_base + 'FKC_experiment_' + flow_input_source + '_friantEqual'
  start_time = datetime.now()

  if not os.path.exists(results_folder):

    prep_sim('Friant', results_folder, print_log)

    scenario = json.load(open('calfews_src/scenarios/FKC_properties__rehab_ownership_all.json'))
    is_friant = {'BDM':False, 'BLR':False, 'BVA':False, 'CWO':False, 'HML':False, 'ID4':False, 'KND':False, 'LHL':False, 
                 'RRB':False, 'SMI':False, 'THC':False, 'TJC':False, 'WKN':False, 'WRM':False, 'KCWA':False, 'COB':False, 
                 'NKN':False, 'ARV':True, 'PIX':False, 'DLE':True, 'EXE':True, 'OKW':False, 'KRT':False, 'LND':True, 
                 'LDS':True, 'LWT':True, 'PRT':True, 'SAU':True, 'SFW':True, 'SSJ':True, 'TPD':True, 'TBA':True, 
                 'TUL':True, 'COF':True, 'FRS':True, 'SOC':False, 'SOB':False, 'CCA':False, 'DLR':False, 'TLB':False, 
                 'KWD':False, 'WSL':False, 'SNL':False, 'PNC':False, 'DLP':False, 'CWC':False, 'MAD':False, 'OTL':False, 
                 'OFK':True, 'OCD':False, 'OEX':False, 'OXV':False, 'OSW':False, 'CNS':False, 'ALT':False, 'KRWA':False}

    num_friant = sum(is_friant.values())
    shares_updated = {d: 1 / num_friant if is_friant[d] else 0.0 for d in scenario['ownership_shares']}

    for i, k in enumerate(scenario['ownership_shares'].keys()):
      scenario['ownership_shares'][k] = shares_updated[k]

    with open(results_folder + '/FKC_scenario.json', 'w') as o:
      json.dump(scenario, o)

    scenario = json.load(open('calfews_src/scenarios/CFWB_properties__large_all.json'))
    scenario['participant_list'] = []
    scenario['ownership'] = {}
    scenario['bank_cap'] = {}
    scenario['initial_recharge'] = 0.0
    scenario['tot_storage'] = 0.0
    scenario['recovery'] = 0.0
    with open(results_folder + '/CFWB_scenario.json', 'w') as o:
      results_folder + '/CFWB_scenario.json'
      json.dump(scenario, o)

    run_sim(results_folder, runtime_file, start_time)



  ### baseline - ownership based on friant allocations
#  results_folder = results_base + 'FKC_experiment_' + flow_input_source + '_friantHistorical'
#  start_time = datetime.now()

#  if not os.path.exists(results_folder):

#    try:
#    prep_sim('Friant', results_folder, print_log)

#    scenario = json.load(open('calfews_src/scenarios/FKC_properties__rehab_ownership_all.json'))
#    hist_deliveries = {'BDM':0, 'BLR':0, 'BVA':0, 'CWO':0, 'HML':0, 'ID4':0, 'KND':0, 'LHL':0,
#                 'RRB':0, 'SMI':0, 'THC':0, 'TJC':0, 'WKN':0, 'WRM':0, 'KCWA':0, 'COB':0,
#                 'NKN':0, 'ARV':0.136207165, 'PIX':0, 'DLE':0.134481079, 'EXE':0.017610656, 'OKW':0, 'KRT':0, 'LND':0.040607704,
#                 'LDS':0.028243958, 'LWT':0.135494501, 'PRT':0.025589446, 'SAU':0.031784396, 'SFW':0.063438028, 'SSJ':0.114883898, 'TPD':0.007703096, 'TBA':0.029784795,
#                 'TUL':0.073845762, 'COF':0.061622586, 'FRS':0.022890257, 'SOC':0, 'SOB':0, 'CCA':0, 'DLR':0, 'TLB':0,
#                 'KWD':0, 'WSL':0, 'SNL':0, 'PNC':0, 'DLP':0, 'CWC':0, 'MAD':0, 'OTL':0,
#                 'OFK':0.075812672, 'OCD':0, 'OEX':0, 'OXV':0, 'OSW':0, 'CNS':0, 'ALT':0, 'KRWA':0}

#    for i, k in enumerate(scenario['ownership_shares'].keys()):
#      scenario['ownership_shares'][k] = hist_deliveries[k]

#    with open(results_folder + '/FKC_scenario.json', 'w') as o:
#      json.dump(scenario, o)

#    scenario = json.load(open('calfews_src/scenarios/CFWB_properties__large_all.json'))
#    scenario['participant_list'] = []
#    scenario['ownership'] = {}
#    scenario['bank_cap'] = {}
#    scenario['initial_recharge'] = 0.0
#    scenario['tot_storage'] = 0.0
#    scenario['recovery'] = 0.0
#    with open(results_folder + '/CFWB_scenario.json', 'w') as o:
#      results_folder + '/CFWB_scenario.json'
#      json.dump(scenario, o)

#    run_sim(results_folder, runtime_file, start_time)



### now loop through rest of infrastructure scenarios
for s in range(start, stop):

  np.random.seed(s)

  ### first run with both FKC expansion and CFWB
  start_time = datetime.now()
  results_folder = results_base + 'FKC_experiment_' + flow_input_source + '_' + str(s) + '_FKC_CFWB'

  if not os.path.exists(results_folder):

#    try:
    prep_sim(str(s) + ', FKC + CFWB', results_folder, print_log)

    ### get prior choices for district ownership (list will be district positions with zero shares)
    with open(results_base + 'FKC_experiment_zerodistricts.txt', 'r') as f:
      count = 0
      for line in f: # read rest of lines
        if count == s:
          zerodistricts = [int(x) for x in line.split()]
        count += 1
    
    ### randomly choose new ownership fractions for FKC expansion & CFWB, plus capacity params for CFWB
    scenario = json.load(open('calfews_src/scenarios/FKC_properties__rehab_ownership_all.json'))
    ndistricts = len(scenario['ownership_shares'])
    shares = np.random.uniform(size=ndistricts)
    shares[zerodistricts] = 0.0
    shares /= shares.sum()
    for i, k in enumerate(scenario['ownership_shares'].keys()):
      scenario['ownership_shares'][k] = shares[i]
    ### save new scenario to results folder
    with open(results_folder + '/FKC_scenario.json', 'w') as o:
      json.dump(scenario, o)

    ### now do similar to choose random params for CFWB. Use same ownership fractions from FKC.
    scenario = json.load(open('calfews_src/scenarios/CFWB_properties__large_all.json'))
    removeddistricts = []
    for i, k in enumerate(scenario['ownership'].keys()):
      if shares[i] > 0.0:
        scenario['ownership'][k] = shares[i]
      else:  
        removeddistricts.append(k)
    for k in removeddistricts:
      scenario['participant_list'].remove(k)    
      del scenario['ownership'][k]
      del scenario['bank_cap'][k]
    scenario['initial_recharge'] = np.random.uniform(0.0, 600.0)
    scenario['tot_storage'] = np.random.uniform(0.0, 1.2)
    scenario['recovery'] = np.random.uniform(0.0, 0.7)
    with open(results_folder + '/CFWB_scenario.json', 'w') as o:
      json.dump(scenario, o)

    run_sim(results_folder, runtime_file, start_time)

#    except:
#      print('EXPERIMENT FAIL: ', results_folder)

  ################
  ### now rerun with only FKC expansion
  results_folder_both = results_folder
  results_folder = results_base + 'FKC_experiment_' + flow_input_source + '_' + str(s) + '_FKC'
  start_time = datetime.now()

  if not os.path.exists(results_folder):

    try:
      prep_sim(str(s) + ', FKC only', results_folder, print_log)

      shutil.copy(results_folder_both + '/FKC_scenario.json', results_folder)

      scenario = json.load(open('calfews_src/scenarios/CFWB_properties__large_all.json'))
      scenario['participant_list'] = []
      scenario['ownership'] = {}
      scenario['bank_cap'] = {}
      scenario['initial_recharge'] = 0.0
      scenario['tot_storage'] = 0.0
      scenario['recovery'] = 0.0
      with open(results_folder + '/CFWB_scenario.json', 'w') as o:
        results_folder + '/CFWB_scenario.json'
        json.dump(scenario, o)

      run_sim(results_folder, runtime_file, start_time)

    except:
      print('EXPERIMENT FAIL: ', results_folder)    

  ################
  ### now rerun with only CFWB
  results_folder = results_base + 'FKC_experiment_' + flow_input_source + '_' + str(s) + '_CFWB'
  start_time = datetime.now()

  if not os.path.exists(results_folder):
    try:
      prep_sim(str(s) + ', CFWB only', results_folder, print_log)

      shutil.copy(results_folder_both + '/CFWB_scenario.json', results_folder)

      scenario = json.load(open('calfews_src/scenarios/FKC_properties__rehab_ownership_all.json'))
      for i, k in enumerate(scenario['ownership_shares'].keys()):
        scenario['ownership_shares'][k] = 0.0
      with open(results_folder + '/FKC_scenario.json', 'w') as o:
        json.dump(scenario, o)

      run_sim(results_folder, runtime_file, start_time)
    except:
      print('EXPERIMENT FAIL: ', results_folder)







