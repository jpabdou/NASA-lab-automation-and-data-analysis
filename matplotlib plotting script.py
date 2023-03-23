from turtle import title
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import csv
import pandas as pd

print("NOTE 1: Ensure that 'experiment directory.csv' is in the same folder as 'matplotlib plotting script.py' and as the .txt data files to be analyzed.")
print("NOTE 2: Open and review 'experiment directory.csv' and note the experiment IDs for the .txt files you want to have analyzed.")

# input call to determine how many plots to overlay
overlay = input("Do you want to overlay plots? Input y or Y for Yes or n or N for No:")
idList = []
if overlay[0] == "n" or overlay[0] == "N":
    f = int(input("Enter your experiment ID (a whole number > 0):"))
    idList.append(f)
elif overlay[0] == "y" or overlay[0] == "Y":
    plotnum = int(input("How many plots to overlay?"))
    plotcount = 0
    while plotnum != plotcount:
        f = int(input("Enter your experiment ID (a whole number > 0):"))
        idList.append(f)
        plotcount += 1

# input call to pull experiment parameters (ID, filename, title, condA, condB, settings#, timestart, stepmin, startflowA, endflowA, startflowB, endflowB, and steps count) based on experiment ID
settings = []
experiment = []
file = open("c:/Users/jabdou/Documents/C4D Data/experiment directory.csv")
csvfile = csv.reader(file)
for row in csvfile:
    settings.append(row)
for id in idList:
    experiment.append(settings[id])

# call to pull Powerchrom text file in the same directory as the python script and converts to lists of x-values (expected in time (minutes)) and y-values (expected in output(V))
data = []
datax = []
datay = []
minimum = 100
maximum = -100
timeend = 1
plotcount = 0
while plotcount != len(idList): 
    exp = "c:/Users/jabdou/Documents/C4D Data/"+ experiment[plotcount][1]+ ".txt"
    print(exp)
    results = open(exp)
    datatable = [z.split(' ')[0] for z in results.readlines()] # outputs an array of each line of the text file as a 
    data.append(datatable)
    data[plotcount]=[z.replace("\n", "") for z in data[plotcount]]
    data[plotcount] = [i for i in data[plotcount] if i]
    datax.append([float(z[:z.find("\t")]) for z in data[plotcount]])
    datay.append([float(z[z.find("\t")+1:]) for z in data[plotcount]])
    newtimeend = datax[plotcount][-1]
    newmin = min(datay[plotcount])
    newmax = max(datay[plotcount])
    timeend = max(newtimeend, timeend)
    minimum = min(minimum, newmin)
    maximum = max(maximum, newmax)
    plotcount += 1

# Simple plot of output (datay[plotcount]) vs. time (datax[plotcount]). The inputs are the settings values for start, end, bottom, and top and the f input for title
def cleanplotter(start, end, bottom, top): #, title):
    fig, ax = plt.subplots()
    #ax.set_title(title)
    ax.set_xlim(start,end)
    ax.set_ylim(bottom,top)
    ax.set_ylabel('Output (V)', loc='center')
    ax.set_xlabel('Time (minutes)', loc='center')
    plotcount = 0
    while plotcount != len(idList):
        ax.plot(datax[plotcount], datay[plotcount], label = experiment[plotcount][2], linewidth = 0.5)
        ax.legend(frameon=False)
        plotcount += 1
    plt.show()


def mix_test(start_rate1, final_rate1, start_rate2, final_rate2, steps_total): # function to generate list of pairs of flow rates for each syringe, P1 as rate1 and P2 as rate2. The inputs are taken from the settings values of the experiment
    step = 1
    diff1 = start_rate1-final_rate1
    diff2 = start_rate2-final_rate2
    ratelist = []
    while steps_total >= step:
        ratelist.append((start_rate1, start_rate2))
        start_rate1 = start_rate1 - (diff1/(steps_total-1))
        start_rate2 = start_rate2 - (diff2/(steps_total-1))
        step = step + 1 
    return(ratelist)

# Calibration curve plot of output vs. conductivity with fitted line and equation. The inputs are the settings values for everything except for title and the f input for title
def condplotter(bottom, top, startflowA, endflowA, startflowB, endflowB, condAbase, condBbase, steps): # , title): 
    fig, ax = plt.subplots()
    #ax.set_title(title)
    ax.set_xlim(float(str(condAbase)[:3]),round(condBbase,1)) # float-str conversion on lower x-limit to truncate decimal and round down
    ax.set_ylim(bottom,top)
    ax.set_ylabel('Output (V)', loc='center')
    # ax.set_xlabel('Electrolytic concentration (ppb)', loc='center') # for output voltage vs concentration plots, if necessary

    ax.set_xlabel('Conductivity (uS/cm)', loc='center')
    ratelist = mix_test(startflowA, endflowA, startflowB, endflowB, steps)
    plotcount = 0
    while plotcount != len(idList):
        timetracker = int(experiment[plotcount][5])
        steptime = int(experiment[plotcount][8])
        print(plotcount) 
        condramp = []
        conddrop = []
        for s in range(steps):
            cond = ((float(experiment[plotcount][3])*ratelist[s][0])+(float(experiment[plotcount][4])*ratelist[s][1]))/(ratelist[s][0]+ratelist[s][1]) # calculated conductivity of each step based on averaging over flow rate
            condramp.append(cond)
            conddrop.append(cond)
        conddrop.reverse()

        # these lists are converted to numpy float64 arrays to ensure compatibility with the linear regression numpy array results generated from scipy  
        condramp = np.array(condramp, dtype=np.float64)
        conddrop = np.array(conddrop, dtype=np.float64)

        ramplist = []
        droplist = []
        timetracker = int(experiment[plotcount][5])
        level = 1
        while level <= steps:
            ramplist.append(round(datay[plotcount][datax[plotcount].index((timetracker + steptime-1.5))],4)) 
            timetracker += steptime
            level +=1
        
        if int(experiment[plotcount][14]) == 2:
            droplist.append(ramplist[-1])
            level = 1
            while level <= steps -1:
                if int(experiment[plotcount][15]) == 1: # checks experiment override column for experiments that require overidden time points found in experiment[plotcount][16] to account for issues during the run
                    newTimePoints = experiment[plotcount][16].strip('][').split(', ') # takes string of list in this column and converst to list
                    droplist.append(round(datay[plotcount][datax[plotcount].index(int(newTimePoints[level-1]))],4))
                else:
                    droplist.append(round(datay[plotcount][datax[plotcount].index((timetracker + steptime-1.5))],4))
                    timetracker += steptime
                level +=1

        # conversion to numpy array just to ensure compatibility when plotting with condramp and conddrop numpy arrays
        ramplist = np.array(ramplist, dtype=np.float64)
        droplist = np.array(droplist, dtype=np.float64)

        rampres = stats.linregress(condramp, ramplist)
        ramp = str(round(rampres.slope,4)) + "*x + " + str(round(rampres.intercept,4))
        
        def rampfit(xval):
            return(rampres.slope*xval + rampres.intercept)
        if int(experiment[plotcount][6]) == 3:
            plt.scatter(condramp,ramplist, label = experiment[plotcount][2])
        else:
            # plt.scatter(condramp,ramplist, label = str(experiment[plotcount][2][:6]) + ": " + "y = " +  ramp + "       R^2 = " + str(round(rampres.rvalue**2,4))) #hard coding trick for displaying frequencies in legend for frequency sweeps
            # plt.scatter(condramp,ramplist, label = experiment[plotcount][2] + " ramp: " + "y = " +  ramp + "       R^2 = " + str(round(rampres.rvalue**2,4))) #hard coding trick for displaying electrolytic dosage amount in ppb in legend for AgNO3 and NaCl comparison

            plt.scatter(condramp,ramplist, label = "ramp " + str(plotcount+1) + ": " + "y = " +  ramp + "       R^2 = " + str(round(rampres.rvalue**2,4)))
        ax.plot(condramp, rampfit(condramp), linestyle='dashed')

        if int(experiment[plotcount][14]) == 2:
            dropres = stats.linregress(conddrop, droplist)
            drop = str(round(dropres.slope,4)) + "*x + " + str(round(dropres.intercept,4))

            def dropfit(xval):
                return(dropres.slope*xval + dropres.intercept)
            plt.scatter(conddrop, droplist, label = experiment[plotcount][2] + " drop: " + "y = " + drop + "      R^2 = " + str(round(dropres.rvalue**2,4))) #hard coding trick for displaying electrolytic dosage amount in ppb in legend for AgNO3 and NaCl comparison

            # plt.scatter(conddrop, droplist, label = "drop " + str(plotcount+1) + ": " + "y = " + drop + "      R^2 = " + str(round(dropres.rvalue**2,4)))
            ax.plot(conddrop, dropfit(conddrop), linestyle='dashed')
        print("ramp " + str(plotcount+1) + " plot data:", condramp,ramplist)
        print("drop" + str(plotcount+1) + " plot data:", conddrop,droplist)
        ax.legend(frameon=False)
        plotcount += 1
    plt.show()

# Calibration curve plot of relative output to minimum vs. conductivity with fitted line and equation. The inputs are the settings values for everything except for title and the f input for title
def relcondplotter(startflowA, endflowA, startflowB, endflowB, condAbase, condBbase, steps): # , title): 
    fig, ax = plt.subplots()
    ax.set_xlim(float(str(condAbase)[:3]),round(condBbase,1)) # float-str conversion on lower x-limit to truncate decimal and round down
    ax.set_ylim(0,1)
    ax.set_ylabel('Relative Output', loc='center')
    # ax.set_xlabel('Electrolytic concentration (ppb)', loc='center') # for output voltage vs concentration plots, if necessary

    ax.set_xlabel('Conductivity (uS/cm)', loc='center')
    ratelist = mix_test(startflowA, endflowA, startflowB, endflowB, steps)
    plotcount = 0
    while plotcount != len(idList):
        timetracker = int(experiment[plotcount][5])
        steptime = int(experiment[plotcount][8])
        print(plotcount) 
        condramp = []
        conddrop = []
        for s in range(steps):
            cond = ((float(experiment[plotcount][3])*ratelist[s][0])+(float(experiment[plotcount][4])*ratelist[s][1]))/(ratelist[s][0]+ratelist[s][1]) # calculated conductivity of each step based on averaging over flow rate
            condramp.append(cond)
            conddrop.append(cond)
        conddrop.reverse()

        # these lists are converted to numpy float64 arrays to ensure compatibility with the linear regression numpy array results generated from scipy  
        condramp = np.array(condramp, dtype=np.float64)
        conddrop = np.array(conddrop, dtype=np.float64)

        ramplist = []
        droplist = []
        timetracker = int(experiment[plotcount][5]) #+ int(experiment[plotcount][7])
        level = 1
        while level <= steps:
            ramplist.append(round(datay[plotcount][datax[plotcount].index((timetracker + steptime-1))],4)) 
            timetracker += steptime
            level +=1
        
        if int(experiment[plotcount][14]) == 2:
            droplist.append(ramplist[-1])
            level = 1
            while level <= steps -1:
                if int(experiment[plotcount][15]) == 1: # checks experiment override column for experiments that require overidden time points found in experiment[plotcount][16] to account for issues during the run
                    newTimePoints = experiment[plotcount][16].strip('][').split(', ') # takes string of list in this column and converst to list
                    droplist.append(round(datay[plotcount][datax[plotcount].index(int(newTimePoints[level-1]))],4))
                else:
                    droplist.append(round(datay[plotcount][datax[plotcount].index((timetracker + steptime-1))],4))
                    timetracker += steptime
                level +=1
        
        relramplist = []
        reldroplist = []
        for f in ramplist: # normalization relative to the maximum of y-inputs within a plot
            relramplist.append((f)/(max(ramplist)))
        for f in droplist:
            reldroplist.append((f)/(max(droplist)))
        # for f in ramplist: # feature-free normalization
        #     relramplist.append((f-min(ramplist))/(max(ramplist)-min(ramplist)))
        # for f in droplist:
        #     reldroplist.append((f-min(droplist))/(max(droplist)-min(droplist)))
        
        # conversion to numpy array just to ensure compatibility when plotting with condramp and conddrop numpy arrays
        relramplist = np.array(relramplist, dtype=np.float64)
        reldroplist = np.array(reldroplist, dtype=np.float64)

        relrampres = stats.linregress(condramp, relramplist)
        relramp = str(round(relrampres.slope,4)) + "*x + " + str(round(relrampres.intercept,4))
        
        def rampfit(xval):
            return(relrampres.slope*xval + relrampres.intercept)
        
        plt.scatter(condramp,relramplist, label = str(experiment[plotcount][2][:6]) + ": " + "y = " +  relramp + "       R^2 = " + str(round(relrampres.rvalue**2,4))) #hard coding trick for displaying frequencies in legend for frequency sweeps
        # plt.scatter(condramp,relramplist, label = experiment[plotcount][2] + " ramp: " + "y = " +  ramp + "       R^2 = " + str(round(rampres.rvalue**2,4))) #hard coding trick for displaying electrolytic dosage amount in ppb in legend for AgNO3 and NaCl comparison

        # plt.scatter(condramp,ramplist, label = "ramp " + str(plotcount+1) + ": " + "y = " +  ramp + "       R^2 = " + str(round(rampres.rvalue**2,4)))
        ax.plot(condramp, rampfit(condramp), linestyle='dashed')

        if int(experiment[plotcount][14]) == 2:
            reldropres = stats.linregress(conddrop, reldroplist)
            reldrop = str(round(reldropres.slope,4)) + "*x + " + str(round(reldropres.intercept,4))

            def dropfit(xval):
                return(reldropres.slope*xval + reldropres.intercept)
            plt.scatter(conddrop, reldroplist, label = experiment[plotcount][2] + " drop: " + "y = " + reldrop + "      R^2 = " + str(round(reldropres.rvalue**2,4))) #hard coding trick for displaying electrolytic dosage amount in ppb in legend for AgNO3 and NaCl comparison

            # plt.scatter(conddrop, droplist, label = "drop " + str(plotcount+1) + ": " + "y = " + drop + "      R^2 = " + str(round(dropres.rvalue**2,4)))
            ax.plot(conddrop, dropfit(conddrop), linestyle='dashed')
        print("ramp " + str(plotcount+1) + " plot data:", condramp,relramplist)
        print("drop" + str(plotcount+1) + " plot data:", conddrop,reldroplist)
        ax.legend(frameon=False)
        plotcount += 1
    plt.show()


# expt = input("Input the title for this experiment plot:") # removed this and just used basic filename for plot titles
# title = experiment[0][2]
# title = input("Input the title for this experiment plot:")
condAbase = float(experiment[0][3])
condBbase = float(experiment[0][4])
preset = int(experiment[0][6])
timestart = int(experiment[0][5])
startflowA = int(experiment[0][9])
endflowA = int(experiment[0][10])
startflowB = int(experiment[0][11])
endflowB = int(experiment[0][12])
steps = int(experiment[0][13])

if preset == 1 or preset == 3: # preset settings for 1 - 1.5 uS/cm experiment or 5.5 - 6 uS/cm experiment
    botlimit = float(round((minimum - 0.02), 2)) # this limit and toplimit are set according to the min/max of the y-values with an offset 
    toplimit = float(round((maximum + 0.02), 2))
elif preset == 2: # preset settings for 1 - 6 uS/cm experiment
    botlimit = float(round((minimum - 0.05), 2))
    toplimit = float(round((maximum + 0.05), 2))
elif preset == 0: # settings for custom experiments
    timestart = float(input("Input your experiment start time in minutes:"))
    timeend = float(input("Input your experiment end time in minutes:"))
    botlimit = float(round((minimum - 0.05), 2))
    toplimit = float(round((maximum + 0.05), 2))
    startflowA= float(input("Input the starting flow rate of P1 syringe in uL/min:"))
    endflowA= float(input("Input the ending flow rate of P1 syringe in uL/min:"))
    startflowB= float(input("Input the starting flow rate of P2 syringe in uL/min:"))
    endflowA= float(input("Input the ending flow rate of P1 syringe in uL/min:"))
    steps= float(input("Input the number of flow rate steps including starting and ending steps:"))
    stepmin = float(input("Input the time between steps in minutes:"))

cleanplotter(timestart, timeend, botlimit, toplimit) #, title + " uS/cm experiment")

condplotter(botlimit, toplimit, startflowA, endflowA, startflowB, endflowB, condAbase, condBbase, steps) #, title + " uS/cm experiment calibration curve")

# relcondplotter(startflowA, endflowA, startflowB, endflowB, condAbase, condBbase, steps) #, title + " uS/cm experiment calibration curve")