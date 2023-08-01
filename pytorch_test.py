from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import numpy as np
import torch
from MiddleWare.pytorch_neural_net import NeuralNetwork, trainNeuralNetwork, Data
from torch.utils.data import Dataset, DataLoader

X, Y = make_classification(
    n_features=4, n_redundant=0, n_informative=3, n_clusters_per_class=2, n_classes=3
)

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33, random_state=42)

batch_size = 64

# Instantiate training and test data
train_data = Data(X_train, Y_train)
train_dataloader = DataLoader(dataset=train_data, batch_size=batch_size, shuffle=True)

test_data = Data(X_test, Y_test)
test_dataloader = DataLoader(dataset=test_data, batch_size=batch_size, shuffle=True)

for batch, (X, y) in enumerate(train_dataloader):
    print(f"Batch: {batch+1}")
    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")
    break

##########################
input_dim = 4
hidden_dim = 10
output_dim = 3

model = NeuralNetwork(input_dim, output_dim)
print(model)
learning_rate = 0.1

print("before training: ")
print(model.linear1.weight * 10000)

trainNeuralNetwork(model, train_dataloader, learning_rate, 2)

global_weights = torch.rand(output_dim, input_dim)

print("net weights after training: ")
print(model.linear1.weight * 10000)

print(" ")
print("global_weights: ")
print(global_weights)

model.set_weights(global_weights)

print("update global weights: ")
print(model.linear1.weight)
#print(list(model.parameters()))
