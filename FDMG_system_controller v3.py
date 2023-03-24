import time
# updates: significant changes to the results_dict entry method and calculating averages, calculated volume from pressure change time, and absolute errors
from experiment_sequence_v3 import expt_run # updates: remove the incorrect method of estimating calculated volume and absolute error using a previous curve from 25 to 24 psi vent with 1 psi delay
from tank_water_sequence_v2 import tank_water_sequence # updates: adjusted volume and pressure cutoffs and updated solenoid functions to be less wordy
from pandas_data_analysis_automation_script_v3 import automation_analysis # updates: file selection and volume entries using the results_dict instead of the "* measurements.csv" file # v3 updates: added statistics calculating average/SD pressure change time and local RMSD for a volume
from pandas_data_analysis_graphtec_script_post_auto_v2 import graphtec_analysis # updates: start/end timestamps, file selection, and volume entries using the results_dict instead of the "* measurements.csv" file

from mcculw import ul
from mcculw.enums import DigitalIODirection
from mcculw.enums import (ULRange, DigitalPortType, InterfaceType, TempScale)
import serial
import os
import json
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd
import re


volume_list = [0.05, 10, 30, 50, 70, 0.050010000000000006]
expt_list = [
    {"P_start": 20, "P_end": 21, "P_delay": 1, "count": 6, "pre": 60, "post": 0, "P_offset": 0.35, "fill_transducer_range": 100, "tank_transducer_range": 30,"volumes": volume_list},
    {"P_start": 23, "P_end": 24, "P_delay": 1, "count": 6, "pre": 60, "post": 0, "P_offset": 0.35, "fill_transducer_range": 100, "tank_transducer_range": 30, "volumes": volume_list}
    ]

true_vol_list = []
root_path = "C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/"


parent_directory = input("Input name of the parent directory for this experiment: ")
run_type = input("Are you running the experiments? Input yes/Yes/y/Y if you are or no/No/n/N if you are processing graphtec data after the experiment: ")

if run_type[0].lower() == "y":
    parent_path = os.path.join(root_path, parent_directory)
    isExist = os.path.exists(parent_path)
    if not isExist:
        os.mkdir(parent_path)
    results_dict = {'Volumes': ['0.05'], '1': {'0.05': [['0.05', 'C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/fill expt choked flow high pressure 03-22-23\\0.05\\1/Wed Mar 22 13-09-30 2023.csv', '2023-03-22 13:10:30.789606', '2023-03-22 13:14:11.008915', '111.152455', '19.990487694740295', '218.033555', '20.9808486700058', '106.8811'], ['0.05', 'C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/fill expt choked flow high pressure 03-22-23\\0.05\\1/Wed Mar 22 13-14-11 2023.csv', '2023-03-22 13:15:49.756315', '2023-03-22 13:18:44.652540', '69.002052', '19.992615580558777', '173.259199', '20.997523069381714', '104.25714699999999'], ['0.05', 'C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/fill expt choked flow high pressure 03-22-23\\0.05\\1/Wed Mar 22 13-18-44 2023.csv', '2023-03-22 13:20:23.401149', '2023-03-22 13:23:18.355795', '69.052677', '19.98892843723297', '173.860668', '20.996580719947815', '104.807991'], ['0.05', 'C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/fill expt choked flow high pressure 03-22-23\\0.05\\1/Wed Mar 22 13-23-18 2023.csv', '2023-03-22 13:24:57.075205', '2023-03-22 13:27:51.489857', '68.495822', '19.99166250228882', '173.324692', '20.999963879585266', '104.82887'], ['0.05', 'C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/fill expt choked flow high pressure 03-22-23\\0.05\\1/Wed Mar 22 13-27-51 2023.csv', '2023-03-22 13:29:30.708283', '2023-03-22 13:32:28.266069', '70.625101', '19.991683959960938', '175.917806', '20.998857021331787', '105.29270500000001'], ['0.05', 'C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/fill expt choked flow high pressure 03-22-23\\0.05\\1/Wed Mar 22 13-32-28 2023.csv', '2023-03-22 13:34:07.018744', '2023-03-22 13:37:02.493621', '68.50009', '19.990174770355225', '171.185108', '20.97887635231018', '102.68501800000001']]}, '2': {'0.05': [['0.05', 'C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/fill expt choked flow high pressure 03-22-23\\0.05\\2/Wed Mar 22 13-37-02 2023.csv', '2023-03-22 13:39:05.709918', '2023-03-22 13:43:27.221534', '149.325748', '22.988855838775635', '259.330603', '23.993375301361084', '110.00485499999999'], ['0.05', 'C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/fill expt choked flow high pressure 03-22-23\\0.05\\2/Wed Mar 22 13-43-27 2023.csv', '2023-03-22 13:45:02.305114', '2023-03-22 13:47:55.660216', '65.338546', '22.97782301902771', '170.152367', '23.999236822128296', '104.813821'], ['0.05', 'C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/fill expt choked flow high pressure 03-22-23\\0.05\\2/Wed Mar 22 13-47-55 2023.csv', '2023-03-22 13:49:30.727436', '2023-03-22 13:52:23.055210', '64.832023', '22.978835105895996', '169.664176', '23.994240760803223', '104.83215299999999'], ['0.05', 'C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/fill expt choked flow high pressure 03-22-23\\0.05\\2/Wed Mar 22 13-52-23 2023.csv', '2023-03-22 13:53:58.140024', '2023-03-22 13:56:51.550598', '66.461637', '22.979975938796997', '170.203674', '23.993289470672607', '103.74203700000001'], ['0.05', 'C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/fill expt choked flow high pressure 03-22-23\\0.05\\2/Wed Mar 22 13-56-51 2023.csv', '2023-03-22 13:58:26.629234', '2023-03-22 14:01:19.989428', '66.411634', '22.981499433517456', '170.157479', '23.989638090133667', '103.74584499999999'], ['0.05', 'C:/Users/jabdou/Desktop/FDMGAutomation/Experiment-results/fill expt choked flow high pressure 03-22-23\\0.05\\2/Wed Mar 22 14-01-20 2023.csv', '2023-03-22 14:02:55.059444', '2023-03-22 14:05:48.519706', '66.959469', '22.99716353416443', '170.257479', '23.991830348968506', '103.29800999999999']]}}


    with open(f"{parent_path}/{parent_directory} experiment parameters.txt", 'w') as convert_file:
        convert_file.write(json.dumps(expt_list))


    for vol in volume_list:
        true_vol = tank_water_sequence(vol, expt_list[0])
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
            #  otherwise, you end up with an expanded array of results in the dictionary with a higher length than the expt_count, which cannot be easily parsed in the later analysis programs. Do note that the actual true_vol remains unchanged and is still used as-is in the expt_run step in line 
            while str(true_vol+addition) in results_dict[str(idx)]:
                addition += 0.00001
            if str(true_vol+addition) not in results_dict[str(idx)]:
                results_dict[str(idx)][str(true_vol+addition)] = []
            print(f"running experiment # {str(idx)} at volume {true_vol} L")
            vol_results = expt_run(expt, file_path, true_vol)
            # vol_results = expt_run(expt["P_start"], expt["P_end"], expt["P_delay"], expt["count"], file_path, true_vol, expt["pre"], expt["post"], expt["offset"])
            # vol_results is a list of length 1 containing a list of length x, where x equals expt["count"], containing a list of length 9, therefore we add vol_results[0] to the dictonary to access the data lists within the list
            results_dict[str(idx)][str(true_vol+addition)] = vol_results
        true_vol_list.append(str(true_vol+addition)) # list used to find the results_dict "true_vol + addition" entries of interest in the data entry for loop in line 93
        results_dict["Volumes"] = true_vol_list
        with open(f"{parent_path}/{parent_directory} data dictionary.txt", 'w') as convert_file:
            convert_file.write(json.dumps(results_dict))
    print("run complete")
    print(results_dict)
    print(true_vol_list)

    # block of code to read data dictionary from file in case experiment was interrupted
    # def file_search(string, path):
    #     result = []
    #     for root, dirs, files in os.walk(path):
    #         for name in files:
    #             if string in name:
    #                 result.append(os.path.join(root, name))
    #     return result
    # file = (file_search("data dictionary", parent_path)[0])

    # with open(file, 'r') as convert_file:
    #     results_dict = json.loads(convert_file.read())

    # params_file = (file_search("parameters", parent_path)[0])

    # with open(params_file, 'r') as params_txt:
    #     expt_list = json.loads((params_txt.read()))


    # block of code for merging list of results_dicts in case the python program was interrupted; copy result_dicts from the raw text files declare them as variables and add them to the test_list list below
    # test_list = []
    # res = dict()
    # for dict in test_list:
    #     for list in dict:
    #         if list in res:
    #             res[list] += (dict[list])
    #         else:
    #             res[list] = dict[list]
    # results_dict = res

    for vol in results_dict["Volumes"]:
        vol = float(vol)

    with open((f'{parent_path}/{parent_directory} USB-TEMP-AI Python data collection and analysis collected measurements.csv') ,  'w') as csv_file:
        header =['Experiment #','Volume (L)', 'file_path', 'experiment start datetime', 'experiment end datetime','start time (s)', 'start pressure (psig)', 'end time (s)', 'end pressure (psig)', 'pressure change time (s)']
        csv_file.write(','.join(header) + '\n')
        collected_data_dictionary = {}
        statistics_dictionary = {}
        true_vol_list = results_dict["Volumes"]
        for idx, expt in enumerate(expt_list,1): # setting indexing to 1 to prevent complaints
            collected_data_dictionary[str(idx)] = {}
            statistics_dictionary[str(idx)]= {}
            statistics_dictionary[str(idx)]["average_abs_error"] = 0
            statistics_dictionary[str(idx)]["global_rmsd"] = 0
            statistics_dictionary[str(idx)]["local_rmsds"] = []
            statistics_dictionary[str(idx)]["absolute_errors"] = []
            statistics_dictionary[str(idx)]["absolute_errors_squared"] = []
            statistics_dictionary[str(idx)]["calculated_volumes"] = []
            statistics_dictionary[str(idx)]["average_pressure_change_times"] = []
            statistics_dictionary[str(idx)]["standard_deviation_pressure_change_times"] = []
            statistics_dictionary[str(idx)]["standard_deviation_volumes"] = []
            statistics_dictionary[str(idx)]["slope"] = []
            statistics_dictionary[str(idx)]["intercept"] = []
            collected_data_dictionary[str(idx)]["volume_time_results_in_volume_bins"] = []
            collected_data_dictionary[str(idx)]["volume_time_results_list"] = []
            for vol in true_vol_list:
                results = results_dict[str(idx)][str(vol)]
                volume_time_result_list = []
                time_list = []
                for entry in results:
                    time_list.append(float(entry[-4]))
                    volume_time_result_list.append([float(entry[0]),float(entry[-4])])
                    collected_data_dictionary[str(idx)]["volume_time_results_list"].append([float(entry[0]),float(entry[-4])])
                    entry.insert(0, str(idx))
                    csv_file.write(','.join(entry) + '\n')
                    entry.pop(0)
                collected_data_dictionary[str(idx)]["volume_time_results_in_volume_bins"].append(volume_time_result_list)
                average_change_time = sum(time_list)/len(time_list)
                statistics_dictionary[str(idx)]["average_pressure_change_times"].append(average_change_time)
                standard_deviation_change_time = np.std(time_list, ddof=1)
                statistics_dictionary[str(idx)]["standard_deviation_pressure_change_times"].append(standard_deviation_change_time)
                csv_file.write(",".join(["","","","","","average change time (s)", str(average_change_time), "standard deviation (s)",str(standard_deviation_change_time)]) + "\n")
            time_array = np.array(statistics_dictionary[str(idx)]["average_pressure_change_times"], dtype=np.float64)
            vol_array = np.array(results_dict["Volumes"], dtype=np.float64)
            time_volume_calibration = stats.linregress(time_array, vol_array)
            time_volume_calibration_linear_fit_string = f"{str(round(time_volume_calibration.slope,4))}*x +  {str(round(time_volume_calibration.intercept,4))}"
            def calculated_volume(xval):
                return(time_volume_calibration.slope*xval + time_volume_calibration.intercept)
            calc_volumes = [calculated_volume(x[1]) for x in collected_data_dictionary[str(idx)]["volume_time_results_list"]]
            collected_abs_errors = [abs(calc_volumes[x]-collected_data_dictionary[str(idx)]["volume_time_results_list"][x][0]) for x in range(0,len(calc_volumes))]
            collected_abs_errors_squared = [x**2 for x in collected_abs_errors]
            statistics_dictionary[str(idx)]["average_abs_error"] = [sum(collected_abs_errors)/len(collected_abs_errors)]
            statistics_dictionary[str(idx)]["global_rmsd"] = [(sum(collected_abs_errors_squared) ** 0.5)/(len(collected_abs_errors_squared)-1)]
            statistics_dictionary[str(idx)]["slope"] = [time_volume_calibration.slope]
            statistics_dictionary[str(idx)]["intercept"] = [time_volume_calibration.intercept]

            for bin in collected_data_dictionary[str(idx)]["volume_time_results_in_volume_bins"]:
                calc_volumes = [calculated_volume(x[1]) for x in bin]
                local_abs_errors = [abs(calc_volumes[x]-bin[x][0]) for x in range(0,len(bin))]
                local_abs_errors_squared = [x**2 for x in local_abs_errors]
                rmsd = (sum(local_abs_errors_squared) ** 0.5)/(len(local_abs_errors_squared)-1)
                [statistics_dictionary[str(idx)]["calculated_volumes"].append(x) for x in calc_volumes]
                statistics_dictionary[str(idx)]["local_rmsds"].append(rmsd)
                [statistics_dictionary[str(idx)]["absolute_errors"].append(x) for x in local_abs_errors]
                [statistics_dictionary[str(idx)]["absolute_errors_squared"].append(x) for x in local_abs_errors_squared]

            csv_file.write(",".join(["","","","","","average absolute error (L)", str(statistics_dictionary[str(idx)]["average_abs_error"][0]), "global RMSD (L)",str(statistics_dictionary[str(idx)]["global_rmsd"][0]), "slope", str(statistics_dictionary[str(idx)]["slope"][0]), "intercept", str(statistics_dictionary[str(idx)]["intercept"][0])  + "\n"]))
        csv_file.write(",".join(["","","","","","experiment run #","P_start", "P_end", "P_delay", "count", "pre-experiment delay time", "post-experiment delay time", "offset psi"])+ "\n")

        for idx, expt in enumerate(expt_list,0):
            csv_file.write(",".join(["","","","","",f"experiment run #{idx +1}",str(expt["P_start"]), str(expt["P_end"]), str(expt["P_delay"]), str(expt["count"]), str(expt["pre"]), str(expt["post"]), str(expt["P_offset"])])+ "\n")
    
    for idx, expt in enumerate(expt_list,1):
        with open((f'{parent_path}/{parent_directory} USB-TEMP-AI Python data collection and analysis experiment#{idx}.csv') ,  'w') as csv_file:
            csv_file.write(",".join(["Measured Volume","files", "start time", "P_start", "end time", "P_end", "pressure change time", "calculated volume", "absolute error", "absolute error^2",  "volume", "average pressure change time", "std. dev. change time", "SD change time converted to volume", "local RMSD", "global RMSD", "slope", "intercept"]) + "\n")
            csv_file.write(",".join(["L","name", "s","psig", "s", "psig",   "s", "L", "L", "L^2",  "L", "s", "s", "L", "L", "L", "L/s", "L"]) + "\n")
            for num, line in enumerate(collected_data_dictionary[str(idx)]["volume_time_results_list"], 0):
                calculated_index = num % expt["count"]
                line_entry = [*results_dict[str(idx)][str(line[0])][num % expt["count"]][0:2], *results_dict[str(idx)][str(line[0])][num % expt["count"]][4:9], str(statistics_dictionary[str(idx)]["calculated_volumes"][num]), str(statistics_dictionary[str(idx)]["absolute_errors"][num]), str(statistics_dictionary[str(idx)]["absolute_errors_squared"][num])]
                if num % expt["count"] == 0:
                    index = num//expt["count"]
                    sdev = statistics_dictionary[str(idx)]["standard_deviation_pressure_change_times"][index]
                    items = [true_vol_list[index], statistics_dictionary[str(idx)]["average_pressure_change_times"][index], sdev, (sdev*abs(statistics_dictionary[str(idx)]["slope"][0])), statistics_dictionary[str(idx)]["local_rmsds"][index]]
                    for item in items:
                        line_entry.append(str(item))
                if num == 0:
                    line_entry.append(str(statistics_dictionary[str(idx)]["global_rmsd"][0]))
                    line_entry.append(str(statistics_dictionary[str(idx)]["slope"][0]))
                    line_entry.append(str(statistics_dictionary[str(idx)]["intercept"][0]))
                csv_file.write(",".join(line_entry) + "\n")

      

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
    
    graphtec_analysis(root_path, parent_directory, (expt_list),results_dict)
