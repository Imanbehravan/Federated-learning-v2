import ipfshttpclient
import json


def writejsonfile(path, data):
    json_object = json.dumps(data, indent=4)
    with open(path, "w") as outfile:
        outfile.write(json_object)

def writeipfs(path, clientID):
    client = ipfshttpclient.connect(clientID)
    result = client.add(path)
    return result["Hash"]

def readFromIPFS(Hash, clientID, path):
    client = ipfshttpclient.connect(clientID)
    data = client.get(Hash, path)


