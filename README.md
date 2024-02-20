# The story behind this project<h1>
This is a collection of programs that motivated me to further my learning in software engineering and web development.

In 2022, I began working on a conductivity detector for monitoring biocide dosage that required scripts to control hardware and run analysis on the detector data. I applied my knowledge in Python to create two scripts (found in the "2022 scripts" folder):

  - M6 pump calibration test.py: automation script for pump experiments on the detector
  - matplotlib plotting script.py: data analysis/visualization script to create a time-series plot and calibration curve plot based on data from each experiment

Because of the motivation I had for developing more features for the project and for improving the code, I knew that I wanted to pursue a career in web development where I can apply my problem-solving skills to create products that have an impact on peoples' lives.

In 2023, I developed software for automated calibration and data analysis of a volume gauging system to determine the volume of water in an International Space Station storage tank in microgravity. While I was developing this software, I was reaching the end of my full stack web development bootcamp and I was able to apply my knowledge from there to write cleaner code with expanded functionality. This was accomplished through a central program (FDMG_system_controller v3.py) by calling functions to automate the system for experiment through:
    - tank_water_sequence_v2.py: automation script to toggle solenoid valves to the water line to fill and empty tank of water to target volume
    - experiment_sequence_v3.py: automation script to toggle solenoid valves to the air line to set air pressure within the tank, reads the pressure transducer installed on the tank to measure the time to reach a target pressure as a means of measuring tank water volume, and exports the data measured from the automation data acquisition (DAQ) board as a .csv file

The central program also calls functions to analyze data from two data capture sources through:

  - pandas_data_analysis_automation_script_v3.py: to process data generated with experiment_sequence_v3.py to control and export data from the automation DAQ
  - pandas_data_analysis_graphtec_script_post_auto_v2.py: to process data manually transferred from a data acquisition (DAQ) logging system

These two analysis scripts each results in a .csv output with the relevant statistics (standard deviation, root-means-squared deviation, and absolute error). They both also output two linear plots as .png images, a calibration curve with a linear fit trendline and an error plot to assess the system in terms of measurement accuracy and precision. With the resulting plots shown below:

## pandas_data_analysis_automation_script_v3.py results:
Calibration curve plot of Water Fill Volume (y-axis) vs. average pressure change time (x-axis) for automation data acquisition (DAQ) board:
<img src="https://github.com/jpabdou/NASA-lab-automation-and-data-analysis/blob/main/images/vent%20expt%20choked%20flow%20high%20pressure%2003-27-23%20USB-TEMP-AI%20calib%20curve%20experiment%231.png" alt="calibration curve plot from USB-TEMP-AI results" />

Error plot for automation DAQ board:

<img src="https://github.com/jpabdou/NASA-lab-automation-and-data-analysis/blob/main/images/vent%20expt%20choked%20flow%20high%20pressure%2003-27-23%20USB-TEMP-AI%20error%20plot%20experiment%231.png" alt="error plot from USB-TEMP-AI results" />

## pandas_data_analysis_graphtec_script_post_auto_v2.py results:
Calibration curve plot of Water Fill Volume (y-axis) vs. average pressure change time (x-axis) for manual DAQ system:
<img src="https://github.com/jpabdou/NASA-lab-automation-and-data-analysis/blob/main/images/vent%20expt%20choked%20flow%20high%20pressure%2003-27-23%20Graphtec%20calib%20curve%20experiment%231.png" alt="calibration curve plot from Graphtec results" />

Error plot for manual DAQ system:

<img src="https://raw.githubusercontent.com/jpabdou/NASA-lab-automation-and-data-analysis/main/images/vent%20expt%20choked%20flow%20high%20pressure%2003-27-23%20Graphtec%20error%20plot%20experiment%231.png" alt="error plot from Graphtec results" />
