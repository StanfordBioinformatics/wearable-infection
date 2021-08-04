# wearable-infection
Real-time detection of infection diseases using wearables



<img src="images/NightSignal_Icon.png" width="272.8" height="262.4">

# NightSignal Algorithm:
Online pre-symptomatic and asymptomatic detection of COVID-19 using wearables data. The current version of NightSignal algorithm works on Fitbit and AppleWatch heart rate and steps data.

**Preprocessing:**
Given the heart rate and step data (e.g., P355472-AppleWatch-hr.csv and P355472-AppleWatch-st.csv files), the resting heart rate (RHR) overnight is calculated for each day by averaging the heart rate values where the corresponding step value is zero (i.e. minute resolution in the case of Fitbit and various ranges - e.g., 5 or 15 minutes - in the case of Apple Watch). 

**Healthy baseline:**
The healthy basline for each indivicdual is calculated as the median of average RHR overnight.

**Generating alerts:**
After the healthy baseline is established, the alerts are generated using the following deterministic finite state machine:


## Requirements and Usage

**Requirements:**
- Python 3
- MatplotLib
- NumPy
- Pandas

**Required packages command:**

Use the following command to install the required Python packages

  ```pip install -r requirements.txt```

<br/>
<br/>

**Usage:**

  For each wearable, use the following command to run NightSignal algorithm on heart rate and step data. The outputs are: 1) A JSON file for the real-time alerts and 2) A plot showing the average RHR overnight and corresponding healthy baseline and alerts w.r.t the NightSignal Deterministic Finite Automata (DFA).    

> Fitbit:

> ``` python3 nightsignal.py --device=Fitbit --restinghr=<RHR_FILE> ```

> AppleWatch:

> ``` python3 nightsignal.py --device=AppleWatch  --heartrate=<HR_FILE> --step=<STEP_FILE> ```

<br/>
<br/>

**Example runs:**

`python3 nightsignal.py --device=AppleWatch --heartrate=P355472-AppleWatch-hr.csv  --step=P355472-AppleWatch-st.csv`

`python3 nightsignal.py --device=Fitbit --restinghr=P682517-Fitbit-rhr.csv`

<br/>
<br/>

**Output example:**

Example of Pre-symptoms Real-time Alerts during COVID-19:  

<img src="images/sample_output.png" width="400" height="250">
