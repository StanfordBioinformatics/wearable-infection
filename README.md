# wearable-infection
Real-time detection of infection diseases using wearables

# NightSignal Algorithm:
Online pre-symptomatic and asymptomatic detection of COVID-19 using wearables data. The current version of NightSignal algorithm works on Fitbit and AppleWatch heartrate and steps data.

**Usage**
Command:

Fitbit:
``` python3 nightsignal.py --device=Fitbit --restinghr=<RHR_FILE> ```

AppleWatch:
``` python3 nightsignal.py --device=AppleWatch  --heartrate=<HR_FILE> --step=<STEP_FILE> ```

