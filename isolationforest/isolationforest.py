import csv
import glob, os, getopt, sys
from os import walk
import pandas as pd
import numpy as np
from datetime import date, timedelta
import matplotlib as mpl
import datetime
import plotly.express as px
from sklearn.ensemble import IsolationForest
os.chdir(".")



###### Arguments
full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]

short_options = "h"
long_options = ["heartrate=", "step=", "device=", "restinghr="]

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except getopt.error as err:
    print(str(err))
    sys.exit(2)
    
heartrate_file = ""
step_file = ""
restinghr_file = ""
device = ""
for current_argument, current_value in arguments:
    if current_argument in ("-h", "--help") :
        print ("Please use: python3 isolationforest.py --device=Fitbit  --heartrate=<HR_FILE> --step=<STEP_FILE> || python3 isolationforest.py --device=AppleWatch  --heartrate=<HR_FILE> --step=<STEP_FILE> ")
    elif current_argument in ("--heartrate"):
        heartrate_file = current_value
    elif current_argument in ("--step"):
        step_file = current_value
    elif current_argument in ("--device"):
        device = current_value
    elif current_argument in ("--restinghr"):
        restinghr_file = current_value


       
###### Fitbit
if(device=="Fitbit"):
    ST_Dic = {}
    with open(step_file, "r") as f:
        ST_lines = f.readlines()
    for st_line in ST_lines:
        if("-" in st_line):
                st_datetime = st_line.split(",")[0]
                st_val = st_line.split(",")[1]
                time_for_night = st_datetime.split(" ")[1]
                if ((time_for_night.startswith("00:")) or (time_for_night.startswith("01:")) or (time_for_night.startswith("02:")) or (time_for_night.startswith("03:")) or (time_for_night.startswith("04:")) or (time_for_night.startswith("05:")) or (time_for_night.startswith("06:"))):
                    ST_Dic[st_datetime] = st_val

    with open('RHR.csv', "w") as rhrFile:
        rhrFile.write("Start_Date_Time,Value\n")
        with open(heartrate_file, "r") as hrCSV:
            hrCSVReader = csv.DictReader(hrCSV)
            for hr_rec in hrCSVReader:
                hr_start_date_time = hr_rec['datetime']
                hr_value = hr_rec['heartrate']
                start_date = hr_start_date_time.split(" ")[0]
                start_time = hr_start_date_time.split(" ")[1]
                start_time_min = hr_start_date_time.split(" ")[1][0:5] + ":00"
                line_to_search = start_date + " " + start_time_min
                if ((start_time.startswith("00:")) or (start_time.startswith("01:")) or (start_time.startswith("02:")) or (start_time.startswith("03:")) or (start_time.startswith("04:")) or (start_time.startswith("05:")) or (start_time.startswith("06:"))):
                    if (line_to_search not in ST_Dic):
                        rhrFile.write(start_date + " " + start_time + "," + hr_value + "\n")
            
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    df = pd.read_csv('RHR.csv' )
    df['Start_Date_Time']=pd.to_datetime(df['Start_Date_Time'])
    df=df.set_index('Start_Date_Time').resample("24H").mean().reset_index()
    df['Value']=df['Value'].interpolate()
    model =  IsolationForest(contamination="auto")
    model.fit(df[['Value']])
    df['Outliers']=pd.Series(model.predict(df[['Value']])).apply(lambda x: 'yes' if (x == -1) else 'no' )
    df.to_csv('if_anomalies.csv'  , columns=['Start_Date_Time','Outliers'] , index=False)
    #print(df.query('outliers=="yes"')['Start_Date_Time'])
    


###### AppleWatch
if(device=="AppleWatch"):
    delta = datetime.timedelta(minutes=1)
    dateTimes = {}
    with open(step_file , "r") as stepCSV:
                stepCSVReader = csv.DictReader(stepCSV)
                for step_rec in stepCSVReader:
                            st_start_date = step_rec['start_datetime'].split(" ")[0]
                            st_start_time = step_rec['start_datetime'].split(" ")[1]
                            st_end_date = step_rec['end_datetime'].split(" ")[0]
                            st_end_time = step_rec['end_datetime'].split(" ")[1]
                            if ((st_start_time.startswith("00:")) or (st_start_time.startswith("01:")) or (st_start_time.startswith("02:")) or (st_start_time.startswith("03:")) or (st_start_time.startswith("04:")) or (st_start_time.startswith("05:")) or (st_start_time.startswith("06:"))):
                                if(st_start_date == st_end_date):
                                    start = datetime.datetime.strptime( st_start_time, '%H:%M:%S' )
                                    end = datetime.datetime.strptime( st_end_time, '%H:%M:%S' )
                                    t = start
                                    while t <= end :
                                        tempArray = []
                                        if(st_start_date in dateTimes):
                                            tempArray = dateTimes[st_start_date]
                                        tempArray.append(datetime.datetime.strftime(t, '%H:%M'))
                                        dateTimes[st_start_date] = tempArray
                                        t += delta

    with open('RHR.csv' , "w") as rhrFile:
            rhrFile.write("Start_Date_Time,Value\n")
            with open(heartrate_file , "r") as hrCSV:
                hrCSVReader = csv.DictReader(hrCSV)
                for hr_rec in hrCSVReader:
                            hr_start_date = hr_rec['datetime'].split(" ")[0]
                            hr_start_time = hr_rec['datetime'].split(" ")[1]
                            hr_value = hr_rec['heartrate']
                            if ((hr_start_time.startswith("00:")) or (hr_start_time.startswith("01:")) or (hr_start_time.startswith("02:")) or (hr_start_time.startswith("03:")) or (hr_start_time.startswith("04:")) or (hr_start_time.startswith("05:")) or (hr_start_time.startswith("06:"))):
                                if (hr_start_date in dateTimes):
                                    arrayForThisDay = dateTimes[hr_start_date]
                                    hr_time  = datetime.datetime.strptime( hr_start_time, '%H:%M:%S' )
                                    if ( datetime.datetime.strftime(hr_time, '%H:%M') not in arrayForThisDay):
                                        rhrFile.write(hr_start_date + " " + hr_start_time + "," + hr_value + "\n")
        

    pd.set_option("display.max_rows", None, "display.max_columns", None)
    df = pd.read_csv('RHR.csv')
    df['Start_Date_Time']=pd.to_datetime(df['Start_Date_Time'])
    df=df.set_index('Start_Date_Time').resample("24H").mean().reset_index()
    df['Value']=df['Value'].interpolate()
    model =  IsolationForest(contamination="auto")
    model.fit(df[['Value']])
    df['Outliers']=pd.Series(model.predict(df[['Value']])).apply(lambda x: 'yes' if (x == -1) else 'no' )
    df.to_csv('if_anomalies.csv'  , columns=['Start_Date_Time','Outliers'] , index=False)
    #print(df.query('outliers=="yes"')['Start_Date_Time'])
