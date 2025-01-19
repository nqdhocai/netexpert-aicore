import pandas as pd

from aicore.components.database.database import *
from aicore.components.database.utils.norm_data import norm_data

dt = pd.read_csv("../../data.csv")
dt = dt.astype('str')
dt.fillna("NULL")
columns = dt.columns

for i in range(0, len(dt)):
    sample = ""
    for key, val in zip(columns, dt.iloc[i].to_list()):
        sample += key + ": " + val + "; "
    data = norm_data(sample)
    print(data)
    insert_device(Device(**data))
