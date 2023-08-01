import numpy as np

data = np.random.randint(10, size=(100, 5))


Fake_Train_destination_path = "/home/iman/projects/kara/blockchain_based_Federated_learning/federatedlearning/codes/Devices/Device_Data/Device_1/device_geneExpression_Fake_trainData.txt"
Test_destination_path = "/home/iman/projects/kara/blockchain_based_Federated_learning/federatedlearning/codes/Devices/Device_Data/Device_1/device_geneExpression_Fake_testData.txt"

np.savetxt(Fake_Train_destination_path, data, fmt='%f', delimiter=',')
np.savetxt(Test_destination_path, data, fmt='%f', delimiter=',')

print("f")