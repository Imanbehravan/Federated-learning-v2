import matplotlib.pyplot as plt

Device_1_Score = [0.26, 0.4, 0.38, 0.31]
Device_2_Score = [0.21, 0.31, 0.25, 0.26]
Device_3_Score = [0.31, 0.36, 0.25, 0.28]


plt.plot(Device_1_Score, label="Device 1 accuracy")
plt.plot(Device_2_Score, label="Device 2 accuracy")
plt.plot(Device_3_Score, label="Device 3 accuracy")

plt.xlabel('round number')
plt.ylabel('accuracy')
plt.title("accuracy of off-chain learners in each round")
plt.legend()
plt.show()