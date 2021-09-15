# IsolationForest Algorithm:

<img src="../images/IsolationForest_Icon.png" width="270.8" height="270.8">

Isolation Forest Anomaly Detection algorithm for wearables data: Fitbit and Apple Watch. To run this algorithm, you can easily run the follwoing command line:

> Fitbit:

> ``` python3 isolationforest.py --device=Fitbit  --heartrate=<HR_FILE> --step=<STEP_FILE> ```

> AppleWatch:

> ``` python3 isolationforest.py --device=AppleWatch  --heartrate=<HR_FILE> --step=<STEP_FILE> ```

Similar to <b>NightSignal</b> algorithm, the resting heart rate overnight data is resampled by daily average (24h) resolution.

The contamination factor is set to "auto" by default and can be customized (e.g., 0.095).

Finally, the result (alerts) is generated in the output file: `if_anomalies.csv`. Points labeled with "yes" are anomalies. 
