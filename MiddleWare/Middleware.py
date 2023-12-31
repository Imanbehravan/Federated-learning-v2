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
from MiddleWare.BlockChainClient import BlockChainConnection
from MiddleWare.NeuralNet import Network, FCLayer, mse_prime, mse
################################## adding neural network from pytorch
from MiddleWare.pytorch_neural_net import NeuralNetwork



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
        datasource = self.config["DEFAULT"]["TestFilePath"]
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
        x_test=self.scaler.transform(self.x_test.to_numpy())
        pred = self.net.predict(x_test)
        return accuracy_score(self.y_test,pred)

    def get_classification_report(self):
        x_test=self.scaler.transform(self.x_test.to_numpy())
        return classification_report(self.y_test,self.net.predict(x_test),zero_division=0,output_dict=True)

    def process_Batch(self):
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
        print(f"{self.deviceName}:Score :",score)

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



class MiddleWare:

    def __init__(self,neural_method, aggregation_method, connection, deviceName, accountNR, configFile):
        self.accountNR=accountNR
        self.consumer_thread=None
        self.analytics=Analytics(deviceName=deviceName,config_file=configFile)
        if (aggregation_method == "on-chain"):
            self.blockChainConnection=connection
        if (aggregation_method == "off-chain"):
            self.serverConnection = connection
        self.deviceName=deviceName
        self.model=FederatedLearningModel(neural_method, config_file=configFile,deviceName=self.deviceName)
        self.config = configFile
        self.consumer = Consumer()
        self.__init_Consumer(deviceName,callback)
        self.proof=None
        self.precision=None
        self.batchSize=None
        self.round=0

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


    def __init_Consumer(self,DeviceName,callBackFunction):
        queueName = self.config["DEFAULT"]["QueueBase"] + DeviceName
        on_message_callback = functools.partial(callBackFunction, args=(self.model))
        self.consumer.declare_queue(queueName)
        self.consumer.consume_data(queueName,on_message_callback)

    def __start_Consuming(self):
        self.consumer_thread=threading.Thread(target=self.consumer.start_consuming)
        self.consumer_thread.start()

    def update(self,w,b,p,r,balance):
        tu = time.time()
        if (self.config["DEFAULT"]["Aggregation"] == "on-chain"):
            IPFSfileHash = self.blockChainConnection.update(w, b, self.accountNR,self.deviceName,self.round, self.accountNR, p)
            self.analytics.add_round_update_blockchain_time(r, time.time() - tu)
            self.analytics.add_round_gas(self.round, balance - self.blockChainConnection.get_account_balance(self.accountNR))

        if (self.config["DEFAULT"]["Aggregation"] == "off-chain"):
            IPFSfileHash = self.serverConnection.update(w, b, self.accountNR, self.deviceName, self.round, p)
        self.model.IPFSHashList.append(IPFSfileHash)


    # funtion start_Middleware_serial us written by Iman to add serial mode.
    # due to RAM problem we cannot run the code with proof in parallel form (using thread library)
    # so we added the following function to do it in serial form.
    # nodes perform their task one by one
    def start_Middleware_serial(self, round, Device, deviceNumber):
        self.__start_Consuming()
        self.round = round
        self.__sleep_call(10)
        if ((self.config["DEFAULT"]["Aggregation"] == "on-chain") & (deviceNumber == 1) & (round == 1)):
            self.blockChainConnection.init_contract(self.accountNR)
            #self.round = self.blockChainConnection.get_RoundNumber(self.accountNR)

        if (self.config["DEFAULT"]["Aggregation"] == "off-chain"):
            self.serverConnection.init_aggregator(self.accountNR)
            #self.round = self.serverConnection.get_RoundNumber(self.accountNR)

        # if (self.config["DEFAULT"]["Aggregation"] == "on-chain"):
        #     outstanding_update=self.blockChainConnection.roundUpdateOutstanding(self.accountNR)
        #     #self.round = self.blockChainConnection.get_RoundNumber(self.accountNR)

        # if (self.config["DEFAULT"]["Aggregation"] == "off-chain"):
        #     outstanding_update = self.serverConnection.round_UpdateOutstanding(self.deviceName)
        #     #self.round = self.serverConnection.get_RoundNumber(self.accountNR)

        print(f"{self.deviceName}: Round {round} Has update outstanding")
        #if(outstanding_update):
        t=time.time()
        balance = 0
        if (self.config["DEFAULT"]["Aggregation"] == "on-chain"):
            balance=self.blockChainConnection.get_account_balance(self.accountNR)
            global_weights=self.blockChainConnection.get_globalWeights(self.accountNR)
            global_bias=self.blockChainConnection.get_globalBias(self.accountNR)
            lr=self.blockChainConnection.get_LearningRate(self.accountNR)
            self.precision=self.blockChainConnection.get_Precision(self.accountNR)
            self.batchSize = self.blockChainConnection.get_BatchSize(self.accountNR)

        if (self.config["DEFAULT"]["Aggregation"] == "off-chain"):
            global_weights = self.serverConnection.get_globalWeights()
            global_bias = self.serverConnection.get_globalBias()
            lr = self.serverConnection.get_LearningRate()
            self.precision = self.serverConnection.get_Precision()
            self.batchSize = self.serverConnection.get_BatchSize()

        self.model.set_precision(precision=self.precision)
        self.model.set_learning_rate(lr)
        self.model.set_weights(global_weights)
        self.model.set_bias(global_bias)
        self.model.curr_batch = Device.data
        #self.batchSize=self.blockChainConnection.get_BatchSize(self.accountNR)
        # while(self.model.curr_batch is None):
        #     pass
        # while(self.model.curr_batch.size < self.batchSize):
        #     pass
        self.model.set_batchSize(self.batchSize)
        tt=time.time()
        self.model.process_Batch()
        self.analytics.add_round_training_local_time(self.round,time.time()-tt)
        self.analytics.add_round_score(self.round,self.model.test_model())
        ## for main code it should be uncommented
        self.analytics.add_round_classification_report(self.round, self.model.get_classification_report())
        w=self.model.get_weights()
        b=self.model.get_bias()
        if self.config["DEFAULT"]["PerformProof"]:
            tp=time.time()
            self.__generate_Proof(global_weights,global_bias,w,b,self.model.x_train,self.model.y_train,lr)
            self.analytics.add_round_proof_times(self.round, time.time() - tp)
        self.model.reset_batch()
        #thread=threading.Thread(target=self.update,args=[w,b,self.proof,self.round,balance])
        #thread.start()
        self.update(w,b,self.proof,self.round,balance)
        print(f"{self.deviceName}:Round {round} update took {time.time()-t} seconds")
        #self.round+=1
        self.analytics.add_round_time(round,time.time()-t)
        iman_breakpoint = 6
        self.analytics.write_data()
        if deviceNumber == self.config["DEFAULT"]["NumberOfParticipants"]:
            time.sleep(self.config["DEFAULT"]["IntervalTime"])
            self.blockChainConnection.endUpdateSerial(self.accountNR)
            print("round finished")
        iman_break_point = 13

    def start_Middleware(self):
        self.__start_Consuming()
        if (self.config["DEFAULT"]["Aggregation"] == "on-chain"):
            self.blockChainConnection.init_contract(self.accountNR)
            self.round = self.blockChainConnection.get_RoundNumber(self.accountNR)

        if (self.config["DEFAULT"]["Aggregation"] == "off-chain"):
            self.serverConnection.init_aggregator(self.accountNR)
            self.round = self.serverConnection.get_RoundNumber(self.accountNR)

        # self.round=self.blockChainConnection.get_RoundNumber(self.accountNR)
        while self.config["DEFAULT"]["Rounds"]>self.round:
            if (self.config["DEFAULT"]["Aggregation"] == "on-chain"):
                outstanding_update=self.blockChainConnection.roundUpdateOutstanding(self.accountNR)
                self.round = self.blockChainConnection.get_RoundNumber(self.accountNR)

            if (self.config["DEFAULT"]["Aggregation"] == "off-chain"):
                outstanding_update = self.serverConnection.round_UpdateOutstanding(self.deviceName)
                self.round = self.serverConnection.get_RoundNumber(self.accountNR)

            print(f"{self.deviceName}: Round {self.round} Has update outstanding: ",outstanding_update)
            if(outstanding_update):
                t=time.time()
                balance = 0
                if (self.config["DEFAULT"]["Aggregation"] == "on-chain"):
                    balance=self.blockChainConnection.get_account_balance(self.accountNR)
                    global_weights=self.blockChainConnection.get_globalWeights(self.accountNR)
                    global_bias=self.blockChainConnection.get_globalBias(self.accountNR)
                    lr=self.blockChainConnection.get_LearningRate(self.accountNR)
                    self.precision=self.blockChainConnection.get_Precision(self.accountNR)
                    self.batchSize = self.blockChainConnection.get_BatchSize(self.accountNR)

                if (self.config["DEFAULT"]["Aggregation"] == "off-chain"):
                    global_weights = self.serverConnection.get_globalWeights()
                    global_bias = self.serverConnection.get_globalBias()
                    lr = self.serverConnection.get_LearningRate()
                    self.precision = self.serverConnection.get_Precision()
                    self.batchSize = self.serverConnection.get_BatchSize()

                self.model.set_precision(precision=self.precision)
                self.model.set_learning_rate(lr)
                self.model.set_weights(global_weights)
                self.model.set_bias(global_bias)
                #self.batchSize=self.blockChainConnection.get_BatchSize(self.accountNR)
                while(self.model.curr_batch is None):
                    pass
                while(self.model.curr_batch.size < self.batchSize):
                    pass
                self.model.set_batchSize(self.batchSize)
                tt=time.time()
                self.model.process_Batch()
                self.analytics.add_round_training_local_time(self.round,time.time()-tt)
                self.analytics.add_round_score(self.round,self.model.test_model())
                ## for main code it should be uncommented
                self.analytics.add_round_classification_report(self.round, self.model.get_classification_report())
                w=self.model.get_weights()
                b=self.model.get_bias()
                if self.config["DEFAULT"]["PerformProof"]:
                    tp=time.time()
                    self.__generate_Proof(global_weights,global_bias,w,b,self.model.x_train,self.model.y_train,lr)
                    self.analytics.add_round_proof_times(self.round, time.time() - tp)
                self.model.reset_batch()
                #thread=threading.Thread(target=self.update,args=[w,b,self.proof,self.round,balance])
                #thread.start()
                self.update(w,b,self.proof,self.round,balance)
                print(f"{self.deviceName}:Round {self.round} update took {time.time()-t} seconds")
                self.round+=1
                self.analytics.add_round_time(self.round,time.time()-t)
                iman_breakpoint = 6
            time.sleep(self.config["DEFAULT"]["WaitingTime"])
            #self.__sleep_call(10)
        self.analytics.write_data()

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


