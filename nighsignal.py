import glob, os, getopt, sys
import csv, json
from os import walk
import statistics
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import datetime
import collections
from collections import deque
from collections import OrderedDict
from itertools import tee, groupby
from matplotlib import pyplot as plt
from operator import itemgetter
from datetime import date, timedelta
os.chdir(".")


### EXAMPLE RUN: python3 nighsignal.py --device=AppleWatch --heartrate=P355472-AppleWatch-hr.csv  --step=P355472-AppleWatch-st.csv
### EXAMPLE RUN: python3 nighsignal.py --device=Fitbit --restinghr=P682517-Fitbit-rhr.csv


#functions
def consecutive_groups(iterable, ordering=lambda x: x):
    for k, g in groupby(enumerate(iterable), key=lambda x: x[0] - ordering(x[1])):
        yield map(itemgetter(1), g)
        
def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z
    
def sort_dict_data(data):
    return OrderedDict((k, v)
                       for k, v in sorted(data.iteritems()))
                       
def round10Base( n ):
    a = (n // 10) * 10
    b = a + 10
    return (b if n - a > b - n else a)


#plot settings
font = {'family' : 'sans-serif',
        'size'   : 4,
}
plt.rc('font', **font)
plt.rc('xtick',labelsize=8)
plt.rc('ytick',labelsize=10)
plt.style.use('seaborn-dark-palette')


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
        print ("Please use: python3 nightsignal.py --device=Fitbit --restinghr=<RHR_FILE> || python3 nightsignal.py --device=AppleWatch  --heartrate=<HR_FILE> --step=<STEP_FILE> ")
    elif current_argument in ("--heartrate"):
        heartrate_file = current_value
    elif current_argument in ("--step"):
        step_file = current_value
    elif current_argument in ("--device"):
        device = current_value
    elif current_argument in ("--restinghr"):
        restinghr_file = current_value


#nightsignal configs
medianConfig = "MedianOfAvgs" # MedianOfAvgs | AbsoluteMedian
yellow_threshold = 3
red_threshold = 4

            
#################################  Fitbit #################################
if(device=="Fitbit"):
    with open(restinghr_file , "r") as rhrFile:
        records = rhrFile.readlines()
    
    date_hrs_dic = {}
    for record in records:
        if ("Datetime" not in record):
            record_elements = record.split(",")
            rec_datetime = record_elements[0]
            rec_date = rec_datetime.split(" ")[0]
            rec_time = rec_datetime.split(" ")[1]
            rec_hr = record_elements[1]
            rec_st = record_elements[3].strip(' \t\n\r')
            if (rec_st == "0" and ((" 00:" in rec_datetime) or (" 01:" in rec_datetime) or (" 02:" in rec_datetime) or (" 03:" in rec_datetime) or (" 04:" in rec_datetime) or (" 05:" in rec_datetime) or (" 06:" in rec_datetime)) ):
                if (rec_date not in date_hrs_dic):
                    date_hrs_dic[rec_date] = rec_hr
                else:
                    date_hrs_dic[rec_date] = date_hrs_dic[rec_date] + "*" + rec_hr
    
    #Calculate AVGs , Imputation, Healthy baseline Median, and Alerts
    date_hr_avgs_dic = {}
    for key in date_hrs_dic:
        AVGHR = 0
        temp = date_hrs_dic[key]
        numOfHRs = str(temp).count("*") + 1
        hrs = temp.split("*")
        for hr in hrs:
            AVGHR = AVGHR + int(float(hr))
        AVGHR = int(AVGHR/numOfHRs)
        date_hr_avgs_dic[key] = AVGHR
                        
    missed_days_avg_dic = {}
    sorted_keys = sorted(date_hr_avgs_dic.keys())
    sorted_avgs = sorted(date_hr_avgs_dic.items())
    for i,v in enumerate(sorted_keys):
        if(i!=0 and i!=len(sorted_keys)-1):
            today = datetime.datetime.strptime(sorted_keys[i] , "%Y-%m-%d")
            nextDay = datetime.datetime.strptime(sorted_keys[i+1] , "%Y-%m-%d")
            prevDay = datetime.datetime.strptime(sorted_keys[i-1] , "%Y-%m-%d")
            if ((nextDay-today).days==1 and (today-prevDay).days==2):
                missDate = today - datetime.timedelta(days=1)
                if (missDate.strftime("%Y-%m-%d") not in missed_days_avg_dic and missDate.strftime("%Y-%m-%d") not in date_hr_avgs_dic):
                    missed_days_avg_dic[missDate.strftime("%Y-%m-%d")] = int(round((date_hr_avgs_dic[sorted_keys[i]] + date_hr_avgs_dic[sorted_keys[i-1]])/2 , 1))
            if ((nextDay-today).days==2 and (today-prevDay).days==1):
                missDate = today + datetime.timedelta(days=1)
                if (missDate.strftime("%Y-%m-%d") not in missed_days_avg_dic and missDate.strftime("%Y-%m-%d") not in date_hr_avgs_dic):
                    missed_days_avg_dic[missDate.strftime("%Y-%m-%d")] = int(round((date_hr_avgs_dic[sorted_keys[i]] + date_hr_avgs_dic[sorted_keys[i+1]])/2 , 1))
    for key in missed_days_avg_dic:
        if key not in date_hr_avgs_dic:
            date_hr_avgs_dic[key] = missed_days_avg_dic[key]
    temp = OrderedDict(sorted(date_hr_avgs_dic.items(), key=lambda t: t[0]))
    date_hr_avgs_dic = dict(temp)
        
    if(medianConfig == "MedianOfAvgs"):
        prev_keys_dic = {}
        for k1 in date_hr_avgs_dic:
            k1_prev_keys = []
            for k2 in date_hr_avgs_dic:
                if (k1>=k2):
                    k1_prev_keys.append(k2)
            prev_keys_dic[k1] = k1_prev_keys
            
        date_hr_meds_dic = {}
        for k in prev_keys_dic:
            list_for_med = []
            prev_keys = prev_keys_dic[k]
            for item in prev_keys:
                list_for_med.append(date_hr_avgs_dic[item])
            date_hr_meds_dic[k] = int(statistics.median(list_for_med))
            
            
    elif(medianConfig == "AbsoluteMedian"):
        live_dates_hrs_dic = {}
        for record in records:
            if ("Datetime" not in record):
                record_elements = record.split(",")
                rec_datetime = record_elements[0]
                rec_date = rec_datetime.split(" ")[0]
                rec_time = rec_datetime.split(" ")[1]
                rec_hr = record_elements[1]
                rec_st = record_elements[3].strip(' \t\n\r')
                if (rec_st == "0" and ((" 00:" in rec_datetime) or (" 01:" in rec_datetime) or (" 02:" in rec_datetime) or (" 03:" in rec_datetime) or (" 04:" in rec_datetime) or (" 05:" in rec_datetime) or (" 06:" in rec_datetime)) ):
                    if (rec_date not in live_dates_hrs_dic):
                        live_dates_hrs_dic[rec_date] = rec_hr
                    else:
                        live_dates_hrs_dic[rec_date] = live_dates_hrs_dic[rec_date] + "*" + rec_hr

        live_dates_hrs_dic_new = {}
        for key1 in live_dates_hrs_dic:
            live_dates_hrs_dic_new[key1] = ""
            temp = ""
            for key2 in live_dates_hrs_dic:
                if key1 >= key2:
                    if temp=="":
                        temp = live_dates_hrs_dic[key2]
                    else:
                        temp = temp + "*" + live_dates_hrs_dic[key2]
            live_dates_hrs_dic_new[key1] = temp

        date_hr_meds_dic = {}
        for key in live_dates_hrs_dic_new:
            MEDHR = 0
            temp = live_dates_hrs_dic_new[key]
            hrs = temp.split("*")
            med_list = []
            for hr in hrs:
                med_list.append(int(float(hr)))
            MEDHR = int(statistics.median(med_list))
            date_hr_meds_dic[key] = MEDHR

    for key in date_hr_avgs_dic:
        if (key in date_hr_meds_dic):
            if (date_hr_avgs_dic[key] >= date_hr_meds_dic[key] + red_threshold):
                with open("potenital_reds.csv" , "a") as out_file:
                    out_file.write(key + "\n")
            if (date_hr_avgs_dic[key] >= date_hr_meds_dic[key] + yellow_threshold):
                with open("potenital_yellows.csv" , "a") as out_file:
                    out_file.write(key + "\n")
        

    #red alerts
    red_alert_dates = []
    dates_array = []
    try:
        with open("potenital_reds.csv" , "r") as my_file:
            for line in my_file:
                dates_array.append(line.strip(' \t\n\r'))
        track = []
        for i in range(len(dates_array)-1):
            today = datetime.datetime.strptime(dates_array[i], '%Y-%m-%d')
            next = datetime.datetime.strptime(dates_array[i+1], '%Y-%m-%d')
            if((next - today).days == 1):
                if(today in track):
                    red_alert_dates.append(str(next).split(' ')[0])
                    track.append(next)
                else:
                    red_alert_dates.append(str(next).split(' ')[0])
                    track.append(today)
                    track.append(next)
    except:
        print("no red file")


    #yellow alerts
    yellow_alert_dates = []
    dates_array = []
    try:
        with open("potenital_yellows.csv" , "r") as my_file:
            for line in my_file:
                dates_array.append(line.strip(' \t\n\r'))
        track = []
        for i in range(len(dates_array)-1):
            today = datetime.datetime.strptime(dates_array[i], '%Y-%m-%d')
            next = datetime.datetime.strptime(dates_array[i+1], '%Y-%m-%d')
            if((next - today).days == 1):
                if(today in track):
                    if(str(next).split(' ')[0] not in red_alert_dates):
                        yellow_alert_dates.append(str(next).split(' ')[0])
                        track.append(next)
                else:
                    if(str(next).split(' ')[0] not in red_alert_dates):
                        yellow_alert_dates.append(str(next).split(' ')[0])
                        track.append(today)
                        track.append(next)
    except:
        print("no yellow file")
        
        
    os.system("rm potenital_reds.csv")
    os.system("rm potenital_yellows.csv")

    #Populate signal file
    alerts = {}
    alerts['nightsignal'] = []
    red_alerted = []
    yellow_alerted = []
    alertsDic = {}
    for key in red_alert_dates:
        alertsDic[key] = "2"
        red_alerted.append(key)
    for key in yellow_alert_dates:
        alertsDic[key] = "1"
        yellow_alerted.append(key)
    for key in date_hr_avgs_dic:
        if (key not in red_alerted) and (key not in yellow_alerted):
            alertsDic[key] = "0"
    sorted_alerts = collections.OrderedDict(sorted(alertsDic.items()))
    for key in sorted_alerts:
        alerts['nightsignal'].append({"date": key+"   "+"07:00:00", "val": str(sorted_alerts[key])})
    with open("NS-signals.json" , "w+") as out_file:
        json.dump(alerts, out_file)


################################# AppleWatch #################################

else:

    #Preprocess to get resting heartrate
    delta = datetime.timedelta(minutes=1)

    dateTimes = {}
    with open(step_file  , "r") as stepCSV:
        stepCSVReader = csv.DictReader(stepCSV)
        for step_rec in stepCSVReader:
            
                st_start_date = step_rec['Start_Date']
                st_start_time = step_rec['Start_Time']
                st_end_date = step_rec['End_Date']
                st_end_time = step_rec['End_Time']
                #We need to add handler for the other one
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

    with open('AW_rhr.csv' , "w") as rhrFile:
        rhrFile.write("Device,Start_Date,Start_Time,Value")
        with open(heartrate_file , "r") as hrCSV:
            hrCSVReader = csv.DictReader(hrCSV)
            for hr_rec in hrCSVReader:
                    hr_start_date = hr_rec['Start_Date']
                    hr_start_time = hr_rec['Start_Time']
                    hr_value = hr_rec['Heartrate']
                    if (hr_start_date in dateTimes):
                        arrayForThisDay = dateTimes[hr_start_date]
                        hr_time  = datetime.datetime.strptime( hr_start_time, '%H:%M:%S' )
                        if ( datetime.datetime.strftime(hr_time, '%H:%M') not in arrayForThisDay):
                            rhrFile.write(device + "," + hr_start_date + "," + hr_start_time + "," + hr_value + "\n")


    with open('AW_rhr.csv', "r") as hrFile:
        records = hrFile.readlines()

    date_hrs_dic = {}
    for record in records:
        if ("Device" not in record):
            record_elements = record.split(",")
            rec_date = record_elements[1]
            rec_time = record_elements[2]
            rec_hr = record_elements[3].strip(' \t\n\r')
            if ((rec_time.startswith("00:")) or (rec_time.startswith("01:")) or (rec_time.startswith("02:")) or (rec_time.startswith("03:")) or (rec_time.startswith("04:")) or (rec_time.startswith("05:")) or (rec_time.startswith("06:"))):
                if (rec_date not in date_hrs_dic):
                    date_hrs_dic[rec_date] = rec_hr
                else:
                    date_hrs_dic[rec_date] = date_hrs_dic[rec_date] + "*" + rec_hr

    #Calculate AVGs , Imputation, Healthy baseline Median, and Alerts
    date_hr_avgs_dic = {}
    for key in date_hrs_dic:
        AVGHR = 0
        temp = date_hrs_dic[key]
        numOfHRs = str(temp).count("*") + 1
        hrs = temp.split("*")
        for hr in hrs:
            AVGHR = AVGHR + int(float(hr))
        AVGHR = int(AVGHR/numOfHRs)
        date_hr_avgs_dic[key] = AVGHR

    missed_days_avg_dic = {}
    sorted_keys = sorted(date_hr_avgs_dic.keys())
    sorted_avgs = sorted(date_hr_avgs_dic.items())
    for i,v in enumerate(sorted_keys):
        if(i!=0 and i!=len(sorted_keys)-1):
            today = datetime.datetime.strptime(sorted_keys[i] , "%Y-%m-%d")
            nextDay = datetime.datetime.strptime(sorted_keys[i+1] , "%Y-%m-%d")
            prevDay = datetime.datetime.strptime(sorted_keys[i-1] , "%Y-%m-%d")
            if ( (nextDay-today).days==1 and (today-prevDay).days==2):
                missDate = today - datetime.timedelta(days=1)
                missed_days_avg_dic[missDate.strftime("%Y-%m-%d")] = round((date_hr_avgs_dic[sorted_keys[i]] + date_hr_avgs_dic[sorted_keys[i-1]])/2 , 1)
    for key in missed_days_avg_dic:
        if key not in date_hr_avgs_dic:
            date_hr_avgs_dic[key] = missed_days_avg_dic[key]
    temp = OrderedDict(sorted(date_hr_avgs_dic.items(), key=lambda t: t[0]))
    date_hr_avgs_dic = dict(temp)

    if(medianConfig == "MedianOfAvgs"):
        prev_keys_dic = {}
        for k1 in date_hr_avgs_dic:
            k1_prev_keys = []
            for k2 in date_hr_avgs_dic:
                if (k1>=k2):
                    k1_prev_keys.append(k2)
            prev_keys_dic[k1] = k1_prev_keys

        date_hr_meds_dic = {}
        for k in prev_keys_dic:
            list_for_med = []
            prev_keys = prev_keys_dic[k]
            for item in prev_keys:
                list_for_med.append(date_hr_avgs_dic[item])
            date_hr_meds_dic[k] = int(statistics.median(list_for_med))


    elif(medianConfig == "AbsoluteMedian"):
        live_dates_hrs_dic = {}
        for record in records:
            if ("Device" not in record):
                record_elements = record.split(",")
                rec_date = record_elements[1]
                rec_time = record_elements[2]
                rec_hr = record_elements[3].strip(' \t\n\r')
                if ((rec_time.startswith("00:")) or (rec_time.startswith("01:")) or (rec_time.startswith("02:")) or (rec_time.startswith("03:")) or (rec_time.startswith("04:")) or (rec_time.startswith("05:")) or (rec_time.startswith("06:"))):
                    if (rec_date not in live_dates_hrs_dic):
                        live_dates_hrs_dic[rec_date] = rec_hr
                    else:
                        live_dates_hrs_dic[rec_date] = live_dates_hrs_dic[rec_date] + "*" + rec_hr

        live_dates_hrs_dic_new = {}
        for key1 in live_dates_hrs_dic:
            live_dates_hrs_dic_new[key1] = ""
            temp = ""
            for key2 in live_dates_hrs_dic:
                if key1 >= key2:
                    if temp=="":
                        temp = live_dates_hrs_dic[key2]
                    else:
                        temp = temp + "*" + live_dates_hrs_dic[key2]
            live_dates_hrs_dic_new[key1] = temp

        date_hr_meds_dic = {}
        for key in live_dates_hrs_dic_new:
            MEDHR = 0
            temp = live_dates_hrs_dic_new[key]
            hrs = temp.split("*")
            med_list = []
            for hr in hrs:
                med_list.append(int(float(hr)))
            MEDHR = int(statistics.median(med_list))
            date_hr_meds_dic[key] = MEDHR


    for key in date_hr_avgs_dic:
        if (key in date_hr_meds_dic):
            if (date_hr_avgs_dic[key] >= date_hr_meds_dic[key] + red_threshold):
                with open("potenital_reds.csv" , "a") as out_file:
                    out_file.write(key + "\n")
            if (date_hr_avgs_dic[key] >= date_hr_meds_dic[key] + yellow_threshold):
                with open("potenital_yellows.csv" , "a") as out_file:
                    out_file.write(key + "\n")

    #red alerts
    red_alert_dates = []
    dates_array = []
    try:
        with open("potenital_reds.csv", "r") as my_file:
            for line in my_file:
                dates_array.append(line.strip(' \t\n\r'))
        track = []
        for i in range(len(dates_array)-1):
            today = datetime.datetime.strptime(dates_array[i], '%Y-%m-%d')
            next = datetime.datetime.strptime(dates_array[i+1], '%Y-%m-%d')
            if((next - today).days == 1):
                if(today in track):
                    red_alert_dates.append(str(next).split(' ')[0])
                    track.append(next)
                else:
                    red_alert_dates.append(str(next).split(' ')[0])
                    track.append(today)
                    track.append(next)
    except:
        print("no red file")


    #yellow alerts
    yellow_alert_dates = []
    dates_array = []
    try:
        with open("potenital_yellows.csv", "r") as my_file:
            for line in my_file:
                dates_array.append(line.strip(' \t\n\r'))
        track = []
        for i in range(len(dates_array)-1):
            today = datetime.datetime.strptime(dates_array[i], '%Y-%m-%d')
            next = datetime.datetime.strptime(dates_array[i+1], '%Y-%m-%d')
            if((next - today).days == 1):
                if(today in track):
                    if(str(next).split(' ')[0] not in red_alert_dates):
                        yellow_alert_dates.append(str(next).split(' ')[0])
                        track.append(next)
                else:
                    if(str(next).split(' ')[0] not in red_alert_dates):
                        yellow_alert_dates.append(str(next).split(' ')[0])
                        track.append(today)
                        track.append(next)
    except:
        print("no yellow file")

    os.system("rm potenital_reds.csv" )
    os.system("rm potenital_yellows.csv" )

    #Populate signal file
    alerts = {}
    alerts['nightsignal'] = []
    red_alerted = []
    yellow_alerted = []
    alertsDic = {}
    for key in red_alert_dates:
        alertsDic[key] = "2"
        red_alerted.append(key)
    for key in yellow_alert_dates:
        alertsDic[key] = "1"
        yellow_alerted.append(key)
    for key in date_hr_avgs_dic:
        if (key not in red_alerted) and (key not in yellow_alerted):
            alertsDic[key] = "0"
    sorted_alerts = collections.OrderedDict(sorted(alertsDic.items()))
    for key in sorted_alerts:
        alerts['nightsignal'].append({"date": key+"   "+"07:00:00", "val": str(sorted_alerts[key])})
    with open("NS-signals.json", "w+") as out_file:
        json.dump(alerts, out_file)



#################################  Plot  #################################
print("Plotting...")

figure = plt.gcf()
ax = plt.gca()


if (len(date_hr_avgs_dic.keys())>1):
    haveData = []
    allX = []
    min = 300
    max = 0
    for key in date_hr_avgs_dic:
        date_time_obj = datetime.datetime.strptime(key, '%Y-%m-%d')
        haveData.append(date_time_obj)
        allX.append(key)
        allX_value = date_hr_avgs_dic[key]
        if(int(date_hr_avgs_dic[key])<min):
            min = int(date_hr_avgs_dic[key])
        if(int(date_hr_avgs_dic[key])>max):
            max = int(date_hr_avgs_dic[key])

    date_set = set(haveData[0] + timedelta(x) for x in range((haveData[-1] - haveData[0]).days))
    missings = sorted(date_set - set(haveData))

    for missedDate in missings:
        allX.append(missedDate.strftime("%Y-%m-%d"))

    sorted_allX = sorted(allX)
    plt.plot(sorted_allX, range(len(sorted_allX)) , color='white')

    #plot average rhr per night
    sorted_res = sorted(date_hr_avgs_dic.items())
    x, y = zip(*sorted_res)
    plt.plot(x, y , color='black' ,  marker='o' ,  markersize=2.5 , linewidth=1.5, label="Avg RHR over night")

    #plot average rhr per night for missing nights
    sorted_res = sorted(missed_days_avg_dic.items())
    if(len(missed_days_avg_dic)!=0):
        x, y = zip(*sorted_res)
        plt.plot(x, y , color='white' , marker='o' , linestyle='' , markersize=3 , markerfacecolor='gray' , markeredgecolor='gray' , label="Imputed Avg RHR \n over night")

    #plot median rhr per night
    sorted_res = sorted(date_hr_meds_dic.items())
    x, y = zip(*sorted_res)
    plt.plot(x, y , color='green' , linewidth=1.5 , linestyle='dashed', label="Med RHR over night")

    #plot yellow threshold
    date_hr_meds_dic_plus2 = {}
    for key in date_hr_meds_dic:
        date_hr_meds_dic_plus2[key] = date_hr_meds_dic[key] + yellow_threshold
    sorted_res = sorted(date_hr_meds_dic_plus2.items())
    x, y = zip(*sorted_res)
    plt.plot(x, y , color='yellow' , linewidth=1 , linestyle='dashed', label="Med RHR over night + 3")


    #plot red threshold
    date_hr_meds_dic_plus3 = {}
    for key in date_hr_meds_dic:
        date_hr_meds_dic_plus3[key] = date_hr_meds_dic[key] + red_threshold
    sorted_res = sorted(date_hr_meds_dic_plus3.items())
    x, y = zip(*sorted_res)
    plt.plot(x, y , color='red' , linewidth=1 , linestyle='dashed', label="Med RHR over night + 4")


    #find consecutive red and yellow days
    red_and_yellow_alert_dates = []
    for d1 in red_alert_dates:
            red_and_yellow_alert_dates.append(d1)
    for d2 in yellow_alert_dates:
        if d2 not in red_and_yellow_alert_dates:
            red_and_yellow_alert_dates.append(d2)
    sorted_red_and_yellow_alert_dates = sorted(red_and_yellow_alert_dates)

    clustered_alerts = {}
    cluster_counter = 0
    for g in consecutive_groups(sorted_red_and_yellow_alert_dates, lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').toordinal()):
        temp = list(g)
        if(len(temp)>=3):
            clustered_alerts[str(cluster_counter)] = temp
            cluster_counter = cluster_counter + 1

    #handle one label for all clustered alerts
    haveClustered = 0
    for key in clustered_alerts:
            clustered_alerts_dic = {}
            for d in clustered_alerts[key]:
                clustered_alerts_dic[d] = date_hr_avgs_dic[d]
            sorted_res = sorted(clustered_alerts_dic.items())
            if(len(clustered_alerts_dic)!=0):
                if(haveClustered==1):
                    x, y = zip(*sorted_res)
                    plt.plot(x, y , color='salmon' , linestyle='-' , linewidth=3)
                else:
                    haveClustered = 1
                    x, y = zip(*sorted_res)
                    plt.plot(x, y , color='salmon' , linestyle='-' , linewidth=3 , label="Clustered alerts \n (>3 consecutive alerts)" )


    #plot red alerts
    red_alerts_dic = {}
    for d in red_alert_dates:
            red_alerts_dic[d] = date_hr_avgs_dic[d]
    sorted_res = sorted(red_alerts_dic.items())
    if(len(red_alerts_dic)!=0):
        for key in red_alerts_dic:
            plt.axvline(x=key , linestyle='-' , color='red' , linewidth=1)
        x, y = zip(*sorted_res)
        plt.plot(x, y , color='white' , marker='o' , linestyle='' , markersize=3.5 , markerfacecolor='red' , markeredgecolor='red' , label="Red alert")


    #plot yellow alerts
    yellow_alerts_dic = {}
    for d in yellow_alert_dates:
            yellow_alerts_dic[d] = date_hr_avgs_dic[d]
    sorted_res = sorted(yellow_alerts_dic.items())
    if(len(yellow_alerts_dic)!=0):
        for key in yellow_alerts_dic:
            plt.axvline(x=key , linestyle='-' , color='orange' , linewidth=1)
        x, y = zip(*sorted_res)
        plt.plot(x, y , color='white' , marker='o' , linestyle='' , markersize=3.5 , markerfacecolor='yellow' , markeredgecolor='yellow', label="Yellow alert")


    #Title & Symptom Onset & Save plot
    plt.xticks(rotation=90)
    plt.ylim(int(min-1), int(max+1))
    h = plt.ylabel('Resting\n heart rate\n over night' , fontsize=12)
    plt.xlabel('    Day' , fontsize=12)
    h.set_rotation(90)
    plt.yticks(np.arange(round10Base(min), round10Base(max), 10))

    for index, label in enumerate(ax.xaxis.get_ticklabels()):
            if index % 3 == 0 :
                label.set_visible(True)
            else :
                label.set_visible(False)

    #uncomment for legend
    #lgd = ax.legend(prop={'size': 8.5}, bbox_to_anchor= (1.0, 1.0), loc="upper left", frameon=False)
    plt.grid(False)
    ax.spines["bottom"].set_color('black')
    ax.spines["bottom"].set_linewidth(1.5)
    ax.spines["top"].set_color('black')
    ax.spines["top"].set_linewidth(1.5)
    ax.spines["right"].set_color('black')
    ax.spines["right"].set_linewidth(1.5)
    ax.spines["left"].set_color('black')
    ax.spines["left"].set_linewidth(1.5)

    figure = plt.gcf()
    figure.set_size_inches(16, 2.5)

    plt.savefig("NightSignalResult" +'.pdf', dpi=300, bbox_inches = "tight")
    plt.close()
