# updates: significant changes to the results_dict entry method and calculating averages, calculated volume from pressure change time, and absolute errors
from experiment_sequence_v3 import expt_run # updates: remove the incorrect method of estimating calculated volume and absolute error using a previous curve from 25 to 24 psi vent with 1 psi delay
# from tank_water_sequence_v2 import tank_water_sequence # updates: adjusted volume and pressure cutoffs and updated solenoid functions to be less wordy
from tank_water_sequence_depressurized_version import tank_water_sequence # new program in which the tank pressure is set to 0 to 0.5 psig before taking a volume measurement
from pandas_data_analysis_automation_script_v3 import automation_analysis # updates: file selection and volume entries using the results_dict instead of the "* measurements.csv" file # v3 updates: added statistics calculating average/SD pressure change time and local RMSD for a volume
from pandas_data_analysis_graphtec_script_post_auto_v2 import graphtec_analysis # updates: start/end timestamps, file selection, and volume entries using the results_dict instead of the "* measurements.csv" file

import os
import json

volume_list = [0, 10, 30, 50, 70, 0]
expt_list = [
{"P_start": 20, "P_end": 21, "P_delay": 1, "count": 6, "pre": 60, "post": 0, "P_offset": 0.5, "supply_transducer_range": 30, "tank_transducer_range": 30, "volumes": volume_list},
{"P_start": 20, "P_end": 23, "P_delay": 1, "count": 6, "pre": 60, "post": 0, "P_offset": 0.5, "supply_transducer_range": 30, "tank_transducer_range": 30, "volumes": volume_list},
{"P_start": 23, "P_end": 24, "P_delay": 1, "count": 6, "pre": 60, "post": 0, "P_offset": 0.5, "supply_transducer_range": 30, "tank_transducer_range": 30, "volumes": volume_list}
    ]

# expt_list_template_vent = [{"P_start": 25, "P_end": 24, "P_delay": 1, "count": 6, "pre": 60, "post": 0, "P_offset": 0.35, "tank_transducer_range": 30, "volumes": volume_list}]

# expt_list_template_fill = [{"P_start": 20, "P_end": 21, "P_delay": 1, "count": 6, "pre": 60, "post": 0, "P_offset": 0.5, "supply_transducer_range": 100, "tank_transducer_range": 30, "volumes": volume_list}]

true_vol_list = []
root_path = "C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/"

parent_directory = input("Input name of the parent directory for this experiment: ")
run_type = input("Are you running the experiments? Input yes/Yes/y/Y if you are or no/No/n/N if you are processing graphtec data after the experiment: ")

if run_type[0].lower() == "y":
    # initializes as "no" for the interruption variable (checking if the experiment was interrupted and needs to run off of the backup records) and the override variable (checks whether or not to run the experiment or just analyze the data as-is)
    interruption = "n"
    override = "n"
    interruption = input("Was this sequence interrupted? Input yes/Yes/y/Y if it was or no/No/n/N if it wasn't: ")


    parent_path = os.path.join(root_path, parent_directory) # creates address for folder using root_path and your entry for parent_directory
    isExist = os.path.exists(parent_path) # checks if folder exists (True or False output)
    if not isExist:
        os.mkdir(parent_path) # creates folder if doesn't exist
    
    def file_search(string, path):
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if string in name:
                    result.append(os.path.join(root, name))
        return result

    if interruption[0].lower() == "y": 
        file = (file_search("data dictionary", parent_path)[0])
        with open(file, 'r') as convert_file:
            results_dict = json.loads(convert_file.read())

        params_file = (file_search("parameters", parent_path)[0])
        with open(params_file, 'r') as params_txt:
            expt_list = json.loads((params_txt.read()))
        
        override = input("Skip experiment and just run automation_analysis script? Input yes/Yes/y/Y for yes or no/No/n/N for no: ")
    else:
        results_dict = {'Volumes': []} # record of data, timestamps, and volumes ran for experiments; used in analysis scripts


    with open(f"{parent_path}/{parent_directory} experiment parameters.txt", 'w') as convert_file:
        convert_file.write(json.dumps(expt_list)) # converts expt_list to txt file for records and analysis

    if override[0].lower() == "n":
        for vol in volume_list: # iterate over each volume in volume_list
            true_vol = tank_water_sequence(vol, expt_list[0]) # assigns to true_vol variable what the scale reading is after reaching the preset volume using tank_water_sequence 
            vol_path = os.path.join(parent_path, str(true_vol))
            isExist = os.path.exists(vol_path)
            if not isExist:
                os.mkdir(vol_path)

            for idx, expt in enumerate(expt_list,1):
                file_path = os.path.join(vol_path, str(idx))
                isExist = os.path.exists(file_path)
                if not isExist:
                    os.mkdir(file_path)
                if str(idx) not in results_dict:
                    results_dict[str(idx)] = {}
                addition = 0 # this addition unit is a means of adding a miniscule value to the true_vol soley for the purpose of results_dict entry in the case of running multiple volume steps with the same true volume; 
                #  otherwise, you end up putting in two datasets into 1 dictionary entry, which is not as easy to separate out data in an unsorted array instead of ensuring that they aren't put together in the first place
                while str(true_vol+addition) in results_dict[str(idx)]:
                    addition += 0.00001
                if str(true_vol+addition) not in results_dict[str(idx)]:
                    results_dict[str(idx)][str(true_vol+addition)] = []
                print(f"running experiment # {str(idx)} at volume {true_vol} L")
                vol_results = expt_run(expt, file_path, true_vol)
                # vol_results is a list of length 1 containing a list of length x, where x equals expt["count"], containing a list of length 9, therefore we add vol_results[0] to the dictonary to access the data lists within the list
                for result in vol_results:
                    results_dict[str(idx)][str(true_vol+addition)].append(result)
            true_vol_list.append(str(true_vol+addition)) # list used to find the results_dict "true_vol + addition" entries of interest in the data entry for loop in line 93
            results_dict["Volumes"] = true_vol_list
            print(results_dict)
            with open(f"{parent_path}/{parent_directory} data dictionary.txt", 'w') as convert_file:
                convert_file.write(json.dumps(results_dict))
    print("run complete")
    print(results_dict)


#####
    # # NOTE: avoid this if possible, but this block of code is for merging 2 results_dicts together in case the Python sequence was interrupted and broken up into 2 backup files
    # # copies result_dicts from the raw text files declare them as variables and add them to the test_list list below
    # test_list = []
    # res = dict()
    # for dict in test_list:
    #     for list in dict:
    #         if list in res:
    #             res[list] += (dict[list])
    #         else:
    #             res[list] = dict[list]
    # results_dict = res
    # print(results_dict)
#####

    # converts each volume string into a float; the reason these volumes were strings to start with is to allow for Python to export these entries into a txt file (doesn't work for floats)
    for vol in results_dict["Volumes"]:
        vol = float(vol)

    automation_analysis(root_path, parent_directory, (expt_list),results_dict)

else:
    parent_path = os.path.join(root_path, parent_directory)

    # function for searching for the "data dictionary" and "parameters" txt files written for the experiment and setting it to results_dict and expt_list for graphtec_analysis
    def file_search(string, path):
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if string in name:
                    result.append(os.path.join(root, name))
        return result
    results_file = (file_search("data dictionary", parent_path)[0])

    with open(results_file, 'r') as results_txt:
        results_dict = json.loads(results_txt.read())

    params_file = (file_search("parameters", parent_path)[0])

    with open(params_file, 'r') as params_txt:
        expt_list = json.loads((params_txt.read()))

        
    # NOTE: this graphtec analysis fails if you have broken up your experiment between multiple graphtec .csv files so avoid this situation if possible.
    # If unavoidable, then you will need to break up your expt_list and results_dict into parts corresponding to the graphtec program,
    # run these parts in place of the expt_list and results_dict parameters below
    
    # regex matches the YYMMDD-HHMMSS format of the Graphtec file
    # files = file_search("Mar", parent_path)

    

    graphtec_analysis(root_path, parent_directory, (expt_list),results_dict)

