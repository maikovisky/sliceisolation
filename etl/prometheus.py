import json
import pytz
import requests
import bitmath
import matplotlib.pyplot as plt
from datetime import datetime
#from bson.timestamp import Timestamp
from pymongo import MongoClient
import pandas as pd
from prometheus_pandas import query
import numpy as np

# apiEndpoint = "http://localhost:9090/api/v1/query_range?start=2024-09-14T14:08:57.000Z&end=2024-09-14T14:30:55.000Z&step=5s&query=(sum(rate(container_network_receive_bytes_total{job='kubelet', metrics_path='/metrics/cadvisor', namespace='open5gs'}[30s]) * on (namespace,pod) group_left(workload,workload_type) namespace_workload_pod:kube_pod_owner:relabel{namespace='open5gs'}) by (workload, interface))"
# txt = requests.get(apiEndpoint).text
# j = json.loads(txt)
# result = j["data"]["result"]

# print(result)

# #dataFrame = pd.read_json(j)
# #print(dataFrame)

def redefineDate(d):
    dt = datetime.strptime(d, "%Y-%m-%dT%H:%M:%S.%fZ")
    print(dt.minute)
    if(dt.second >= 30):
        dt = dt.replace(second=30, microsecond=0)
    else:
        dt = dt.replace(second=0, microsecond=0)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def getPlot(df):
    df.reset_index(inplace=True)
    df["ts"] = df["index"].apply(lambda x: pd.Timestamp(x))    
    df["ts"] = (df["index"].astype("int64") / 1000000).astype("int64")
    ts = df['ts'].agg(['min', 'max'])
    df2 = df[['{interface="slice01",workload="open5gs-upf-1"}', 'ts']].dropna()
    df2['open5gs-upf-1'] = df2['{interface="slice01",workload="open5gs-upf-1"}'] / 1000000

    plt.figure(figsize=(20, 5))
    plt.plot(df2['ts'], df2['open5gs-upf-1'], marker='o', linestyle='-')

    # Adicionando título e rótulos
    plt.title('Consumo de Rede ao Longo do Tempo')
    plt.xlabel('Tempo')
    plt.ylabel('Consumo (Mbps)')

    # Formatando o eixo x para mostrar datas de forma legível
    plt.gcf().autofmt_xdate()

    # Salvando o gráfico em um arquivo PNG
    plt.savefig('consumo_rede.png')

    # Fechando a figura para liberar memória
    plt.close()
    

def getPrometheus(q, start, end):
    start = redefineDate(start)
    print(start)
       
    p = query.Prometheus('http://localhost:9090')
    return p.query_range(
        "sort_desc(sum(rate(container_network_receive_bytes_total{job='kubelet', metrics_path='/metrics/cadvisor', namespace='open5gs', interface=~'(slice01|slice02|slice03|slice04|slice05)'}[2m0s]) * on (namespace,pod) group_left(workload,workload_type) namespace_workload_pod:kube_pod_owner:relabel{namespace='open5gs', workload=~'(open5gs-upf-1|open5gs-upf-2|open5gs-upf-3|open5gs-upf-4|open5gs-upf-5)'}) by (workload, interface) * 8)",
        start, end, "30s"
    )

start = datetime.fromtimestamp(1726707755, tz=pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
end   = datetime.fromtimestamp(1726708959, tz=pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
print(start)
print(end)

df = getPrometheus("", start, end)
df.reset_index(inplace=True)
df["ts"] = df["index"].apply(lambda x: pd.Timestamp(x))    
df["ts"] = (df["index"].astype("int64") / 1000000).astype("int64")
#print(df["ts"].min)
ts = df['ts'].agg(['min', 'max'])
df["ts"] = ((df['ts'] - ts["min"])/1000).astype("int64")
#df = df.set_index('ts')
#print(df[['{interface="slice02",workload="open5gs-upf-2"}', 'ts']].dropna())
#print(df)

df2 = df[['{interface="slice02",workload="open5gs-upf-2"}', 'ts']].dropna()
df2['open5gs-upf-1'] = df2['{interface="slice02",workload="open5gs-upf-2"}'] / 1000000
#print(df2.describe())

plt.figure(figsize=(20, 5))
plt.plot(df2['ts'], df2['open5gs-upf-1'], marker='o', linestyle='-')

# Adicionando título e rótulos
plt.title('Consumo de Rede ao Longo do Tempo')
plt.xlabel('Tempo')
plt.ylabel('Consumo (Mbps)')

# Formatando o eixo x para mostrar datas de forma legível
plt.gcf().autofmt_xdate()

# Salvando o gráfico em um arquivo PNG
plt.savefig('consumo_rede.png')

# Fechando a figura para liberar memória
plt.close()