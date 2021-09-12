# IsolationForest Algorithm:

A version of Isolation Forest Anomaly Detection algorithm can be found in `isolationforest` folder. To apply this algorithm, please run the follwoing command line:

> Fitbit:

> ``` python3 isolationforest.py --device=Fitbit  --heartrate=<HR_FILE> --step=<STEP_FILE> ```

> AppleWatch:

> ``` python3 isolationforest.py --device=AppleWatch  --heartrate=<HR_FILE> --step=<STEP_FILE> ```

Similar to NightSignal algorithm, the RHRs are resampled by daily average (24h) resolution. 
The contamination factor is set to "auto" by default. 
Finally, the result (alerts) can be found in the output file: `if_anomalies.csv`. Points labeled with "yes" are anomalies. 
