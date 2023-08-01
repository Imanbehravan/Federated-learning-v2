import pandas as pd
import numpy as np

numOfDevices = 6
numOfActivities = 19
numOfDatapoints = 5
i = 1

while i<=numOfDevices:
    j = 1
    data = pd.DataFrame()
    outputpath = f'Device_Data/Device_{i}/' + 'device_data_new.txt'
    while j <= numOfActivities:
        k = 1
        while k <= 60:
            if (j<10)&(k<10):
                path = f'data/a0{j}/p{i}/s0{k}' + '.txt'
            elif ((j<10)&(k>=10)):
                path = f'data/a0{j}/p{i}/s{k}' + '.txt'
            elif (j>=10)&(k<10):
                path = f'data/a{j}/p{i}/s0{k}' + '.txt'
            else:
                path = f'data/a{j }/p{i}/s{k}' + '.txt'

            activityData = pd.read_csv(
                path, names=
                ["T_xacc", "T_yacc", "T_zacc", "T_xgyro", "T_ygyro", "T_zgyro", "T_xmag", "T_ymag", "T_zmag",
                 "RA_xacc", "RA_yacc", "RA_zacc", "RA_xgyro", "RA_ygyro", "RA_zgyro", "RA_xmag", "RA_ymag", "RA_zmag",
                 "LA_xacc", "LA_yacc", "LA_zacc", "LA_xgyro", "LA_ygyro", "LA_zgyro", "LA_xmag", "LA_ymag", "LA_zmag",
                 "RL_xacc", "RL_yacc", "RL_zacc", "RL_xgyro", "RL_ygyro", "RL_zgyro", "RL_xmag", "RL_ymag", "RL_zmag",
                 "LL_xacc", "LL_yacc", "LL_zacc", "LL_xgyro", "LL_ygyro", "LL_zgyro", "LL_xmag", "LL_ymag", "LL_zmag",
                 ]
            )
            activityData["Activity"] = j
            data = [data,activityData]
            data = pd.concat(data)
            k = k + 1
        j = j+1
    np.savetxt(outputpath, data.values[np.random.randint(len(data), size = 1000), :], fmt='%f', delimiter=' ')
    i = i+1

