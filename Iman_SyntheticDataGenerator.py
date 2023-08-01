import numpy as np
from numpy.random import rand
import pandas as pd

numRows = 150
numFeatures = 9
numClass = 3
class_labels = [1, 2, 3]

centers = []
class_1_center = np.array([1, 1, 1])
centers.append(class_1_center)
class_2_center = np.array([10, 10, 10])
centers.append(class_2_center)
class_3_center = np.array([100, 100, 100])
centers.append(class_3_center)
print(centers)
print(centers[1])

data = []

for i in range(int(numRows/3)):
    for j in range(3):
        test = []
        test = rand(3) + centers[j]
        test = test.tolist()
        test.append(class_labels[j])
        data.append(test)


#########################################################

matData = np.mat(data)
trainDataset = pd.DataFrame(data=matData.astype(float))

trainDataset.to_csv('Iman_testData.csv', sep=',', header=False, float_format='%.2f', index=False)


mydata = pd.read_csv("Iman_testData.csv", names=["f1", "f2", "f3", "class"])
print(mydata.head())

