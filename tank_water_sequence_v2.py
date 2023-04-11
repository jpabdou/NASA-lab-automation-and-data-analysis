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
 

def tank_water_sequence(target_mass, first_experiment_params):
    def check_params(key_string): # function that automatically checks that you set your keys and values correctly in your first experiment parameters
        if key_string not in params:
            raise Exception(f'{key_string} key is not in the experiment dictionary. Check the expt_list in the FDMG_system_controller program')

    params = first_experiment_params # assign to params variable as first_experiment_params
    check_params("P_start")
    check_params("P_end")
    check_params("P_offset")
    check_params("volumes")
    check_params("tank_transducer_range")
    check_params("P_delay")


    transducer_conversion_factor = params["tank_transducer_range"]*7.5/30 # sets the multiplier and offset values to convert transducer voltage into pressure in psi; using a 250 ohm resistor
    


    cutoff = 5 # pressure cutoff in psi used to control air valves during water filling or draining

    
    volume_offsets = [0, 0.05] # volume offsets in the case of the tank being filled for each step so the target range of each volume step is target_volume to target_volume + 0.05 L
    if len(params["volumes"]) >=2: 
        if params["volumes"][0] > params["volumes"][1]: # determining if tank is being emptied for each volume after the first volume (supposed to be 0)
            volume_offsets = [-0.05, 0] # if water is drained for each volume step, change offset so the target range of each volume step is target_volume - 0.05 L to target_volume


    # Configure serial connection to scale
    ser1 = serial.Serial(
        port='COM3',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=False,
        timeout=1,
        bytesize=serial.EIGHTBITS
    )

    # Check that the connection is open
    print(ser1.isOpen())
    print("scale connected")

    # target mass in kg

    timelog = [" 1000 kg"] # starting/default value is set to 1000 kg, an improbably high value for the tank
    # timelog not currently in use, but can be implemented with a write to csv while loop, see around line 150 in experiment_sequence at close to the end of the expt_run function

    # Sends instructions to pump in the form of a string encoded in ASCII format

    def direct1(string):
        string = string + "\r\n" #\r\n are carriage return and new line for python strings, respectively.
        ser1.write(string.encode('ascii'))


    def direct_log1(command): # logging the mass of the rate ran before and after sending the current rate on the pump using the PR V command and directing the pump rate
        direct1(command)
        followup= str(ser1.read_until()) # returns the scale reading in this string format: "b'+ xxxx kg'" where xxxx is your scale mass value
        if (followup != "b''"):
            logger(followup)
        else:
            logger(" 1000 kg")

    def logger(string):
        timelog.append(string)
        return(timelog)

    def float_convert(): # returns the last recorded scale mass reading as a decimal value
        return float(timelog[-1][timelog[-1].find(" "):timelog[-1].find(" kg")]) # remove the rest of the scale reading string and converts to a float value equal to mass in kg

    def pressure_measurement():
        board_num2 = 1 # board_num corresponding to the USB-TEMP-AI set up in Instacal
        channel = 0
        ai_range = ULRange.BIP5VOLTS
        value = ul.v_in(board_num2, channel, ai_range) # reads voltage value for tank transducer
        return (value*transducer_conversion_factor)-transducer_conversion_factor # returns converted voltage into pressure (psig)


    def air_fill(board_num, air_in_port, air_out_port):
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, air_in_port, 1)
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, air_out_port, 0)

    def air_vent(board_num, air_in_port, air_out_port):
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, air_in_port, 0)
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, air_out_port, 1)

    def air_off(board_num, air_in_port, air_out_port):
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, air_in_port, 0)
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, air_out_port, 0)
    
    def air_function(function): # higher order function for controlling the air solenoids based on the function parameter
        board_num1 = 0 # board_num corresponding to the USB-ERB08 set up in Instacal
        air_in = 16 #bit_num corresponding to the air fill solenoid
        air_out = 17 #bit_num corresponding to the air vent solenoid
        function(board_num1, air_in, air_out)
    

    def water_drain(board_num, water_in_port, water_out_port):
        air_function(air_fill)
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, water_in_port, 0)
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, water_out_port, 1)

    def water_fill(board_num, water_in_port, water_out_port):
        air_function(air_vent)
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, water_in_port, 1)
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, water_out_port, 0)
    
    def water_off(board_num, water_in_port, water_out_port):
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, water_in_port, 0)
        ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, water_out_port, 0)

    def water_function(function): # higher order function for controlling the water solenoids based on the function parameter
        board_num1 = 0 # board_num corresponding to the USB-ERB08 set up in Instacal
        water_in = 18 #bit_num corresponding to the water fill solenoid
        water_out = 19 #bit_num corresponding to the water drain solenoid
        function(board_num1, water_in, water_out)

    def all_shutoff():
        water_function(water_off)
        air_function(air_off)

    all_shutoff() # initialize with every solenoid off
    drain = False # initialize drain variable as a local variable set to False; False means that the tank is to be filled with water while True means the tank is to be emptied of water
    air_closed = True # initialize air_closed variable as a local variable set to True; False means that the air solenoids are to be active for filling and venting while True means both air solenoids are closed
    #                   the reason for this distinction between the drain and air_closed states is because this script primarily involves the water solenoids to keeping running until the tank is filled/emptied of water to reach the target mass
    #                   the air solenoids only need to be active to maintain the tank air bladder pressure above a cutoff when draining water from the tank or below a cutoff when filling the tank with water


    # first scale reading and determines if tank drain sequence should run or tank fill
    while (float_convert()== 1000): #while loop to check that the first tank mass reading is the actual mass and not the default value of 1000 kg
        direct_log1("N")

    if target_mass  < float_convert():
        water_function(water_drain)
        air_closed=False
        drain = True

    if target_mass  > float_convert():
        water_function(water_fill)
        air_closed=False
        drain =False

    startProgram = (datetime.datetime.now())
    while not (target_mass + volume_offsets[0] <= float_convert() <= target_mass + volume_offsets[1]) : # self-correcting while loop that targets tank mass +/- 0.05 kg
        if not (float_convert() ==1000): # ensure that switching doesn't occur if the timelog[index] is the default value of 1000
            if target_mass + volume_offsets[1] < float_convert() and drain ==False: # switching logic if the tank mass above the target mass range 
                water_function(water_drain)
                drain = True
                print(f"switching to drain set to {str(drain)}")
            if target_mass + volume_offsets[0] > float_convert() and drain ==True: # switching logic if the tank mass is below the target mass range
                water_function(water_fill)
                drain =False
                print(f"switching to drain set to {str(drain)}")
        value = pressure_measurement()
        # logic for opening/closing air valves during fill, this might need to be reworked to prevented air valves from opening/closing at too high of a frequency and increasing wear
        if value<cutoff-0.5 and drain == False and air_closed == False:
            air_closed=True
            air_function(air_off)
        if value > cutoff+0.5 and drain == False and air_closed == True:
            air_closed =False
            air_function(air_vent)
        if value>cutoff +0.5 and drain == True and air_closed == False:
            air_closed=True
            air_function(air_off)
        if value < cutoff-0.5 and drain == True and air_closed == True:
            air_closed= False
            air_function(air_fill)
        direct_log1("N")



    all_shutoff()
    while (float_convert()== 1000): #while loop to check that the tank mass reading is the actual mass and not the default value of 1000 kg
        direct_log1("N")
    print(f"reached target mass of {float_convert()}")
    value = pressure_measurement()

    if params["P_start"] > params["P_end"]:
        P_init_range = [params["P_start"]+params["P_delay"]+params["P_offset"], params["P_start"]+params["P_delay"]+params["P_offset"]+0.05]
    else:
        P_init_range = [params["P_start"]-params["P_delay"]-params["P_offset"]-0.05, params["P_start"]-params["P_delay"]-params["P_offset"]]
    print(P_init_range)
    while not (P_init_range[0]<=value<=P_init_range[1]):
        if P_init_range[0] > value:
            air_function(air_fill)
        else:
            air_function(air_vent)
        value = pressure_measurement()
    while not (target_mass + volume_offsets[0] <= float_convert() <= target_mass + volume_offsets[1]) : # self-correcting while loop that targets tank mass +/- 0.05 kg
        if not (float_convert() ==1000): # ensure that switching doesn't occur if the timelog[index] is the default value of 1000
            if target_mass + volume_offsets[1] < float_convert() and drain ==False: # switching logic if the tank mass above the target mass range 
                water_function(water_drain)
                drain = True
                print(f"switching to drain set to {str(drain)}")
            if target_mass + volume_offsets[0] > float_convert() and drain ==True: # switching logic if the tank mass is below the target mass range
                water_function(water_fill)
                drain =False
                print(f"switching to drain set to {str(drain)}")
        value = pressure_measurement()
        # logic for opening/closing air valves during fill, this might need to be reworked to prevented air valves from opening/closing at too high of a frequency and increasing wear
        if value<cutoff-0.5 and drain == False and air_closed == False:
            air_closed=True
            air_function(air_off)
        if value > cutoff+0.5 and drain == False and air_closed == True:
            air_closed =False
            air_function(air_vent)
        if value>cutoff +0.5 and drain == True and air_closed == False:
            air_closed=True
            air_function(air_off)
        if value < cutoff-0.5 and drain == True and air_closed == True:
            air_closed= False
            air_function(air_fill)
        direct_log1("N")
    
    endProgram = (datetime.datetime.now())
    all_shutoff()
    if ((endProgram-startProgram).seconds>60): # verifying that pressure changes where no more than 1 minute, no need to equilibrate if no time was spent filling/venting air    
        print("equilibrating for 5 minutes due over 1 minute of pressure change")
        time.sleep(300) # reset time for tank to account for adiabatic expansion that occurs as the air pressure change occurs during the water fill/drain
    while (float_convert()== 1000): #while loop to check that the tank mass reading is the actual mass and not the default value of 1000 kg
        direct_log1("N")
    

    return(float_convert())

# expt_list_template_vent = {"P_start": 25, "P_end": 24, "P_delay": 1, "count": 6, "pre": 60, "post": 0, "P_offset": 0.35, "tank_transducer_range": 30, "volumes": [70]}
# tank_water_sequence(70,expt_list_template_vent)