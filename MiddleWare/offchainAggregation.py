import numpy as np
import json
import time
from Data2IPFS import writeipfs
from MiddleWare.centralAggregator import *


class offChainAggregationClient:

    def __init__(self, config_file):
        ################### connecting to server. this part should be revised based on the remote server which hosts the aggregator
        self.config = config_file
        self.precision = None
        self.updateRound = 0
        dataDictionary = {}
        deviceData = {"weights": [], "bias": []}
        device_num = self.config["DEFAULT"]["NumberOfParticipants"]
        for i in range(device_num):
            deviceName = "Device_" + str(i + 1)
            dataDictionary[deviceName] = deviceData
        dataDictionary["global_weights"] = []
        dataDictionary["global_bias"] = []
        dataDictionary["RoundNumber"] = 1
        dataDictionary["temp_global_weights"] = []
        dataDictionary["temp_global_bias"] = []
        dataDictionary["Round_start_time_stamp"] = 0
        dataDictionary["participating_devices"] = []
        dataDictionary["initialized"] = False
        dataDictionary["learningRate"] = self.config["DEFAULT"]["LearningRate"]
        dataDictionary["precision"] = self.config["DEFAULT"]["Precision"]
        dataDictionary["batchSize"] = self.config["DEFAULT"]["BatchSize"]
        json_object = json.dumps(dataDictionary, indent=4)
        with open("DeviceUpdates.json", "w") as outfile:
            outfile.write(json_object)

    def init_aggregator(self, accountNR):

        if (accountNR == 0):
            np.random.seed(4)
            weights = np.random.randn(self.config["DEFAULT"]["OutputDimension"],self.config["DEFAULT"]["InputDimension"]) * self.config["DEFAULT"]["Precision"] / 5
            bias = np.random.randn(self.config["DEFAULT"]["OutputDimension"], ) * self.config["DEFAULT"]["Precision"] / 5
            weights = [[int(x) for x in y] for y in weights]
            bias = [int(x) for x in bias]
            ################### connecting to server. this part should be revised based on the remote server which hosts the aggregator
            initModel(weights, bias)


    def get_RoundNumber(self, accountNR):
        ################### connecting to server. this part should be revised based on the remote server which hosts the aggregator
        return getRoundNumber()

    def round_UpdateOutstanding(self, deviceName):
        ################### connecting to server. this part should be revised based on the remote server which hosts the aggregator
        return roundUpdateOutstanding(deviceName, self.config)



    def get_globalWeights(self):
        ################### connecting to server. this part should be revised based on the remote server which hosts the aggregator
        return getGlobalWeights()

    def get_globalBias(self):
        ################### connecting to server. this part should be revised based on the remote server which hosts the aggregator
        return getGlobalBias()

    def get_LearningRate(self):
        ################### connecting to server. this part should be revised based on the remote server which hosts the aggregator
        return getLearningRate()

    def get_Precision(self):
        ################### connecting to server. this part should be revised based on the remote server which hosts the aggregator
        return getPrecision()

    def get_BatchSize(self):
        ################### connecting to server. this part should be revised based on the remote server which hosts the aggregator
        return getBatchSize()


    def update(self, weights, bias, accountNR, deviceName, round, proof=None):
        if self.config["DEFAULT"]["PerformProof"]:
            IPFSFileHash = self.__update_with_proof(weights, bias, accountNR, deviceName, round, proof)
            print("nothing yet")
        else:
            IPFSFileHash = self.__update_without_proof(weights, bias, accountNR, deviceName, round)

        return IPFSFileHash

    def __update_without_proof(self, weights, bias, accountNR, deviceName, round):
        weights = [[int(x) for x in y] for y in weights]
        bias = [int(x) for x in bias]
        IPFSdata = self.config["DEFAULT"]["IPFSDataPath"] + deviceName + '.json'
        data_dictionary = {
            "weights": weights,
            "bias": bias,
            "round": round
        }
        json_object = json.dumps(data_dictionary, indent=4)
        with open(IPFSdata, "w") as outfile:
            outfile.write(json_object)
        IPFSFileHash = writeipfs(IPFSdata, self.config["DEFAULT"]["IPFSclientID"])

        ################### connecting to server. this part should be revised based on the remote server which hosts the aggregator

        updateWithoutProof(weights, bias, deviceName)
        return IPFSFileHash

    def __update_with_proof(self, weights, bias, accountNR, deviceName, round, proof):
        print("nothing yet")
        updateWithProof(weights, bias, proof)