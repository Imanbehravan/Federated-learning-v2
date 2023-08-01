import io
import json
import subprocess
import sys
import threading
import time
import functools
import argparse
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import pandas as pd

from Analytics.Analytics import Analytics
from MessageBroker.Consumer import Consumer
from MiddleWare.BlockChainClientV2 import BlockChainConnection
from MiddleWare.NeuralNet import Network, FCLayer, mse_prime, mse
################################## adding neural network from pytorch
from MiddleWare.pytorch_neural_net import NeuralNetwork
from Data2IPFS import readFromIPFS
from heapq import nlargest

#################################################
from utils.utils import read_yaml
from test import proof_generation


def print_report(device,model, X_test, y_test):
    print(f"{device}",classification_report(y_test,model.predict(X_test),zero_division=0))

class FederatedLearningModel:

    def __init__(self, neural_method, config_file, deviceName):
        self.deviceName=deviceName
        self.config =config_file
        self.neural_method = neural_method
        self.consumer = Consumer()
        self.scaler = StandardScaler()
        if (neural_method == 1): # use base model
            self.net = Network(self.config["DEFAULT"]["OutputDimension"],self.config["DEFAULT"]["InputDimension"],self.config["DEFAULT"]["Precision"] )
            self.net.add(FCLayer(self.config["DEFAULT"]["InputDimension"], self.config["DEFAULT"]["OutputDimension"]))
            self.net.use(mse, mse_prime)
        ######################################## adding pytorch module of neural network
        if (neural_method == 2):
            self.net = NeuralNetwork(self.config["DEFAULT"]["InputDimension"], self.config["DEFAULT"]["OutputDimension"], self.config["DEFAULT"]["BatchSize"])

        ###########################################################################
        self.epochs=self.config["DEFAULT"]["Epochs"]

        self.learning_rate=None
        self.curr_batch=None
        self.batchSize=None
        self.x_train=None
        self.y_train=None
        self.IPFSHashList = []
        self.weightsHash = None
        self.biasHash = None
        datasource = self.config["DEFAULT"]["TestFilePath"] + self.deviceName +'/device_geneExpression_testData.txt'
        ## main code
        # testdata = pd.read_csv(
        #     datasource, sep=' ', names=
        #     ["T_xacc", "T_yacc", "T_zacc", "T_xgyro", "T_ygyro", "T_zgyro", "T_xmag", "T_ymag", "T_zmag",
        #      "RA_xacc", "RA_yacc", "RA_zacc", "RA_xgyro", "RA_ygyro", "RA_zgyro", "RA_xmag", "RA_ymag", "RA_zmag",
        #      "LA_xacc", "LA_yacc", "LA_zacc", "LA_xgyro", "LA_ygyro", "LA_zgyro", "LA_xmag", "LA_ymag", "LA_zmag",
        #      "RL_xacc", "RL_yacc", "RL_zacc", "RL_xgyro", "RL_ygyro", "RL_zgyro", "RL_xmag", "RL_ymag", "RL_zmag",
        #      "LL_xacc", "LL_yacc", "LL_zacc", "LL_xgyro", "LL_ygyro", "LL_zgyro", "LL_xmag", "LL_ymag", "LL_zmag",
        #      "Activity"]
        #
        # )

        columnNames = []
        numDim = self.config["DEFAULT"]["InputDimension"]


        for i in range(numDim):
            text = f'feature_{i}'
            columnNames.append(text)
        columnNames.append("Activity")
        testdata = pd.read_csv(
            datasource, sep=',', names=columnNames)




        # testdata.fillna(inplace=True, method='backfill')
        # testdata.dropna(inplace=True)
        #
        # ## main code
        # testdata.drop(columns= ["T_xacc", "T_yacc", "T_zacc", "T_xgyro","T_ygyro","T_zgyro","T_xmag", "T_ymag", "T_zmag","RA_xacc", "RA_yacc", "RA_zacc", "RA_xgyro","RA_ygyro","RA_zgyro","RA_xmag", "RA_ymag", "RA_zmag","RL_xacc", "RL_yacc", "RL_zacc", "RL_xgyro","RL_ygyro","RL_zgyro" ,"RL_xmag", "RL_ymag", "RL_zmag","LL_xacc", "LL_yacc", "LL_zacc", "LL_xgyro","LL_ygyro","LL_zgyro" ,"LL_xmag", "LL_ymag", "LL_zmag"],inplace=True)
        # activity_mapping = self.config["DEFAULT"]["ActivityMappings"]
        # filtered_activities = self.config["DEFAULT"]["Activities"]
        # activity_encoding = self.config["DEFAULT"]["ActivityEncoding"]
        # for key in activity_mapping.keys():
        #     testdata.loc[testdata['Activity'] == key,'Activity'] = activity_mapping[key]
        # testdata = testdata[testdata['Activity'].isin(filtered_activities)]
        # for key in activity_encoding.keys():
        #     testdata.loc[testdata['Activity'] == key, 'Activity'] = activity_encoding[key]

        # this part is added to reduce the number of test samples due to RAM issue
        ## main code
        self.y_test = testdata["Activity"]
        self.x_test = testdata.drop(columns="Activity")


        ## iman code

        # self.x_test = testdata.drop(columns="class")
        # self.y_test = testdata["class"]
        iman_breakpoint = 4

    def test_model(self):
        self.scaler.fit(self.x_test.values)
        x_test=self.scaler.transform(self.x_test.values)
        pred = self.net.predict(x_test)
        return accuracy_score((self.y_test).tolist(),pred)

    def get_classification_report(self):
        x_test=self.scaler.transform(self.x_test.to_numpy())
        return classification_report(self.y_test,self.net.predict(x_test),zero_division=0,output_dict=True)

    def process_Batch(self, globalRond):
        self.curr_batch.dropna(inplace=True)
        batch=self.curr_batch.sample(self.batchSize)
        self.x_train = batch.drop(columns=self.config["DEFAULT"]["ResponseVariable"])
        self.y_train = batch[self.config["DEFAULT"]["ResponseVariable"]]
        self.x_train = self.x_train.to_numpy()
        self.y_train = self.y_train.to_numpy()
        self.scaler.fit(self.x_test.to_numpy())
        self.x_train=self.scaler.transform(self.x_train)
        self.net.fit(self.x_train, self.y_train, epochs=self.epochs, learning_rate=self.learning_rate)
        score=self.test_model()
        print(f"round {globalRond}: {self.deviceName}:Score :",score)

    def reset_batch(self):
        self.curr_batch=None
        self.x_train=None
        self.y_train=None

    def get_weights(self):
        return self.net.get_weights()

    def get_bias(self):
        return self.net.get_bias()

    def set_learning_rate(self,rate):
        self.learning_rate=rate

    def set_weights(self,weights):
        self.net.set_weights(weights)

    def set_bias(self,bias):
        self.net.set_bias(bias)

    def set_batchSize(self,batchSize):
        self.batchSize=batchSize

    def set_precision(self,precision):
        self.net.set_precision(precision)

    def add_data_to_current_batch(self,data):
        if self.curr_batch is None:
            self.curr_batch = data
        else:
            self.curr_batch=pd.concat([self.curr_batch,data])



class MiddleWareV2:

    def __init__(self,neural_method, connection, deviceName, accountNR, configFile):
        self.accountNR=accountNR
        self.consumer_thread=None
        self.analytics=Analytics(deviceName=deviceName,config_file=configFile)
        self.blockChainConnection=connection
        self.deviceName=deviceName
        self.model=FederatedLearningModel(neural_method, config_file=configFile,deviceName=self.deviceName)
        self.config = configFile
        self.consumer = Consumer()
        self.__init_Consumer(deviceName,callback)
        self.proof=None
        self.fact=None
        self.precision=None
        self.batchSize=None
        self.round=0
        self.registered = False

    def __generate_Proof(self,w,b,w_new,b_new,x_train,y_train,learning_rate):

        x_train=x_train*self.precision
        b_new=b_new.reshape(self.config["DEFAULT"]["OutputDimension"],)
        x_train = x_train.astype(int)
        y_train = y_train.astype(int)
        def args_parser(args):
            res = ""
            for arg in range(len(args)):
                entry = args[arg]
                if isinstance(entry, (list, np.ndarray)):
                    for i in range(len(entry)):
                        row_i = entry[i]
                        if isinstance(row_i, (list, np.ndarray)):
                            for j in range(len(row_i)):
                                val = row_i[j]
                                res += str(val) + " "
                        else:
                            res += str(row_i) + " "
                else:
                    res += str(args[arg]) + " "
            res = res[:-1]
            return res


        def convert_matrix(m):
            max_field = 21888242871839275222246405745257275088548364400416034343698204186575808495617
            m=np.array(m)
            return np.where(m < 0, max_field + m, m), np.where(m > 0, 0, 1)

        zokrates = "zokrates"
        verification_base=self.config["DEFAULT"]["VerificationBase"]
        weights, weights_sign = convert_matrix(w)
        bias, bias_sign = convert_matrix(b)
        weights_new, _ = convert_matrix(w_new)
        bias_new, _ = convert_matrix(b_new)
        x, x_sign = convert_matrix(x_train)
        args = [weights, weights_sign, bias, bias_sign, x, x_sign, y_train, learning_rate, self.precision,
                weights_new, bias_new]
        out_path=verification_base+"out"
        abi_path=verification_base+"abi.json"
        witness_path=verification_base+"witness_"+self.deviceName

        zokrates_compute_witness = [zokrates, "compute-witness", "-o",witness_path,'-i',out_path,'-s',abi_path,"-a"]
        zokrates_compute_witness.extend(args_parser(args).split(" "))
        g = subprocess.run(zokrates_compute_witness, capture_output=True)
        self.__sleep_call(10)
        proof_path=verification_base+"proof_"+self.deviceName
        proving_key_path=verification_base+"proving.key"
        zokrates_generate_proof = [zokrates, "generate-proof",'-w',witness_path,'-p',proving_key_path,'-i',out_path,'-j',proof_path]
        g = subprocess.run(zokrates_generate_proof, capture_output=True)
        self.__sleep_call(10)
        ##g = subprocess.call(zokrates_generate_proof, shell=True)
        with open(proof_path,'r+') as f:
            self.proof=json.load(f)
        iman_break_point = 17

    def __generate_fact(self, globalRound):
        self.blockChainConnection.lock_newRound.acquire()
        print(f"Round: {globalRound}, {self.deviceName} fact generation process ... ")
        commands = f'''
        python3 -m venv ~/cairo_venv
        source ~/cairo_venv/bin/activate
        cairo-sharp submit --source /home/iman/projects/kara/blockchain_based_Federated_learning/federatedlearning/codes/Devices/Verification/Cairo/{self.deviceName}/MKT_check.cairo \
        --program_input /home/iman/projects/kara/blockchain_based_Federated_learning/federatedlearning/codes/Devices/Verification/Cairo/{self.deviceName}/cairoInputTrainData.json
        '''
        process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf-8")
        out, err = process.communicate(commands)
        fact = out[out.find("Fact") + 6:-1]
        print(f"Round: {globalRound}, {self.deviceName} fact generated: ", fact)
        process.stdin.close()
        process.stdout.close()
        process.wait()
        self.blockChainConnection.lock_newRound.release()
        return fact


    def __init_Consumer(self,DeviceName,callBackFunction):
        queueName = self.config["DEFAULT"]["QueueBase"] + DeviceName
        on_message_callback = functools.partial(callBackFunction, args=(self.model))
        self.consumer.declare_queue(queueName)
        self.consumer.consume_data(queueName,on_message_callback)

    def __start_Consuming(self):
        self.consumer_thread=threading.Thread(target=self.consumer.start_consuming)
        self.consumer_thread.start()

    def update(self,w,b,fact,r,balance):
        tu = time.time()
        if (self.config["DEFAULT"]["Aggregation"] == "on-chain"):
            IPFSfileHash = self.blockChainConnection.update(w, b, self.accountNR,self.deviceName,r, fact)
            self.analytics.add_round_update_blockchain_time(r, time.time() - tu)
            self.analytics.add_round_gas(r, balance - self.blockChainConnection.get_account_balance(self.accountNR))

        if (self.config["DEFAULT"]["Aggregation"] == "off-chain"):
            IPFSfileHash = self.serverConnection.update(w, b, self.accountNR, self.deviceName, self.round, p)
        self.model.IPFSHashList.append(IPFSfileHash)

    def KfedAverage(self, HashList):
        AccuracyList = []
        IPFSClientID = self.config["DEFAULT"]["IPFSclientID"]
        allWights = []
        allBias = []
        for h in HashList:
            path = self.config["DEFAULT"]["IPFSDataPath"] + self.deviceName + '/'
            modelData = readFromIPFS(h, IPFSClientID, path)
            outputPath = path + '/' + h
            f = open(outputPath)
            data = json.load(f)
            weights = data["weights"]
            allWights.append(weights)
            bias = data["bias"]
            allBias.append(bias)
            lr = self.blockChainConnection.get_LearningRate(self.accountNR)
            self.precision = self.blockChainConnection.get_Precision(self.accountNR)
            self.batchSize = self.blockChainConnection.get_BatchSize(self.accountNR)
            self.model.set_precision(precision=self.precision)
            self.model.set_learning_rate(lr)
            self.model.set_weights(weights)
            self.model.set_bias(bias)
            acc = self.model.test_model()
            AccuracyList.append(acc)
        numBestModels = self.config["DEFAULT"]["KtopModels"]
        if numBestModels > self.config["DEFAULT"]["NumberOfParticipants"]:
            numBestModels = self.config["DEFAULT"]["NumberOfParticipants"]
        topModelsIndex = nlargest(numBestModels, range(len(AccuracyList)), key=lambda idx: AccuracyList[idx])
        for j in range(numBestModels):
            if j == 0:
                sumWeights = np.array(allWights[topModelsIndex[j]])
                sumBias = np.array(allBias[topModelsIndex[j]])
            if j > 0:
                sumWeights = sumWeights + np.array(allWights[topModelsIndex[j]])
                sumBias = sumBias + np.array(allBias[topModelsIndex[j]])

        averageWeights = sumWeights/numBestModels
        averageBias = sumBias / numBestModels
        return averageWeights.tolist(), averageBias.tolist()




    def start_MiddlewareV2(self):
        self.__start_Consuming()
        #if (self.config["DEFAULT"]["Aggregation"] == "on-chain"):
        self.blockChainConnection.register(self.accountNR, self.deviceName)
        # self.round = self.blockChainConnection.get_RoundNumber(self.accountNR)
        globalRound = self.blockChainConnection.get_RoundNumber(self.accountNR)



        while self.config["DEFAULT"]["Rounds"] > globalRound:
        # while self.config["DEFAULT"]["Rounds"]>self.round:
            globalRound = self.blockChainConnection.get_RoundNumber(self.accountNR)
            #self.round = globalRound
            # if (self.round == 0):
            if (globalRound == 1):
                outstanding_update = self.blockChainConnection.roundUpdateOutstanding(self.accountNR)
                print(f" Round {globalRound} {self.deviceName}: Has update outstanding: ", outstanding_update)
                if (outstanding_update == False):
                    lr = self.blockChainConnection.get_LearningRate(self.accountNR)
                    self.model.set_learning_rate(lr)
                    self.precision = self.blockChainConnection.get_Precision(self.accountNR)
                    self.model.set_precision(precision=self.precision)
                    w = self.model.get_weights()
                    b = self.model.get_bias()
                    self.fact = []
                    balance = self.blockChainConnection.get_account_balance(self.accountNR)
                    if self.config["DEFAULT"]["PerformProof"]:
                        self.fact = self.__generate_fact(globalRound)
                        ### just for simulation. in the real tests it should be removed
                        self.fact = '0x663cb3658d0f920c97a6006950551d2b427b8468a7f003272df1c4a853b0b939'
                    self.update(w, b, self.fact, globalRound, balance)
                    #thread = threading.Thread(target=self.update, args=[w, b, self.fact, globalRound, balance])
                    #thread.start()
                    #self.round += 1
                    self.registered = True
                    iman_break_point = 15

            # if (self.round > 1):
            if (globalRound > 1):
                #if (self.config["DEFAULT"]["Aggregation"] == "on-chain"):
                if (self.accountNR == 0):
                    iman_breakpoint = 100
                if (self.accountNR == 1):
                    iman_breakpoint = 101
                if (self.accountNR == 2):
                    iman_breakpoint = 102
                outstanding_update=self.blockChainConnection.roundUpdateOutstanding(self.accountNR)
                # self.round = self.blockChainConnection.get_RoundNumber(self.accountNR)

                # if (self.config["DEFAULT"]["Aggregation"] == "off-chain"):
                #     outstanding_update = self.serverConnection.round_UpdateOutstanding(self.deviceName)
                #     self.round = self.serverConnection.get_RoundNumber(self.accountNR)

                print(f"Round {globalRound} {self.deviceName}: Has update outstanding: ",outstanding_update)
                if(outstanding_update == False):
                    round = self.blockChainConnection.get_RoundNumber(self.accountNR)
                    # if round > self.round:

                    t=time.time()
                    balance = 0
                    #if (self.config["DEFAULT"]["Aggregation"] == "on-chain"):
                    balance=self.blockChainConnection.get_account_balance(self.accountNR)
                    UploadedModelsHash = self.blockChainConnection.getHashOfModels(self.accountNR)
                    averageWeights, averageBias = self.KfedAverage(UploadedModelsHash)
                    # global_weights=self.blockChainConnection.get_globalWeights(self.accountNR)
                    # global_bias=self.blockChainConnection.get_globalBias(self.accountNR)
                    lr=self.blockChainConnection.get_LearningRate(self.accountNR)
                    self.precision=self.blockChainConnection.get_Precision(self.accountNR)
                    self.batchSize = self.blockChainConnection.get_BatchSize(self.accountNR)

                    # if (self.config["DEFAULT"]["Aggregation"] == "off-chain"):
                    #     global_weights = self.serverConnection.get_globalWeights()
                    #     global_bias = self.serverConnection.get_globalBias()
                    #     lr = self.serverConnection.get_LearningRate()
                    #     self.precision = self.serverConnection.get_Precision()
                    #     self.batchSize = self.serverConnection.get_BatchSize()

                    self.model.set_precision(precision=self.precision)
                    self.model.set_learning_rate(lr)
                    self.model.set_weights(averageWeights)
                    self.model.set_bias(averageBias)
                    self.batchSize=self.blockChainConnection.get_BatchSize(self.accountNR)
                    while(self.model.curr_batch is None):
                        pass
                    while(self.model.curr_batch.size < self.batchSize):
                        pass
                    self.model.set_batchSize(self.batchSize)
                    tt=time.time()
                    self.model.process_Batch(globalRound)
                    self.analytics.add_round_training_local_time(globalRound,time.time()-tt)
                    self.analytics.add_round_score(globalRound,self.model.test_model())
                    ## for main code it should be uncommented
                    self.analytics.add_round_classification_report(globalRound, self.model.get_classification_report())
                    w=self.model.get_weights()
                    b=self.model.get_bias()


                    self.model.reset_batch()
                    self.fact = []
                    if self.config["DEFAULT"]["PerformProof"]:
                        self.fact = self.__generate_fact(globalRound)
                        ### just for simulation. in the real tests it should be removed
                        self.fact = '0x663cb3658d0f920c97a6006950551d2b427b8468a7f003272df1c4a853b0b939'
                    self.update(w,b,self.fact,globalRound,balance)
                    #thread=threading.Thread(target=self.update,args=[w,b,self.fact,globalRound,balance])
                    #thread.start()
                    print(f"Round {globalRound} {self.deviceName}: update took {time.time()-t} seconds")
                    #self.round+=1
                    self.analytics.add_round_time(globalRound,time.time()-t)
                    iman_breakpoint = 6
            time.sleep(self.config["DEFAULT"]["WaitingTime"])

            #self.__sleep_call(10)
        self.analytics.write_data()
        iman_breakpoint = 15

    def __sleep_call(self, t):
        #print(f"{self.deviceName}:Checking for new update round in:")
        for i in range(0,t):
            #print(i+1,end=" ")
            #print("... ",end=" ")
            time.sleep(1)
        #print()
        #print(f"{self.deviceName}:Checking for new update =>")

def callback(ch, method, properties, body,args):
    model=args
    if isinstance(model,FederatedLearningModel):
        batch=pd.read_csv(io.BytesIO(body),header=0,index_col=0)
        model.add_data_to_current_batch(batch)


