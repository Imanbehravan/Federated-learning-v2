import sys
import threading
import time
from MiddleWare.BlockChainClientV2 import BlockChainConnection
from MiddleWare.offchainAggregation import offChainAggregationClient
from utils.utils import read_yaml
from Edge_Device.EdgeDevice import EdgeDevice
from MiddleWare.MiddlewareV2 import MiddleWareV2


def start_Device(deviceName, accountNr, blockchain_connection, config_file, neural_method, roundNumber, deviceNumber):
    edgeDevice = EdgeDevice(deviceName, config_file=config_file)
    thread = threading.Thread(target=edgeDevice.start_EdgeDevice)
    thread.start()
    #edgeDevice.start_EdgeDevice()
    middleware = MiddleWareV2(neural_method, blockchain_connection, deviceName, accountNr, config_file)
    middleware.start_MiddlewareV2()

if __name__ == "__main__":
    config_file = read_yaml("IMAN_CONFIG_2.yaml")
    neural_method = config_file["DEFAULT"]["NeuralNetworkPackage"]  # 1 = scikit learn, 2 = pytorch
    # connection is used instead of blockchain_connection
    connection = BlockChainConnection(config_file=config_file)
    connection.connect()
    #start_Device("Device_" + str(1), 0, connection, config_file, neural_method, 0, 1)
    for i in range(config_file["DEFAULT"]["NumberOfParticipants"]):
        thread = threading.Thread(target=start_Device, args=["Device_" + str(i + 1), i, connection, config_file, neural_method, 0, i + 1])
        thread.start()
        time.sleep(1)
        #start_Device("Device_" + str(i + 1), i, connection, config_file, neural_method, 0, i + 1)