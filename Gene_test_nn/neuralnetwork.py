import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np


class NeuralNetwork(torch.nn.Module):
    def __init__(self, input_dim, output_dim, hiddenLayerNeuron_1, hiddenLayerNeuron_2, batchsize):
        super(NeuralNetwork, self).__init__()
        self.linear1 = torch.nn.Linear(input_dim, output_dim)
        #self.linear1 = torch.nn.Linear(input_dim, output_dim)
        #self.linear2 = torch.nn.Linear(hiddenLayerNeuron_1, hiddenLayerNeuron_2)
        #self.linear3 = torch.nn.Linear(hiddenLayerNeuron_2, output_dim)
        self.batchsize = batchsize

    def forward(self, x):
        x_1 = torch.sigmoid(self.linear1(x))
        #x_2 = self.linear2(x_1)
        #x_3 = torch.sigmoid(self.linear3(x_2))
        # x = self.linear2(x)
        return x_1


    def set_precision(self,precision):
        self.precision=precision

    def set_weights(self, global_weights):
        tensored_weights = torch.Tensor(global_weights)
        self.linear1.weight = torch.nn.Parameter(tensored_weights/self.precision)
        iman_break_point = 4

    def set_bias(self, global_bias):
        tensored_bias = torch.Tensor(global_bias)
        self.linear1.bias = torch.nn.Parameter(tensored_bias/self.precision)
        iman_break_point = 5

    def get_weights(self):
        weights = self.linear1.weight * self.precision
        weights = weights.detach().numpy()
        weights = weights.astype(int)
        return (weights)

    def get_bias(self):
        biases = self.linear1.bias * self.precision
        biases = biases.detach().numpy()
        biases = biases.astype(int)
        biases = biases.reshape(-1,1)
        return (biases)

    def predict(self, x_test):
        x_test = torch.Tensor(x_test.values)
        outputs = self(x_test)
        __, predicted = torch.max(outputs, 1)
        predicted = predicted.tolist()
        return predicted

    def fit(self,  x_train, y_train, epochs, learning_rate):
        #y_train = y_train.astype(int)
        train_data = Data(x_train, y_train)
        train_dataloader = DataLoader(dataset=train_data, batch_size=self.batchsize, shuffle=True)
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(self.parameters(), lr=learning_rate)
        for epoch in range(epochs):
            running_loss = 0.0
            for i, data in enumerate(train_dataloader, 0):
                inputs, labels = data
                # set optimizer to zero grad to remove previous epoch gradients
                optimizer.zero_grad()
                # forward propagation
                outputs = self(inputs)
                loss = criterion(outputs, labels)
                # backward propagation
                loss.backward()
                # optimize
                optimizer.step()
                running_loss += loss.item()
            # display statistics
            print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 2000:.5f}')





class Data(Dataset):
    def __init__(self, X_train, y_train):
        # need to convert float64 to float32 else
        # will get the following error
        # RuntimeError: expected scalar type Double but found Float
        X_train = X_train.to_numpy()
        #y_train = y_train.to_numpy()
        y_train = np.array(y_train)
        self.X = torch.from_numpy(X_train.astype(np.float32))
        # need to convert float64 to Long else
        # will get the following error
        # RuntimeError: expected scalar type Long but found Float
        self.y = torch.from_numpy(y_train).type(torch.LongTensor)
        self.len = self.X.shape[0]

    def __getitem__(self, index):
        return self.X[index], self.y[index]

    def __len__(self):
        return self.len