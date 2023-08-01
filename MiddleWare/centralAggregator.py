import json
import time
import numpy as np


def initModel(weights, bias):
    with open("DeviceUpdates.json", "r") as dataFile:
        fileContent = json.load(dataFile)

    dataFile.close()
    fileContent["global_weights"] = weights
    fileContent["global_bias"] = bias
    fileContent["temp_global_weights"] = weights
    fileContent["temp_global_bias"] = bias
    fileContent["initialized"] = True
    fileContent["Round_start_time_stamp"] = time.time()
    jsonString = json.dumps(fileContent)
    jsonFile = open("DeviceUpdates.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()

def getBatchSize():
    with open("DeviceUpdates.json", "r") as dataFile:
        fileContent = json.load(dataFile)
    dataFile.close()
    return fileContent["batchSize"]

def getPrecision():
    with open("DeviceUpdates.json", "r") as dataFile:
        fileContent = json.load(dataFile)
    dataFile.close()
    return fileContent["precision"]

def getLearningRate():
    with open("DeviceUpdates.json", "r") as dataFile:
        fileContent = json.load(dataFile)
    dataFile.close()
    return fileContent["learningRate"]

def getGlobalBias():
    with open("DeviceUpdates.json", "r") as dataFile:
        fileContent = json.load(dataFile)
    dataFile.close()
    return fileContent["global_bias"]

def getGlobalWeights():
    with open("DeviceUpdates.json", "r") as dataFile:
        fileContent = json.load(dataFile)
    dataFile.close()
    return fileContent["global_weights"]

def getRoundNumber():
    with open("DeviceUpdates.json", "r") as dataFile:
        fileContent = json.load(dataFile)
    dataFile.close()
    return fileContent["RoundNumber"]

def updateWithProof(weights, bais, proof):
    print("nothing yet")

def updateWithoutProof(weights, bias, deviceName):
    with open("DeviceUpdates.json", "r") as dataFile:
        fileContent = json.load(dataFile)
    dataFile.close()
    participatingDevices = fileContent["participating_devices"]
    if (len(participatingDevices) == 0):
        fileContent["participating_devices"].append(deviceName)
        jsonString = json.dumps(fileContent)
        jsonFile = open("DeviceUpdates.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
        movingAverageWeights(weights)
        movingAverageBias(bias)
        iman_break_point = 15
    else:
        newUser = True
        for i in participatingDevices:
            if deviceName == i:
                newUser = False
        if newUser:
            fileContent["participating_devices"].append(deviceName)
            jsonString = json.dumps(fileContent)
            jsonFile = open("DeviceUpdates.json", "w")
            jsonFile.write(jsonString)
            jsonFile.close()
            movingAverageWeights(weights)
            movingAverageBias(bias)
            iman_break_point = 16

def movingAverageWeights(weights):
    with open("DeviceUpdates.json", "r") as dataFile:
        fileContent = json.load(dataFile)
    dataFile.close()
    participatingCount = len(fileContent["participating_devices"])
    if (participatingCount == 1):
        fileContent["temp_global_weights"] = weights
        jsonString = json.dumps(fileContent)
        jsonFile = open("DeviceUpdates.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
    else:
        currentWeights = np.array(fileContent["temp_global_weights"])
        deviceWeights = np.array(weights)
        newWeights = currentWeights + deviceWeights
        fileContent["temp_global_weights"] = newWeights.tolist()
        jsonString = json.dumps(fileContent)
        jsonFile = open("DeviceUpdates.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()

def movingAverageBias(bias):
    with open("DeviceUpdates.json", "r") as dataFile:
        fileContent = json.load(dataFile)
    dataFile.close()
    participatingCount = len(fileContent["participating_devices"])
    if (participatingCount == 1):
        fileContent["temp_global_bias"] = bias
        jsonString = json.dumps(fileContent)
        jsonFile = open("DeviceUpdates.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
    else:
        currentBias = np.array(fileContent["temp_global_bias"])
        deviceBias = np.array(bias)
        newBias = currentBias + deviceBias
        fileContent["temp_global_bias"] = newBias.tolist()
        jsonString = json.dumps(fileContent)
        jsonFile = open("DeviceUpdates.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()

def roundUpdateOutstanding(deviceName, config):
    with open("DeviceUpdates.json", "r") as dataFile:
        fileContent = json.load(dataFile)
    dataFile.close()
    isInitiallized = fileContent["initialized"]
    if isInitiallized:
        newRound = True
        for device in fileContent["participating_devices"]:
            if (deviceName == device):
                newRound = False

        if (newRound == False):
            endUpdateRound(config)
        newRoundRefreshed = True
        with open("DeviceUpdates.json", "r") as dataFile:
            fileContent = json.load(dataFile)
        dataFile.close()
        for device in fileContent["participating_devices"]:
            if (deviceName == device):
                newRoundRefreshed = False
        if ((newRoundRefreshed == True) & (newRound == False)):
            return newRoundRefreshed
        else:
            return newRound
    else:
        False
    
def endUpdateRound(config):
    now = time.time()
    ################### connecting to server. this part should be revised based on the remote server which hosts the aggregator
    with open("DeviceUpdates.json", "r") as dataFile:
        fileContent = json.load(dataFile)
    dataFile.close()
    roundStartTimeStamp = fileContent["Round_start_time_stamp"]
    updateInterval = config["DEFAULT"]["IntervalTime"]
    if ((now - roundStartTimeStamp) > updateInterval):
        tempAverageWeights = np.array(fileContent["temp_global_weights"])/len(fileContent["participating_devices"])
        tempAverageBias = np.array(fileContent["temp_global_bias"])/len(fileContent["participating_devices"])
        fileContent["global_weights"] = tempAverageWeights.tolist()
        fileContent["global_bias"] = tempAverageBias.tolist()
        fileContent["RoundNumber"] += 1
        fileContent["Round_start_time_stamp"] = time.time()
        fileContent["participating_devices"] = []
        jsonString = json.dumps(fileContent)
        jsonFile = open("DeviceUpdates.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()


    
