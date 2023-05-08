<h1>The story behind this project<h1>
<h3>This is a collection of programs that motivated me to further my learning in software engineering and web development.</h3>

<h3>In 2022, I began working on a conductivity detector for monitoring biocide dosage that required scripts to control hardware and run analysis on the detector data. I applied my knowledge in Python to create two scripts (found in the "2022 scripts" folder):<br></br>
  <ul>
    <li>M6 pump calibration test.py: automation script for pump experiments on the detector
    <li>matplotlib plotting script.py: data analysis/visualization script to create a time-series plot and calibration curve plot based on data from each experiment
  </ul>
Because of the motivation I had for developing more features for the project and for improving the code, I knew that I wanted to pursue a career in web development where I can apply my problem-solving skills to create products that have an impact on peoples' lives.</h3>

<h3>In 2023, I developed software for automated calibration and data analysis of a volume gauging system to determine the volume of water in an International Space Station storage tank in microgravity. While I was developing this software, I was reaching the end of my full stack web development bootcamp and I was able to apply my knowledge from there to write cleaner code with expanded functionality. This was accomplished through a central program (FDMG_system_controller v3.py) by calling functions to automate the system for experiment through:<br></br>
    <ul>
    <li>tank_water_sequence_v2.py: automation script to toggle solenoid valves to the water line to fill and empty tank of water to target volume
    <li>experiment_sequence_v3.py: automation script to toggle solenoid valves to the air line to set air pressure within the tank and measure the time to reach a target pressure as a means of measuring tank volume
  </ul>
The central program also calls functions to analyze data from two data capture sources through:<br></br>
    <ul>
    <li>pandas_data_analysis_graphtec_script_post_auto_v2.py
    <li>pandas_data_analysis_automation_script_v3.py
  </ul>
These two analysis scripts each results in a .csv output with the relevant statistics (standard deviation, root-means-squared deviation, and absolute error). They both also output two linear plots as .png images, a calibration curve with a linear fit trendline and an error plot to assess the system in terms of measurement accuracy and precision. With the resulting plots shown below:</h3>

<h3>pandas_data_analysis_automation_script_v3.py results:</h3>
<img src="images\vent expt choked flow high pressure 03-27-23 USB-TEMP-AI calib curve experiment#1.png" alt="calibration curve plot from USB-TEMP-AI results" />
<br></br>
<img src="images\vent expt choked flow high pressure 03-27-23 USB-TEMP-AI error plot experiment#1.png" alt="error plot from USB-TEMP-AI results" />
<br></br>

<h3>pandas_data_analysis_graphtec_script_post_auto_v2.py results:</h3>
<img src="images\vent expt choked flow high pressure 03-27-23 Graphtec calib curve experiment#1.png" alt="calibration curve plot from graphtec results" />
<br></br>
<img src="images\vent expt choked flow high pressure 03-27-23 Graphtec error plot experiment#1.png" alt="error plot from graphtec results" />
<br></br>
