from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport
import os
# os.chdir('C:\\Users\\jabdou\\Downloads\\examples\\ui')
import time
import serial
import datetime
import struct


import tkinter as tk
from tkinter import IntVar

from mcculw import ul
from mcculw.enums import DigitalIODirection
from mcculw.enums import (ULRange, DigitalPortType, InterfaceType, TempScale)
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

# params is the Python dictionary with the parameters used to control the experiment
# params["P_start"] is the pressure at which the pressure change measurements is started (time start during the vent for pressure change time)
# params["P_end"] is the pressure at which the pressure change measurements is ended (time end during the vent for pressure change time); this point is also at which the vent experiment is concluded
# params["P_delay"] is the pressure delay added before the P_start at which the vent experiment and data collection begins (t = 0 for the experiment and measurements is when the the tank pressure is at params["P_start"] + params["P_delay"])
# params["count"] is the number of replicates that the experiment is repeated for the given params["P_start"], params["P_end"], and params["P_delay"] 
# folder_path is where the raw experiment run data is saved
# volume is the recorded volume on the scale at the start of the expt_run program
# params["pre"] is the time the tank is left idle at params["P_start"] + params["P_delay"]
# params["post"] is the time the tank is left idle at params["P_end"]
# params["P_offset"] is the pressure offset on top of params["P_start"] + params["P_delay"], if any. This is used to account for the pressure change due to the equilibration tank temperature after adiabatic expansion during the filling/venting to reach params["P_start"]+params["P_delay"]

def expt_run(params, folder_path, volume):

    def check_params(key_string):
        if key_string not in params:
            raise Exception(f'{key_string} key is not in the experiment dictionary. Check the expt_list in the FDMG_system_controller program')

    expt_type = ""
    check_params("P_start")
    check_params("P_end")
    check_params("P_offset")
    check_params("P_delay")
    check_params("tank_transducer_range")
    check_params("count")
    check_params("pre")
    check_params("post")
    if params["P_start"] == params["P_end"]:
        raise Exception("P_start and P_end must be different values")
    
    
    add_delay = 0.05 + params["P_offset"] # add_delay is for the window of pressures the tank is set at around params["P_start"] + params["P_delay"] to avoid an infinite loop of venting and filling to reach a single point pressure target

    
    if params["P_start"] > params["P_end"]:
        expt_type = "vent"
        P_init_range = [params["P_start"] + params["P_delay"] + params["P_offset"], params["P_start"] + params["P_delay"]+add_delay]
    else:
        expt_type = "fill"
        check_params("supply_transducer_range")
        P_init_range = [params["P_start"] - params["P_delay"]-add_delay, params["P_start"] - params["P_delay"]-params["P_offset"]]

        
    def pressure_temperature_measurement_logging(setting, start_sequence,timelog, expt_type):
        board_num = 1 # board_num corresponding to the USB-TEMP-AI set up in Instacal
        ai_range = ULRange.BIP5VOLTS
        first_channel = 0
        second_channel = 1
        value = ul.v_in(board_num, first_channel, ai_range)
        temperature = ul.t_in(board_num, first_channel, TempScale.KELVIN)
        temperature2 = ul.t_in(board_num, second_channel, TempScale.KELVIN)
        
        if expt_type == "fill":
            value2 = ul.v_in(board_num, second_channel, ai_range)
            
            # conversion formula to calculate pressure (psig) from pressure transducer voltage (V)
            # NOTE: BE SURE TO CHANGE THIS FORMULA IF USING A DIFFERENT TRANSDUCER
            transducer_conversion_factor_1= params["tank_transducer_range"] *7.5/30
            transducer_conversion_factor_2= params["supply_transducer_range"] *7.5/30
            result = (value*transducer_conversion_factor_1)-transducer_conversion_factor_1
            result2 = (value2*transducer_conversion_factor_2)-transducer_conversion_factor_2
            log_item = [result, result2,temperature, temperature2]
        else:
            # conversion formula to calculate pressure (psig) from pressure transducer voltage (V)
            # NOTE: BE SURE TO CHANGE THIS FORMULA IF USING A DIFFERENT TRANSDUCER 
            transducer_conversion_factor = params["tank_transducer_range"] *7.5/30
            result = (value*transducer_conversion_factor)-transducer_conversion_factor 
            log_item = [result,temperature, temperature2]
        
        if setting != "pre":
            logger(log_item,start_sequence, timelog)
        return result

    def air_fill(board_num, air_in_port, air_out_port):
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, air_in_port, 1)
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, air_out_port, 0)

    def air_vent(board_num, air_in_port, air_out_port):
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, air_in_port, 0)
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, air_out_port, 1)

    def air_off(board_num, air_in_port, air_out_port):
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, air_in_port, 0)
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, air_out_port, 0)
    
    def air_function(function):
        board_num1 = 0 # board_num corresponding to the USB-ERB08 set up in Instacal
        air_in = 16 #bit_num corresponding to the air fill solenoid
        air_out = 17 #bit_num corresponding to the air vent solenoid
        function(board_num1, air_in, air_out)

    
    def logger(inputArr, start_sequence,timelog):
        current_time = datetime.datetime.now()
        entry = [str(current_time),str(((current_time-start_sequence).seconds)+((current_time-start_sequence).microseconds/10 ** 6))]
        for input in inputArr:
            if not isinstance(input, str):
                input= str(input)
            entry.append(input)
        timelog.append(entry)
        return(timelog)

    air_function(air_off) #initialize with every solenoid off

    count = 0
    results = []

    
    while count < params["count"]:
        start_sequence = (datetime.datetime.now())
        if expt_type == "fill":
            timelog = [["current date/time","time (s)", "tank pressure (psig)", "supply pressure (psig)","tank temperature (K)", "FDMG cross external temperature (K)"]]
        else:
            timelog = [["current date/time,time (s)","tank pressure (psig)","tank temperature (K)","FDMG cross internal temperature (K)"]]
        value = pressure_temperature_measurement_logging("pre",start_sequence,timelog, expt_type)
        startTime = time.ctime(time.time()).replace(":","-")

        # first scale reading and determines if tank drain sequence should run or tank fill
        while not (P_init_range[0] <= value <= P_init_range[1]): 
            if (value > P_init_range[0]):
                if (abs(value - P_init_range[0])>0.5):
                    sleep_time = 2
                else:
                    sleep_time = 0.1
                air_function(air_vent)
                time.sleep(sleep_time)
            else:
                if (abs(value - P_init_range[1])>0.5):
                    sleep_time = 2
                else:
                    sleep_time = 0.1
                air_function(air_fill)
                time.sleep(sleep_time)
            value = pressure_temperature_measurement_logging("pre", start_sequence ,timelog, expt_type)

        # print(f"reached target psig of {value} and equilibrating for {pre} seconds")
        air_function(air_off)
        time.sleep(params["pre"])

        print(f"began experiment")
        start_sequence = (datetime.datetime.now())
        result_start = []
        result_end = []
        if expt_type == "vent":
            air_function(air_vent)
            while (params["P_end"]-0.02 <= value) : # measurement loop for the FDMG build that checks if the pressure reading is not less than params["P_end"]
                time.sleep(0.05) # equal to 1/10 of sampling interval of TEMP-AI, 2 Hz. NOTE: Change if higher sampling rate DAQ used
                value = pressure_temperature_measurement_logging("during", start_sequence , timelog, expt_type)
                if not value >= params["P_start"] and len(result_start) == 0:
                    result_start = timelog[-2] #sets result_start to the first instance of time where params["P_start"] (or higher) is measured
                    if result_start[1] == "time (s)":
                        result_start = timelog[-1] # conditional for if the result_start is recorded for the first measurement because the experiment began at below params["P_start"], which causes the timelog header in line 99 to be accidentally used for result_start. Sets result_start to be the first data recording in that case.        
                    print(f"Start point of {result_start[2]} psig reached at {result_start[1]} sec")
                if not value >= params["P_end"] and len(result_end) == 0:
                    result_end = timelog[-2] #sets result_end to the first instance of time where params["P_start"] (or higher) is measured
                    if result_end[1] == "time (s)":
                        result_end = timelog[-1] # conditional for if the result_end is recorded for the first measurement because the experiment began at below params["P_start"], which causes the timelog header in line 99 to be accidentally used for result_end. Sets result_end to be the first data recording in that case.        
                    print(f"End point of {result_end[2]} psig reached at {result_end[1]} sec")
        else:
            air_function(air_fill)
            while (params["P_end"]+0.02 >= value): # measurement loop for the FDMG build that checks if the pressure reading is not greater than params["P_end"]
                time.sleep(0.05) # equal to 1/10 of sampling interval of TEMP-AI, 2 Hz. NOTE: Change if higher sampling rate DAQ used
                value = pressure_temperature_measurement_logging("during", start_sequence , timelog, expt_type)
                if not value <= params["P_start"] and len(result_start) == 0:
                    result_start = timelog[-2] #sets result_start to the first instance of time where params["P_start"] (or lower) is measured 
                    if result_start[1] == "time (s)":
                        result_start = timelog[-1] # conditional for if the result_start is recorded for the first measurement because the experiment began at below params["P_start"], which causes the timelog header in line 99 to be accidentally used for result_start. Sets result_start to be the first data recording in that case.
                    print(f"Start point of {result_start[2]} psig reached at {result_start[1]} sec")
                if not value <= params["P_end"] and len(result_end) == 0:
                    result_end = timelog[-2] #sets result_end to the first instance of time where params["P_start"] (or higher) is measured
                    if result_end[1] == "time (s)":
                        result_end = timelog[-1] # conditional for if the result_end is recorded for the first measurement because the experiment began at below params["P_start"], which causes the timelog header in line 99 to be accidentally used for result_end. Sets result_end to be the first data recording in that case.        
                    print(f"End point of {result_end[2]} psig reached at {result_end[1]} sec")
        # result_end = timelog[-2] # sets result_end to the first instance of time where params["P_end"] (or the first pressure past params["P_end"]) is measured
        
        # run_result = [str(volume)] + result_start[:-1] + result_end[:-1] + [str(float(result_end[0]) - float(result_start[0]))] # concatenates volume of the experiment and the time and pressure results of results_start and result_end and pressure change time (the difference between time end and start)
        # NOTE: THE UNPACK OPERATOR "*" ONLY WORKS ON PYTHON 3.6+. IF ON A PYTHON VERSION BELOW 3.6, COMMENT THIS OUT AND UNCOMMENT LINE ABOVE
        print(f"reached end point from {(result_start[1])} sec at {(result_start[2])} psig to {(result_end[1])} sec at {(result_end[2])} psig ")

        pressure_change_time = float(result_end[1]) - float(result_start[1])
        end_sequence = datetime.datetime.now()
        run_result = [str(volume), (folder_path + "/" +startTime.replace(":","-") + ".csv"),str(start_sequence), str(end_sequence), *result_start[1:3], *result_end[1:3], str(pressure_change_time)] # concatenates volume of the experiment and the time and pressure results of results_start and result_end and pressure change time (the difference between time end and start)
        results.append(run_result)
        print(f"completed measurement from {str(start_sequence)} to {str(end_sequence)}")
        air_function(air_off)


        with open((folder_path + "/" +startTime.replace(":","-") + ".csv") ,  "w") as csv_file:
            for line in timelog:
                csv_file.write(",".join(line) + "\n")
        
        count +=1
        # print(f"begin equilibration period of {post} seconds")
        if not count == params["count"]:
            time.sleep(params["post"])


    # # real-time analysis printed in console to show to visitors, if necessary 
    # print display of 1 run to show system functioning to visitor
    # print("start time (s):")
    # print(round(float(results[0][1]),2))
    # print("start pressure (psig):")
    # print(round(float(results[0][2]),2))
    # print("end time (s):")
    # print(round(float(results[0][3]),2))
    # print("end pressure (psig):")
    # print(round(float(results[0][4]),2))
    # print("pressure change time or end time - start time (s):")
    # print(round(float(results[0][5]),2))
    # print("calculated volume (L):")
    # print(round(float(results[0][6]),2))
    # print("absolute error or absolute value of calculated volume - volume (L):")
    # print(round(float(results[0][7]),2))
    # print("calibration curve used to convert pressure change time to calculated volume:")
    # print("calculated volume = (pressure change time*-0.34311) + 73.89513")
    return(results)

