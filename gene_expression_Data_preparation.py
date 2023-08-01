import pandas as pd
from Gene_test_nn.neuralnetwork import NeuralNetwork
from sklearn.model_selection import train_test_split
import numpy as np


path = "/home/iman/projects/kara/blockchain_based_Federated_learning/federatedlearning/codes/Devices/Gene_expression_data.txt"
columnNames = []
for i in range(60660):
    text = f'gene_ID_{i}'
    columnNames.append(text)

targets = []

for i in range(200):
    if i <= 99:
        targets.append(0)
    if i > 99:
        targets.append(1)

gene_ExpressionData = pd.read_csv(
            path, sep=',', names= columnNames)

#gene_ExpressionData["activity"] = targets

print(gene_ExpressionData.head())

var_val = gene_ExpressionData.var()
num_dim = 30
sorted_features = var_val.sort_values(ascending = False, axis = 'index')[0:num_dim].index

#normalized_data=(gene_ExpressionData-gene_ExpressionData.min())/(gene_ExpressionData.max()-gene_ExpressionData.min())

gene_ExpressionRedeucedData = gene_ExpressionData[sorted_features]
normalized_data=(gene_ExpressionRedeucedData-gene_ExpressionRedeucedData.min())/(gene_ExpressionRedeucedData.max()-gene_ExpressionRedeucedData.min())
X_train, X_test, y_train, y_test = train_test_split(normalized_data, targets, test_size=0.3, shuffle=True, random_state=1)
X_train = X_train.reset_index()
X_train = X_train.drop(columns="index")
X_train["Activity"] = y_train
X_test = X_test.reset_index()
X_test = X_test.drop(columns="index")
X_test["Activity"] = y_test

Train_destination_path = "/home/iman/projects/kara/blockchain_based_Federated_learning/federatedlearning/codes/Devices/Device_Data/Device_1/device_geneExpression_trainData.txt"
Test_destination_path = "/home/iman/projects/kara/blockchain_based_Federated_learning/federatedlearning/codes/Devices/Device_Data/Device_1/device_geneExpression_testData.txt"

np.savetxt(Train_destination_path, X_train.values, fmt='%f', delimiter=',')
np.savetxt(Test_destination_path, X_test.values, fmt='%f', delimiter=',')