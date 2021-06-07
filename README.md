# wearable-infection
Real-time detection of infection diseases using wearables

# NightSignal Algorithm:
Online pre-symptomatic and asymptomatic detection of COVID-19 using wearables data. The current version of NightSignal algorithm works on Fitbit and AppleWatch heartrate and steps data.

## Usage

**Command:**

Fitbit:

``` python3 nightsignal.py --device=Fitbit --restinghr=<RHR_FILE> ```

AppleWatch:

``` python3 nightsignal.py --device=AppleWatch  --heartrate=<HR_FILE> --step=<STEP_FILE> ```


**Examples:**

`python3 nighsignal.py --device=AppleWatch --heartrate=P355472-AppleWatch-hr.csv  --step=P355472-AppleWatch-st.csv`

`python3 nighsignal.py --device=Fitbit --restinghr=P682517-Fitbit-rhr.csv`

