import os
import pandas as pd
import time
from MessageBroker.Publisher import Publisher
from utils.utils import read_yaml


class EdgeDevice:
    def __init__(self,DeviceName,config_file):
        self.config=config_file
        # main code
        self.datasource=os.path.join(os.path.join(self.config["DEFAULT"]["TrainFilePath"],DeviceName+"/device_geneExpression_trainData.txt"))

        # Iman code
        # self.datasource = os.path.join(
        #     os.path.join(self.config["DEFAULT"]["TrainFilePath"], DeviceName+'/Iman_Data'))
        ######################
        print(self.datasource)
        self.publisher=Publisher()
        self.queueName=self.config["DEFAULT"]["QueueBase"]+DeviceName
        self.publisher.declare_queue(self.queueName)
        self.data=None
        ## main code
        self.init_dataset()


        ## iman code
        ##self.init_dataset_Iman()
        iman_breakpoint = 2

    def init_dataset_Iman(self):
        self.data = pd.read_csv(self.datasource, names=["f1", "f2", "f3", "Activity"])
        self.data.fillna(inplace=True, method='backfill')
        self.data.dropna(inplace=True)

    def init_dataset(self):
        ## loading digital sport data
        # self.data = pd.read_csv(
        #     self.datasource, sep=' ', names=
        #     ["T_xacc", "T_yacc", "T_zacc", "T_xgyro", "T_ygyro", "T_zgyro", "T_xmag", "T_ymag", "T_zmag",
        #      "RA_xacc", "RA_yacc", "RA_zacc", "RA_xgyro", "RA_ygyro", "RA_zgyro", "RA_xmag", "RA_ymag", "RA_zmag",
        #      "LA_xacc", "LA_yacc", "LA_zacc", "LA_xgyro", "LA_ygyro", "LA_zgyro", "LA_xmag", "LA_ymag", "LA_zmag",
        #      "RL_xacc", "RL_yacc", "RL_zacc", "RL_xgyro", "RL_ygyro", "RL_zgyro", "RL_xmag", "RL_ymag", "RL_zmag",
        #      "LL_xacc", "LL_yacc", "LL_zacc", "LL_xgyro", "LL_ygyro", "LL_zgyro", "LL_xmag", "LL_ymag", "LL_zmag",
        #      "Activity"]
        #             )
        # self.data.fillna(inplace=True, method='backfill')
        # self.data.dropna(inplace=True)
        # self.data.drop(columns= ["T_xacc", "T_yacc", "T_zacc", "T_xgyro","T_ygyro","T_zgyro","T_xmag", "T_ymag", "T_zmag","RA_xacc", "RA_yacc", "RA_zacc", "RA_xgyro","RA_ygyro","RA_zgyro","RA_xmag", "RA_ymag", "RA_zmag","RL_xacc", "RL_yacc", "RL_zacc", "RL_xgyro","RL_ygyro","RL_zgyro" ,"RL_xmag", "RL_ymag", "RL_zmag","LL_xacc", "LL_yacc", "LL_zacc", "LL_xgyro","LL_ygyro","LL_zgyro" ,"LL_xmag", "LL_ymag", "LL_zmag"],inplace=True)
        # activity_mapping = self.config["DEFAULT"]["ActivityMappings"]
        # activity_encoding = self.config["DEFAULT"]["ActivityEncoding"]
        # filtered_activities = self.config["DEFAULT"]["Activities"]
        # for key in activity_mapping.keys():
        #     self.data.loc[ self.data['Activity'] == key,'Activity'] = activity_mapping[key]
        # self.data = self.data[self.data['Activity'].isin(filtered_activities)]
        # for key in activity_encoding.keys():
        #     self.data.loc[self.data['Activity'] == key, 'Activity'] = activity_encoding[key]
        #     iman_break_point = 16
        ## loading gene expression data (data preparation should be done outside)
        columnNames = []
        numDim = self.config["DEFAULT"]["InputDimension"]



        for i in range(numDim):
            text = f'feature_{i}'
            columnNames.append(text)
        columnNames.append("Activity")
        self.data = pd.read_csv(
            self.datasource, sep=',', names=columnNames)


        iman_break_point = 17


    def next_batch(self):
        p=self.config["DEFAULT"]["NumberOfSamplesGenerated"]
        batch=self.data.sample(p)
        return batch

    def start_EdgeDevice(self):

        ## iman code
        # nextbatch = self.next_batch()
        # self.publisher.publish_data(self.queueName,nextbatch.to_csv())
        # time.sleep(float(self.config["DEFAULT"]["IntervalDataGenerator"]))

        # main code
        while True:
            nextbatch=self.next_batch()
            self.publisher.publish_data(self.queueName,nextbatch.to_csv())
            time.sleep(float(self.config["DEFAULT"]["IntervalDataGenerator"]))
    def y_name(self):
        return "Activity"

