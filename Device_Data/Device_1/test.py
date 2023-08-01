import os
import pandas as pd

path_0 = os.getcwd()

print((str(path_0)))

path = os.path.join(os.path.join(str(os.getcwd()),'Iman_Data'))

print("path: ", path)

data = pd.read_csv(path, names=["f1", "f2", "f3", "Activity"])

print(data.head())