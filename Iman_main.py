import sys
import threading
import time
from MiddleWare.BlockChainClient import BlockChainConnection
from MiddleWare.offchainAggregation import offChainAggregationClient
from utils.utils import read_yaml
from Edge_Device.EdgeDevice import EdgeDevice
from MiddleWare.Middleware import MiddleWare

def start_Device(deviceName, accountNr, blockchain_connection, config_file, neural_method, aggregation_method, roundNumber, deviceNumber):
    if (config_file["DEFAULT"]["RunningMode"] == "parallel"):
        edgeDevice = EdgeDevice(deviceName, config_file=config_file)
        thread = threading.Thread(target=edgeDevice.start_EdgeDevice)
        thread.start()
        middleware = MiddleWare(neural_method, aggregation_method, blockchain_connection, deviceName, accountNr, config_file)
        middleware.start_Middleware()

    if (config_file["DEFAULT"]["RunningMode"] == "serial"):
        edgeDevice = EdgeDevice(deviceName, config_file=config_file)
        middleware = MiddleWare(neural_method, aggregation_method, blockchain_connection, deviceName, accountNr, config_file)
        middleware.start_Middleware_serial(roundNumber, edgeDevice, deviceNumber)

if __name__ == '__main__':
    config_file = read_yaml("IMAN_CONFIG_2.yaml")
    neural_method = config_file["DEFAULT"]["NeuralNetworkPackage"] # 1 = scikit learn, 2 = pytorch
    aggregation_method = config_file["DEFAULT"]["Aggregation"]
    if (aggregation_method == "on-chain"):
        # connection is used instead of blockchain_connection
        connection=BlockChainConnection(config_file=config_file)
        connection.connect()


    if (aggregation_method == "off-chain"):
        connection = offChainAggregationClient(config_file=config_file)

    # this part is added by Iman to enable the code to run the process in serial rather than parallel
    if (config_file["DEFAULT"]["RunningMode"] == "serial"):
        for j in range(config_file["DEFAULT"]["Rounds"]):
            for i in range(config_file["DEFAULT"]["NumberOfParticipants"]):
                start_Device("Device_" + str(i+1), i, connection, config_file, neural_method, aggregation_method, j+1, i+1)
        print("process finished")

    if (config_file["DEFAULT"]["RunningMode"] == "parallel"):
        for i in range(config_file["DEFAULT"]["NumberOfParticipants"]):
            thread=threading.Thread(target= start_Device,args=["Device_"+str(i+1),i,connection,config_file, neural_method, aggregation_method, 0, i+1])
            thread.start()
            time.sleep(1)

