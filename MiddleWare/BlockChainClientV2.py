import threading
import time

import numpy as np
from web3 import Web3
from utils.utils import read_yaml
import json
from Data2IPFS import writejsonfile
from Data2IPFS import writeipfs
import subprocess

class BlockChainConnection:
    def __init__(self,config_file):
        self.config = config_file
        self.web3Connection=None
        self.FLcontractABI=None
        self.FLcontractDeployed=None
        self.FLcontractAddress=self.config["DEFAULT"]["FLContractAddress"]
        self.lock_newRound=threading.Lock()
        self.precision=None

    def connect(self):
        self.web3Connection=Web3(Web3.HTTPProvider(self.config["DEFAULT"]["EtheriumRPCServer"],request_kwargs={'timeout': 60*10}))
        with open(self.config["DEFAULT"]["FLContractABIPAth"]) as f:
            ##self.FLcontractABI=json.load(f)["abi"]
            self.FLcontractABI = json.load(f)
        self.FLcontractDeployed=self.web3Connection.eth.contract(address=self.FLcontractAddress,abi=self.FLcontractABI)

    def register(self,accountNR, device_name):
        if self.is_connected():
             try:
                 thxHash= self.FLcontractDeployed.functions.register().transact({"from": self.web3Connection.eth.accounts[accountNR]})
                 self.__await_Trainsaction(thxHash)
                 print("registration of " + device_name + " successfully done")
             except:
                print("registeration of " + device_name + " failed")
             #thxHash= self.FLcontractDeployed.functions.map_temp_to_global().transact({"from": self.web3Connection.eth.accounts[accountNR]})
             #self.__await_Trainsaction(thxHash)
             #thxHash = self.FLcontractDeployed.functions.updateVerifier(self.config["DEFAULT"]["VerifierContractAddress"]).transact({"from": self.web3Connection.eth.accounts[0]})
             #self.__await_Trainsaction(thxHash)

    def __check_ZKP(self,proof,accountNR):
         a=proof['proof']['a']
         a=[Web3.toInt(hexstr=x) for x in a]
         b=proof['proof']['b']
         b=[[Web3.toInt(hexstr=x) for x in y] for y in b ]
         c=proof['proof']['c']
         c=[Web3.toInt(hexstr=x) for x in c]
         inputs = proof['inputs']
         inputs = [Web3.toInt(hexstr=x) for x in inputs]
         #istrue= self.FLcontractDeployed.functions.checkZKP(a,b,c, inputs).call({"from": self.web3Connection.eth.accounts[accountNR]})
         #print(f"AccountNr = {accountNR}: ZKP went through",istrue)
         return a,b,c,inputs


    def __await_Trainsaction(self,thxHash):
        self.web3Connection.eth.wait_for_transaction_receipt(thxHash)

    def is_connected(self):
        return self.web3Connection.isConnected()

    def get_LearningRate(self,accountNR):
        self.precision=self.__get_Precision(accountNR)
        lr=self.FLcontractDeployed.functions.getLearningRate().call({"from":self.web3Connection.eth.accounts[accountNR]})
        return lr

    def __get_Precision(self,accountNR):
        return self.FLcontractDeployed.functions.getPrecision().call({"from":self.web3Connection.eth.accounts[accountNR]})

    def get_InputDimension(self,accountNR):
        return self.FLcontractDeployed.functions.getInputDimension().call({"from":self.web3Connection.eth.accounts[accountNR]})

    def get_Epochs(self,accountNR):
        return self.config["DEFAULT"]["Epochs"]

    def get_OutputDimension(self,accountNR):
        return self.FLcontractDeployed.functions.getOutputDimension().call({"from":self.web3Connection.eth.accounts[accountNR]})

    def get_globalWeights(self,accountNR):

        we=self.FLcontractDeployed.functions.get_global_weights().call(
            {"from": self.web3Connection.eth.accounts[accountNR]})
        return we

    def get_globalBias(self,accountNR):
        bias=self.FLcontractDeployed.functions.get_global_bias().call(
            {"from": self.web3Connection.eth.accounts[accountNR]})
        return bias

    def get_account_balance(self,accountNR):
        return self.web3Connection.fromWei(self.web3Connection.eth.getBalance( self.web3Connection.eth.accounts[accountNR]), "ether")


    def roundUpdateOutstanding(self,accountNR):
        # self.lock_newRound.acquire()
        accountAddress = self.web3Connection.eth.accounts[accountNR]
        newround=self.FLcontractDeployed.functions.roundUpdateOutstanding(accountAddress).call({"from": self.web3Connection.eth.accounts[accountNR]})
        # if not newround:
        #     try:
        #         txhash=self.FLcontractDeployed.functions.end_update_round().transact(
        #             {"from": self.web3Connection.eth.accounts[accountNR]})
        #         self.__await_Trainsaction(txhash)
        #     except Exception as intx:
        #         print(f"AccountNr = {accountNR}: Update Ending Reverted")
        #         print(f"AccountNr = {accountNR}: Trying end Again")
        #         try:
        #             # , a, b, c, inputs
        #             txhash = self.FLcontractDeployed.functions.end_update_round().transact(
        #                 {"from": self.web3Connection.eth.accounts[accountNR]})
        #             self.__await_Trainsaction(txhash)
        #         except Exception as intx:
        #             print(f"AccountNr = {accountNR}: Update Ending Reverted")
        #             print(intx)
        # newround_refreshed=self.FLcontractDeployed.functions.roundUpdateOutstanding().call({"from": self.web3Connection.eth.accounts[accountNR]})
        # if newround_refreshed and (not newround):
        #     print(f"AccountNr = {accountNR}: Round is finished starting new round =>")
        #     self.lock_newRound.release()
        #     return newround_refreshed
        # else:
        #     self.lock_newRound.release()
        return newround

    def __update_with_proof(self,weights,bias,accountNR,Device_name, round,  fact):
        weights = [[int(x) for x in y] for y in weights]
        bias = [int(x) for x in bias]
        IPFSdata = self.config["DEFAULT"]["IPFSDataPath"] + Device_name + '.json'
        IPFSFileHash = "0x00000000000000000000000000000000"
        if self.config["DEFAULT"]["WriteOnIPFS"]:
            data_dictionary = {
                "weights": weights,
                "bias": bias,
                "round": round
            }
            json_object = json.dumps(data_dictionary, indent=4)
            with open(IPFSdata, "w") as outfile:
                outfile.write(json_object)
            IPFSFileHash = writeipfs(IPFSdata, self.config["DEFAULT"]["IPFSclientID"])

        #### in the following  part we check to see if the fact has been registered or not
        # this is just for simulation. this task should be done by the FL contract
        commands_2 = f'''
        python3 -m venv ~/cairo_venv
        source ~/cairo_venv/bin/activate
        cairo-sharp is_verified {fact}  --node_url=https://ethereum-goerli.publicnode.com
        '''

        check = False
        t1 = time.time()
        while check == False:
            # command = 'cairo-sharp is_verified' +  fact + ' --node_url=https://ethereum-goerli.publicnode.com'
            process_2 = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                         encoding="utf-8")
            out, err = process_2.communicate(commands_2)
            #print(out)
            if str(out[:-1]) == 'True':
                check = True

        print(f"Round: {round}, {Device_name} : fact is registered")
        ###################################################

        thxHash = self.FLcontractDeployed.functions.update_with_proof((IPFSFileHash[2:]), fact).transact({"from": self.web3Connection.eth.accounts[accountNR]})
        self.__await_Trainsaction(thxHash)
        print(f"Round: {round}, {Device_name}: UPDATE SUCCESSFUL")
        return IPFSFileHash


    def __update_without_proof(self,weights,bias,accountNR, Device_name, round):
        weights = [[int(x) for x in y] for y in weights]
        bias = [int(x) for x in bias]
        IPFSdata = self.config["DEFAULT"]["IPFSDataPath"] + Device_name + '.json'
        IPFSFileHash = "0x00000000000000000000000000000000"
        if self.config["DEFAULT"]["WriteOnIPFS"]:
            data_dictionary = {
                "weights": weights,
                "bias": bias,
                "round": round
            }
            json_object = json.dumps(data_dictionary, indent=4)
            with open(IPFSdata, "w") as outfile:
                outfile.write(json_object)

            IPFSFileHash = writeipfs(IPFSdata, self.config["DEFAULT"]["IPFSclientID"])


        thxHash = self.FLcontractDeployed.functions.update_without_proof(IPFSFileHash[2:]).transact(
            {"from": self.web3Connection.eth.accounts[accountNR]})
        self.__await_Trainsaction(thxHash)

        print(f"Round: {round}, {Device_name}: UPDATE SUCCESSFUL")
        return IPFSFileHash


    def update(self,weights,bias,accountNR,Device_name, round, fact=None):
        if self.config["DEFAULT"]["PerformProof"]:
            tries=5
            IPFSFileHash = ''
            while tries>0:
                try:
                    IPFSFileHash = self.__update_with_proof(weights,bias,accountNR,Device_name, round,fact)
                    tries=-1
                except:
                    time.sleep(self.config["DEFAULT"]["WaitingTime"])
                    if tries == 1:
                        print(f"Round: {round}, {Device_name}: Update Failed")
                    tries-=1
        else:
            tries = 5
            IPFSFileHash = ''
            while tries > 0:
                try:
                    IPFSFileHash = self.__update_without_proof(weights, bias, accountNR, Device_name, round)
                    tries = -1
                except:
                    time.sleep(self.config["DEFAULT"]["WaitingTime"])
                    if tries == 1:
                        print(f"Round: {round}, {Device_name}: Update Failed")
                    tries -= 1
        return IPFSFileHash

    def endUpdateSerial(self, accountNR):
        thxHash = self.FLcontractDeployed.functions.end_update_round().transact(
            {"from": self.web3Connection.eth.accounts[accountNR]})
        self.__await_Trainsaction(thxHash)
        iman_break_point = 18

    def get_BatchSize(self,accountNR):
        return  self.FLcontractDeployed.functions.getBatchSize().call({"from":self.web3Connection.eth.accounts[accountNR]})

    def get_RoundNumber(self, accountNR):
        return self.FLcontractDeployed.functions.getRoundNumber().call(
            {"from": self.web3Connection.eth.accounts[accountNR]})

    def get_Precision(self,accountNR):
        self.precision = self.__get_Precision(accountNR)
        return self.precision

    def getHashOfModels(self, accountNR):
        UploadedModelsHash= self.FLcontractDeployed.functions.getModelHAsh().call(
            {"from": self.web3Connection.eth.accounts[accountNR]})
        hashList = []
        for h in UploadedModelsHash:
            hashList.append('Qm'+h)
        return hashList



