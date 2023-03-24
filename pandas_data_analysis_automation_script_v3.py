from turtle import title
import numpy as np
from scipy import stats
import csv
import pandas as pd
import os
import time
import json

def automation_analysis(path, dir, experiment_list,dictionary):
    
    parent_path = os.path.join(path,dir)

    def rounding(val):
        return(round(val,2))

    for idx, expt in enumerate(experiment_list, 1):
        listings = []
        volumes = []
        if expt["P_start"] > expt["P_end"]:
            expt_type = "vent"
            # conditions is a list of P_target values and P_target limits for data analysis containing: 1) the P_start point with a slight offset of 0.01 psig (can be removed was just the legacy process for the data), 2) the P_end point with a slight offset, 3) the absolute difference between P_start and P_end as a limiting condition for correction variable used for P_start (lower limit) and P_end (upper limit), 4) the P_delay as an upper limiting condition for correction variable of P_start
            conditions = [expt["P_start"] + 0.01, expt["P_end"] +0.01, abs(expt["P_start"]-expt["P_end"]), expt["P_delay"]]
        else:
            expt_type = "fill"
            conditions = [expt["P_start"] - 0.01, expt["P_end"] -0.01, abs(expt["P_start"]-expt["P_end"]), expt["P_delay"]]
        for vol in dictionary["Volumes"]:
            results = dictionary[str(idx)][str(vol)]
            volume_listing= []
            for result in results:
                file_info = []
                file_info.append(result[1])
                volume = float(result[0])
                file_info.append(volume)
                # file_info.append(rounding((75.7-(volume-0.07)-rounding(1.05/1.14, 2))))
                volume_listing.append(file_info)
            volumes.append([volume]+np.repeat("", expt["count"]-1).tolist())
            listings.append(volume_listing)
                
        start_results=[]
        end_results=[]
        start_pressures = []
        end_pressures = []
        pressure_change_times = []
        average_pressure_change_times = []
        standard_deviation_pressure_change_times = []
        # very hack-y, but two sets of lists for averages and standard deviations, one that is just the values and another for the csv that includes empty strings for line breaks
        csv_average_pressure_change_times = []
        csv_standard_deviation_pressure_change_times = []
        collected_volume_time_results = []
        csv_volumes = []

        if expt_type == "fill":
            av_upstream_pressures = []
            sd_upstream_pressures = []

        for volume_section in listings:
            start_time_block = []
            end_time_block = []
            P_start_block = []
            P_end_block = []
            pressure_change_time_block = []

            if expt_type == "fill":
                average_upstream_pressure_point = []
                sd_upstream_pressure_point = []

            for expt_info in volume_section:
                print(f"analyzing experiment# {idx} with info in order of automation filepath analyzed and volume in L:", expt_info)
                data = pd.read_csv(expt_info[0], sep = ",")
                data["tank pressure (psig)"]=data["tank pressure (psig)"].apply(lambda x: round(x,2)) 
                data["time (s)"] = data["time (s)"].apply(lambda x: round(x,2))        
                start_point = (data[(rounding(data["tank pressure (psig)"])) == rounding(conditions[0])][:1]['time (s)']).to_numpy()
                correction = 0
                while len(start_point) == 0 and correction < conditions[3]:
                    if expt_type == "fill":
                        correction-= 0.01
                    else:
                        correction+= 0.01
                    start_point = (data[(rounding(data["tank pressure (psig)"])) == rounding(conditions[0]+correction)][:1]['time (s)']).to_numpy()
                if correction == conditions[3]: # logic to switch to checking condition[0], starting pressure, minus the correction
                    correction = 0
                    while len(start_point) == 0 and correction < conditions[2]:
                        if expt_type == "fill":
                            correction+= 0.01
                        else:
                            correction-= 0.01
                        start_point = (data[(rounding(data["tank pressure (psig)"])) == rounding(conditions[0]+correction)][:1]['time (s)']).to_numpy()
                    if correction == conditions[2]:
                        raise Exception('Start pressure not found. Recheck your data analysis parameters and experiment data')
                start_pressure = (data[(rounding(data["tank pressure (psig)"])) == rounding(conditions[0]+correction)][:1]['tank pressure (psig)']).to_numpy()

                start_time_block.append(rounding(start_point[0]))
                P_start_block.append(start_pressure[0])
                end_point = (data[(rounding(data["tank pressure (psig)"])) == rounding(conditions[1])][:1]['time (s)']).to_numpy()
                correction = 0
                while len(end_point) == 0 and correction < conditions[2]:
                    if expt_type == "fill":
                        correction -= 0.01
                    else:
                        correction += 0.01
                    end_point = (data[(rounding(data["tank pressure (psig)"])) == rounding(conditions[1]+correction)][:1]['time (s)']).to_numpy()

                if correction == conditions[2]: # logic to switch to checking condition[0], starting pressure, minus the correction
                    correction = 0
                    while len(end_point) == 0 and correction < 0.2: # lower limit set only to 0.2 psig, an arbitrary lower limit as the data collection should have stopped not too much lower than from P_end
                        if expt_type == "fill":
                            correction += 0.01
                        else:
                            correction -= 0.01
                        end_point = (data[(rounding(data["tank pressure (psig)"])) == rounding(conditions[0]+correction)][:1]['time (s)']).to_numpy()
                    if correction == 0.2:
                        raise Exception('End pressure not found. Recheck your data analysis parameters and experiment data')
                end_pressure = (data[(rounding(data["tank pressure (psig)"])) == rounding(conditions[1]+correction)][:1]['tank pressure (psig)']).to_numpy()
                end_time_block.append(rounding(end_point[0]))
                P_end_block.append(end_pressure[0])
                pressure_change_time_block.append(rounding(end_point[0]-start_point[0]))
                collected_volume_time_results.append([expt_info[1], rounding(end_point[0]-start_point[0])])

                if expt_type == "fill":
                    data = data[(data["tank pressure (psig)"] >= start_pressure[0]) & (data["tank pressure (psig)"] <= end_pressure[0])]
                    average_upstream_pressure_point.append(rounding(data["upstream pressure (psig)"].mean()))
                    sd_upstream_pressure_point.append(rounding(data["upstream pressure (psig)"].std()))
             
            start_results.append(start_time_block)
            end_results.append(end_time_block)
            start_pressures.append(P_start_block)
            end_pressures.append(P_end_block)
            pressure_change_times.append(pressure_change_time_block)

            average_pressure_change_times.append(sum(pressure_change_time_block)/len(pressure_change_time_block))
            csv_average_pressure_change_times.append([rounding(sum(pressure_change_time_block)/len(pressure_change_time_block))]+np.repeat("",expt["count"]-1).tolist())
            
            standard_deviation_pressure_change_times.append(np.std(pressure_change_time_block, ddof=1).tolist())
            csv_standard_deviation_pressure_change_times.append([rounding(np.std(pressure_change_time_block, ddof=1).tolist())]+np.repeat("",expt["count"]-1).tolist())
            
            csv_volumes.append([expt_info[1]]+np.repeat("",expt["count"]-1).tolist())
            
            if expt_type == "fill":
                av_upstream_pressures.append(average_upstream_pressure_point)
                sd_upstream_pressures.append(sd_upstream_pressure_point)

        time_array = np.array(average_pressure_change_times, dtype=np.float64)
        vol_array = np.array(dictionary["Volumes"], dtype=np.float64)
        time_volume_calibration = stats.linregress(time_array, vol_array)
        def calculated_volume(xval):
            return(time_volume_calibration.slope*xval + time_volume_calibration.intercept)
        calc_volumes = [(calculated_volume(x[1])) for x in collected_volume_time_results]
        abs_errors = [(abs(calc_volumes[x]-collected_volume_time_results[x][0])) for x in range(0,len(collected_volume_time_results))]
        abs_errors_squared = [(x**2) for x in abs_errors]

        csv_standard_deviation_volumes = []
        for block in csv_standard_deviation_pressure_change_times:
            volume_block = []
            for sd in block:
                if sd == '':
                    volume_block.append(sd)
                else:
                    volume_block.append(rounding(sd*-time_volume_calibration.slope))
            csv_standard_deviation_volumes.append(volume_block)

        local_rmsds = []
        local_rmsds_block = []
        summation = 0
        for val_index,val in enumerate(abs_errors_squared,1):
            if (val_index % expt["count"]== 0):
                summation += val
                local_rmsds_block.insert(0, rounding((summation/(expt["count"]-1))**0.5))
                local_rmsds.append(local_rmsds_block)
                local_rmsds_block = []
                summation=0
            else:
                local_rmsds_block.append("")
                summation += val

        global_rmsd = [rounding((sum(abs_errors_squared)/(len(abs_errors_squared)-1))**0.5)] +np.repeat("",len(abs_errors_squared)-1).tolist()

        slope = [rounding(time_volume_calibration.slope)] +np.repeat("",len(abs_errors_squared)-1).tolist()
        intercept = [rounding(time_volume_calibration.intercept)] +np.repeat("",len(abs_errors_squared)-1).tolist()


        df_list = []
        if expt_type == "vent":
            units_dataframe = {"files": ["name"],"tank fill volume": ["L"], "P_start": ["psig"], "P_end": ["psig"], "start time": ["s"], "end time": ["s"], "pressure change time": ["s"], "volume": ["L"], "average pressure change time": ["s"], "std. dev. change time": ["s"], "std. dev. volume" : ["L"], "calculated volume": ["L"], "absolute error": ["L"], "absolute error^2": ["L^2"], "Tank Fill Volume": ["L"], "local RMSD": ["L"], "global RMSD": ["L"], "slope": ["L/s"], "intercept": ["L"]}
        else:
            units_dataframe = {"files": ["name"],"tank fill volume": ["L"], "P_start": ["psig"], "P_end": ["psig"], "ave. upstream pressure": ["psig"], "st. dev. upstream pressure": ["psig"],"start time": ["s"], "end time": ["s"], "pressure change time": ["s"], "volume": ["L"], "average pressure change time": ["s"], "std. dev. change time": ["s"], "std. dev. volume" : ["L"], "calculated volume": ["L"], "absolute error": ["L"], "absolute error^2": ["L^2"], "Tank Fill Volume": ["L"], "local RMSD": ["L"], "global RMSD": ["L"], "slope": ["L/s"], "intercept": ["L"]}
        df_list.append(pd.DataFrame(data=units_dataframe))
        total_index = 0
        for entry_num, volume_section in enumerate(listings,0):
            for expt_num, expt_info in enumerate(volume_section, 0):
                if expt_type == "vent":
                    inputs = {"files": expt_info[0], "tank fill volume": expt_info[1], "P_start": start_pressures[entry_num][expt_num], "P_end": end_pressures[entry_num][expt_num], "start time": start_results[entry_num][expt_num], "end time": end_results[entry_num][expt_num], "pressure change time": pressure_change_times[entry_num][expt_num], "volume": volumes[entry_num][expt_num], "calculated volume": calc_volumes[total_index], "absolute error": abs_errors[total_index], "absolute error^2": abs_errors_squared[total_index],  "average pressure change time": csv_average_pressure_change_times[entry_num][expt_num], "std. dev. change time": csv_standard_deviation_pressure_change_times[entry_num][expt_num], "std. dev. volume" : csv_standard_deviation_volumes[entry_num][expt_num], "Tank Fill Volume": volumes[entry_num][expt_num], "local RMSD": local_rmsds[entry_num][expt_num], "global RMSD": global_rmsd[total_index], "slope": slope[total_index], "intercept": intercept[total_index]}  
                else:
                    inputs = {"files": expt_info[0], "tank fill volume": expt_info[1], "P_start": start_pressures[entry_num][expt_num], "P_end": end_pressures[entry_num][expt_num], "ave. upstream pressure": av_upstream_pressures[entry_num][expt_num], "st. dev. upstream pressure": sd_upstream_pressures[entry_num][expt_num],"start time": start_results[entry_num][expt_num], "end time": end_results[entry_num][expt_num], "pressure change time": pressure_change_times[entry_num][expt_num], "volume": volumes[entry_num][expt_num], "calculated volume": calc_volumes[total_index], "absolute error": abs_errors[total_index], "absolute error^2": abs_errors_squared[total_index],  "average pressure change time": csv_average_pressure_change_times[entry_num][expt_num], "std. dev. change time": csv_standard_deviation_pressure_change_times[entry_num][expt_num], "std. dev. volume" : csv_standard_deviation_volumes[entry_num][expt_num], "Tank Fill Volume": volumes[entry_num][expt_num], "local RMSD": local_rmsds[entry_num][expt_num], "global RMSD": global_rmsd[total_index], "slope": slope[total_index], "intercept": intercept[total_index]}                
                df = pd.DataFrame(data= [inputs])
                df_list.append(df)
                total_index+=1
        
        df = pd.concat(df_list)

        df.to_csv(f"{parent_path}/{dir} USB-TEMP-AI Python analysis try#2 experiment#{idx}.csv", index=False) 
