import numpy as np
import pandas as pd
from pymongo import MongoClient


mongoUrl = "mongodb://localhost:27017/"
dbName  = "metrics"

def getDatabase(database):    
    global mongoUrl    
    conn = MongoClient(mongoUrl)        
    return conn[database]


def plotReceiveBoxPlot(collection, workloads=["open5gs-upf-1", "open5gs-upf-2", "open5gs-upf-3","open5gs-upf-4", "open5gs-upf-5"], Experinces=None):
    global mongoUrl
    global dbName
    conn = MongoClient(mongoUrl) 
    db = conn[dbName]
    if Experinces is not None:
        df = pd.DataFrame(list(db[collection].find(filter={"workload": {"$in": workloads}, "ts": {"$gte": 900}, "exp": {"$in": Experinces}}, projection={"_id": 0})))
    else:
        df = pd.DataFrame(list(db[collection].find(filter={"workload": {"$in": workloads}, "ts": {"$gte": 900}}, projection={"_id": 0})))
    
    df["value"] = round(df["value"] / 1024 / 1024, 3)
    df = df.drop(df[df['value'] == 0.0].index)
    return df
 
def plotLatencyBoxPlotPrep(collection, workloads, last5m=False, Filter="workload", Experiences=None):
    global mongoUrl
    global dbName
    conn = MongoClient(mongoUrl) 
    db = conn[dbName]
    
    strLast5m = {"ts": {"$gte": 900}} if last5m else None

    if Experiences is not None:
        if last5m:
            df = pd.DataFrame(list(db[collection].find(filter={"workload": {"$in": workloads}, "ts": {"$gte": 900}, "exp": {"$in": Experiences}}, projection={"_id": 0})))
        else:
            df = pd.DataFrame(list(db[collection].find(filter={"workload": {"$in": workloads}, "exp": {"$in": Experiences}}, projection={"_id": 0})))
    else:
        if last5m:
            df = pd.DataFrame(list(db[collection].find(filter={"workload": {"$in": workloads}, "ts": {"$gte": 900}}, projection={"_id": 0})))
        else:
            df = pd.DataFrame(list(db[collection].find(filter={"workload": {"$in": workloads}}, projection={"_id": 0})))


    df["value"] = round(df["value"] * 1000, 1)
    df = df.drop(df[df['value'] == 0.0].index)
    return df

pd.options.display.float_format = '{:.2f}'.format

experiences = { "Baseline": [1,2,3,4,5], "CPU": [6,7,8], "Nice": [9,10], "Limite de banda": [11,12,13], "CPU e Nice": [14,15,16], "CPU e Limite de banda": [17,18,19,20,21,22], "CPU e Nice e Limite de banda": [23,24,25,26], 
                "CPU 1000": [6,14,17,20,23,24], "CPU 1000 and 500": [7,15,18,21,25,26],  "CPU 1000 and 250": [8,16,18,21,25,26], "Nice -5 and 5": [10,14,15,16,23,24,25,26],
                "Limite de banda ativo": [11,17,18,19,23,25], "Limite de banda 150": [12,20,21,22,24,26]}

df = plotReceiveBoxPlot("receive", [f"open5gs-upf-{i:d}" for i in range(1, 6)])
df2 = df.groupby(["exp", "priority"])["value"].describe() #.unstack()
df2['IQR'] = df2['75%'] - df2['25%']
df2['lower_limit'] = df2['25%'] - 1.5 * df2['IQR']
df2['upper_limit'] = df2['75%'] - 1.5 * df2['IQR']

df_exp2 = df2.loc[df2.index.get_level_values('priority') == "open5gs-upf-1"]
df_exp2 = df_exp2.rename(columns={'count': 'quantidades', 'mean': 'Média', 'std': 'Desvio Padrão', 'min': 'mínimo', '25%': 'Q1', '50%': 'Mediana', '75%': 'Q3', 'max': 'máximo', 'IQR': 'IQR', 'lower_limit': 'Limite inferior', 'upper_limit': 'Limite superior'})
df_exp2 = df_exp2[['Limite inferior', 'Q1', 'Mediana',  'Média', 'Q3', "Limite superior", 'Desvio Padrão']]
df_exp2 = df_exp2.reset_index(level='priority').drop(columns=['priority'])

counter = 0
for k, e in experiences.items(): 
    df_exp_filtered = df_exp2[df_exp2.index.get_level_values('exp').isin(e)]
    df_exp_filtered = df_exp_filtered.applymap(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
    df_exp_filtered = df_exp_filtered.reset_index()

    print(f"\n\n\nExperiencias {e}")
    print(df_exp_filtered.to_latex(index=False))
    

df = plotLatencyBoxPlotPrep("latency", [f"open5gs-my5gran0{i:d}" for i in range(1, 6)], last5m=True, Filter="priority")
print(df)
df2 = df.groupby(["exp", "priority"])["value"].describe() #.unstack()
df2['IQR'] = df2['75%'] - df2['25%']
df2['lower_limit'] = df2['25%'] - 1.5 * df2['IQR']
df2['upper_limit'] = df2['75%'] - 1.5 * df2['IQR']

df_exp2 = df2.loc[df2.index.get_level_values('priority') == "Slice 01"]
df_exp2 = df_exp2.rename(columns={'count': 'quantidades', 'mean': 'Média', 'std': 'Desvio Padrão', 'min': 'mínimo', '25%': 'Q1', '50%': 'Mediana', '75%': 'Q3', 'max': 'máximo', 'IQR': 'IQR', 'lower_limit': 'Limite inferior', 'upper_limit': 'Limite superior'})
df_exp2 = df_exp2[['Limite inferior', 'Q1', 'Mediana',  'Média', 'Q3', "Limite superior", 'Desvio Padrão']]
df_exp2 = df_exp2.reset_index(level='priority').drop(columns=['priority'])

counter = 0
for k, e in experiences.items(): 
    df_exp_filtered = df_exp2[df_exp2.index.get_level_values('exp').isin(e)]
    df_exp_filtered = df_exp_filtered.applymap(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
    df_exp_filtered = df_exp_filtered.reset_index()

    print(f"\n\n\nExperiencias {e}")
    print(df_exp_filtered.to_latex(index=False))