from Data2IPFS import readFromIPFS
import json

hash = "QmdWn9Q9tvsuNxtFWaKF7AyvxNUMwgf8LU5kPMaQ6cyShz"

path = "/home/iman/projects/kara/blockchain_based_Federated_learning/federatedlearning/codes/Devices/IPFSStorage"

ipfsClientID = "/ip4/127.0.0.1/tcp/5001/http"

data = readFromIPFS(hash, ipfsClientID, path)

FilePath = path + '/' + hash

f = open(FilePath)

data = json.load(f)

print("finish")