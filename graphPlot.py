import numpy as np
import matplotlib.pyplot as plt

Device_1 = [95, 97, 97, 97]
Device_2 = [100, 100, 100, 100]
Device_3 =[77, 100, 100, 100]

round = [2, 3, 4, 5]

plt.plot(round, Device_1, color="r", label = "Client 1")
plt.plot(round, Device_2, color="g", label = "Client 2")
plt.plot(round, Device_3, color="b", label = "Client 3")
plt.xlabel("Round")
plt.ylabel("Accuracy")
plt.legend()
plt.show()

Device_1 = [93, 97, 1, 97, 97, 97, 97]
Device_2 = [100, 100, 100, 100, 100, 100, 100]
Device_3 =[80, 100, 100, 100, 100, 100, 100]

round = [2, 3, 4, 5, 6, 7, 8]

plt.plot(round, Device_1, color="r", label = "Client 1")
plt.plot(round, Device_2, color="g", label = "Client 2")
plt.plot(round, Device_3, color="b", label = "Client 3")
plt.xlabel("Round")
plt.ylabel("Accuracy")
plt.legend()
plt.show()


Device_1 = [89, 95, 95, 95]
Device_2 = [94, 100, 100, 97]
Device_3 = [86, 100, 100, 100]
Device_4 = [72, 97, 97, 97]
Device_5 = [77, 83, 96, 96]



round = [2, 3, 4, 5]

plt.plot(round, Device_1, color="r", label = "Client 1")
plt.plot(round, Device_2, color="g", label = "Client 2")
plt.plot(round, Device_3, color="b", label = "Client 3")
plt.plot(round, Device_4, color="c", label = "Client 4")
plt.plot(round, Device_5, color="m", label = "Client 5")
plt.xlabel("Round")
plt.ylabel("Accuracy")
plt.legend()
plt.show()

Experiment_1 = [90, 99, 99, 99]
Experiment_2 = [91, 99, 100, 99, 99, 99 ,99]
Experiment_3 = [83, 95, 97, 97]
round_1 = [2, 3, 4, 5]
round_2 = [2, 3, 4, 5, 6, 7, 8]

plt.plot(round_1, Experiment_1, color="r", label = "Experiment 1")
plt.plot(round_2, Experiment_2, color="g", label = "Experiment 2")
plt.plot(round_1, Experiment_3, color="b", label = "Experiment 3")
plt.xlabel("Round")
plt.ylabel("Average accuracy")
plt.legend()
plt.show()


