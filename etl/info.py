import re
import pytz
import numpy as np
import bitmath
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
from datetime import datetime
from os import walk
from prometheus_pandas import query
import pandas as pd
from pymongo import MongoClient


prometeusUrl = "http://localhost:9090"
basepath = "../../experimentos/experimentos/"
mongoUrl = "mongodb://localhost:27017/"
dbName  = "metrics"


def getDatabase(database):    
    global mongoUrl    
    conn = MongoClient(mongoUrl)        
    return conn[database]

def getReceiveBytes(start, end):
    global prometeusUrl
    start = redefineDate(start)
       
    p = query.Prometheus(prometeusUrl)
    return p.query_range(
        "sort_desc(sum(rate(container_network_receive_bytes_total{job='kubelet', metrics_path='/metrics/cadvisor', namespace='open5gs', interface=~'(slice01|slice02|slice03|slice04|slice05)'}[2m0s]) * on (namespace,pod) group_left(workload,workload_type) namespace_workload_pod:kube_pod_owner:relabel{namespace='open5gs', workload=~'(open5gs-upf-1|open5gs-upf-2|open5gs-upf-3|open5gs-upf-4|open5gs-upf-5)'}) by (workload, interface) * 8)",
        start, end, "30s"
    )
    
def getReceiveIperfBytes(start, end):
    global prometeusUrl
    start = redefineDate(start)
       
    p = query.Prometheus(prometeusUrl)
    return p.query_range(
        "sort_desc(sum(rate(container_network_receive_bytes_total{job='kubelet', metrics_path='/metrics/cadvisor', namespace='open5gs', interface=~'(eth0)'}[2m0s]) * on (namespace,pod) group_left(workload,workload_type) namespace_workload_pod:kube_pod_owner:relabel{namespace='open5gs', workload=~'(open5gs-iperf01|open5gs-iperf02|open5gs-iperf03|open5gs-iperf04|open5gs-iperf05)'}) by (workload, interface) * 8)",
        start, end, "30s"
    )
    
def getCPU(start, end):
    global prometeusUrl
    start = redefineDate(start)
       
    p = query.Prometheus(prometeusUrl)
    return p.query_range(
        "sort_desc(sum(node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate{namespace='open5gs'} * on(namespace ,pod) group_left(workload, workload_type) namespace_workload_pod:kube_pod_owner:relabel{namespace='open5gs', workload=~'(open5gs-upf-1|open5gs-upf-2|open5gs-upf-3|open5gs-upf-4|open5gs-upf-5)'}) by (workload))",
        start, end, "30s"
    )

def getLatency(start, end):
    global prometeusUrl
    start = redefineDate(start)
       
    p = query.Prometheus(prometeusUrl)
    return p.query_range(
        "sort_desc(avg(rate(ping_average_response_ms{namespace='open5gs', service=~'(open5gs-my5gran01|open5gs-my5gran02|open5gs-my5gran03|open5gs-my5gran04|open5gs-my5gran05)'}[2m0s])) by(job))",
        start, end, "30s"
    )

def redefineDate(d):
    dt = datetime.strptime(d, "%Y-%m-%dT%H:%M:%S.%fZ")
    if(dt.second >= 30):
        dt = dt.replace(second=30, microsecond=0)
    else:
        dt = dt.replace(second=0, microsecond=0)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def getTimestamps(exp, cicle):
    global basepath
    filename = "{}experiment{:02d}/exp{:04d}/experiment{:02d}-grafana.txt".format(basepath, exp, cicle, exp)
    f = open(filename, 'r')
    t = f.readline()
    g = re.search("&from=(\\d+)&to=(\\d+)", t, re.IGNORECASE)
    start = datetime.fromtimestamp(int(int(g.group(1)) / 1000), tz=pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end   = datetime.fromtimestamp(int(int(g.group(2)) / 1000), tz=pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    start = redefineDate(start)
    return start, end

def getCicle(base):
    global basepath
    b = "{}{}".format(basepath, base)
    path = next(walk(b), (None, None, []))[1]  # [] if no file
    experiment = int(base[-2:])
    for p in path:
        cicle = int(p[-4:])
        start, end = getTimestamps(int(experiment), int(cicle))
        
        # Pega dados de rede dos UPF
        df = getData(getReceiveBytes(start, end), experiment, cicle)
        saveReceiveData(experiment, cicle, df)
        
        # Pega dados de rede dos IPERF
        df = getData(getReceiveIperfBytes(start, end), experiment, cicle)
        saveReceiveIperfData(experiment, cicle, df)
        
        df = getData(getCPU(start, end), experiment, cicle)
        saveCPUData(experiment, cicle, df)
        
        df = getData(getLatency(start, end), experiment, cicle)
        saveLatencyData(experiment, cicle, df)


def getAll(ignore=[]):
    global basepath
    path = next(walk(basepath), (None, None, []))[1]  # [] if no file
    for p in path:
        if p in ignore:
            continue
        print(f"Capturando dados de {p}")
        getCicle(p)


def getData(df, exp, cicle):
    df.reset_index(inplace=True)
    df["ts"] = df["index"].apply(lambda x: pd.Timestamp(x))    
    df["ts"] = (df["index"].astype("int64") / 1000000).astype("int64")
    ts = df['ts'].agg(['min', 'max'])
    df["ts"] = ((df['ts'] - ts["min"])/1000).astype("int64")
    df["exp"] = exp
    df["cicle"] = cicle
    return df
    
    
def saveToMongo(df, col, workload, interface=None):
    global dbName
    df2 = df[["ts", "exp", "cicle", workload]].rename(columns={workload: 'value'})
    df2["workload"] = workload
    df2["priority"] = workload if workload in ["open5gs-upf-1", "open5gs-iperf01"]  else "others"
    if interface is not None:
        df2["interface"] = interface
    getDatabase(dbName)[col].insert_many(df2.to_dict("records"))
    
def saveReceiveData(exp, cicle, df):
    df = df.reset_index(inplace=False)
    df = df.rename(columns={'{interface="slice01",workload="open5gs-upf-1"}': "open5gs-upf-1", '{interface="slice02",workload="open5gs-upf-2"}': "open5gs-upf-2",
                            '{interface="slice03",workload="open5gs-upf-3"}': "open5gs-upf-3", '{interface="slice04",workload="open5gs-upf-4"}': "open5gs-upf-4",
                            '{interface="slice05",workload="open5gs-upf-5"}': "open5gs-upf-5", 'index': 'dt', 'level_0': 'idx'})
    #df = df.reset_index(inplace=False)
    filename = "{}experiment{:02d}/exp{:04d}/experiment{:02d}-data.csv".format(basepath, exp, cicle, exp)
    df.to_csv(filename, index=False)
    filename = "{}experiment{:02d}/exp{:04d}/experiment{:02d}-mean.csv".format(basepath, exp, cicle, exp)
    df_mean = df.describe().loc[['min','mean','max','std']]
    df_mean.to_csv(filename)
    for n in range(1, 6):
        saveToMongo(df, "receive", f"open5gs-upf-{n}", f"slice0{n}")

def saveReceiveIperfData(exp, cicle, df):
    df = df.reset_index(inplace=False)
    df = df.rename(columns={'{interface="eth0",workload="open5gs-iperf01"}': "open5gs-iperf01", '{interface="eth0",workload="open5gs-iperf02"}': "open5gs-iperf02",
                            '{interface="eth0",workload="open5gs-iperf03"}': "open5gs-iperf03", '{interface="eth0",workload="open5gs-iperf04"}': "open5gs-iperf04",
                            '{interface="eth0",workload="open5gs-iperf05"}': "open5gs-iperf05", 'index': 'dt', 'level_0': 'idx'})
    filename = "{}experiment{:02d}/exp{:04d}/experiment{:02d}-iperf-data.csv".format(basepath, exp, cicle, exp)
    df.to_csv(filename, index=False)
    filename = "{}experiment{:02d}/exp{:04d}/experiment{:02d}-iperf-mean.csv".format(basepath, exp, cicle, exp)
    df_mean = df.mean().to_csv(filename)
    df.reset_index(inplace=True)
    for n in range(1, 6):
        saveToMongo(df, "receive", f"open5gs-iperf0{n}", "eth0")


def saveCPUData(exp, cicle, df):
    df = df.reset_index(inplace=False)
    df = df.rename(columns={'{workload="open5gs-upf-1"}': "open5gs-upf-1", '{workload="open5gs-upf-2"}': "open5gs-upf-2",
                            '{workload="open5gs-upf-3"}': "open5gs-upf-3", '{workload="open5gs-upf-4"}': "open5gs-upf-4",
                            '{workload="open5gs-upf-5"}': "open5gs-upf-5", 'index': 'dt', 'level_0': 'idx'})
    filename = "{}experiment{:02d}/exp{:04d}/experiment{:02d}-cpu-data.csv".format(basepath, exp, cicle, exp)
    df.to_csv(filename, index=False)
    filename = "{}experiment{:02d}/exp{:04d}/experiment{:02d}-cpu-mean.csv".format(basepath, exp, cicle, exp)
    df_mean = df.mean().to_csv(filename)
    df.reset_index(inplace=True)
    for n in range(1, 6):
        saveToMongo(df, "cpu", f"open5gs-upf-{n}")

def saveToMongoAll(df, col, prefix_workload, interface=None, ranger=6):
    for n in range(1, ranger):
        if f"{prefix_workload}{n}" not in df.columns:
            break
        saveToMongo(df, col, f"{prefix_workload}{n}", interface)
    
def saveLatencyData(exp, cicle, df):
    df = df.reset_index(inplace=False)
    df = df.rename(columns={'{job="open5gs-my5gran01"}': "open5gs-my5gran01", '{job="open5gs-my5gran02"}': "open5gs-my5gran02",
                            '{job="open5gs-my5gran03"}': "open5gs-my5gran03", '{job="open5gs-my5gran04"}': "open5gs-my5gran04",
                            '{job="open5gs-my5gran05"}': "open5gs-my5gran05", 'index': 'dt', 'level_0': 'idx'})  
    filename = "{}experiment{:02d}/exp{:04d}/experiment{:02d}-latency-data.csv".format(basepath, exp, cicle, exp)
    df.to_csv(filename, index=False)
    filename = "{}experiment{:02d}/exp{:04d}/experiment{:02d}-latency-mean.csv".format(basepath, exp, cicle, exp)
    df_mean = df.mean().to_csv(filename)
    df.reset_index(inplace=True)
    saveToMongoAll(df, "latency", "open5gs-my5gran0")


def aggMongo():
    global mongoUrl
    global dbName
    conn = MongoClient(mongoUrl)   
    collections = ["receive", "cpu", "latency"]
    filters = ["workload", "priority"]
    
    for col in collections:
        # Agregação com média, mínimo, máximo, desvio padrão e contagem agrupando por workload, experimento e timestamp
        for filter in filters:
            print(f"Agregando dados de {col} por {filter}")
            conn[dbName][col].aggregate([
                { "$match": {"value": {"$gt": 0.0}} },
                { "$group": { "_id": {"workload": f"${filter}", "exp": "$exp", "ts": "$ts"}, "avg": {"$avg": "$value"}, "min": {"$min": "$value"}, "max": {"$max": "$value"}, 
                            "std": {"$stdDevPop": "$value"}, "count": {"$sum": 1}, "workload": {"$first": f"${filter}"}, "exp": {"$first": "$exp"}, "ts": {"$first": "$ts"}, "priority": {"$first": "$priority"}} },
                { "$out" : f"{col}_{filter}_avg_ts" }
            ])
            
            # Agregação com média, mínimo, máximo, desvio padrão e contagem agrupando por workload e experimento
            conn[dbName][col].aggregate([
                { "$match": {"value": {"$gt": 0.0}} },
                { "$group": { "_id": {"workload": f"${filter}", "exp": "$exp"}, "avg": {"$avg": "$value"}, "min": {"$min": "$value"}, "max": {"$max": "$value"}, 
                            "std": {"$stdDevPop": "$value"}, "count": {"$sum": 1}, "workload": {"$first": f"${filter}"}, "exp": {"$first": "$exp"}, "priority": {"$first": "$priority"}} },
                { "$out" : f"{col}_{filter}_avg" }
            ])
            
            # Agregação com média, mínimo, máximo, desvio padrão e contagem agrupando por workload e experimento e filtrando por timestamp maior que 900
            conn[dbName][col].aggregate([
                { "$match": {"ts": {"$gte": 900}, "value": {"$gt": 0.0}} },
                { "$group": { "_id": {"workload": f"${filter}", "exp": "$exp"}, "avg": {"$avg": "$value"}, "min": {"$min": "$value"}, "max": {"$max": "$value"}, 
                            "std": {"$stdDevPop": "$value"}, "count": {"$sum": 1}, "workload": {"$first": f"${filter}"}, "exp": {"$first": "$exp"}, "priority": {"$first": "$priority"} }},
                { "$out" : f"{col}_{filter}_avg_last_5m" }
            ])
        

def resetDatabase(backup=False):
    global mongoUrl
    global dbName
    conn = MongoClient(mongoUrl)     
    if backup:
        db_name = "metrics_backup-{}".format(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        #conn.drop_database("metrics_backup")
        #conn.admin.command('copydb', fromdb='metrics', todb=db_name)   

    conn.drop_database(dbName)

def plotCPUPrep(workloads=["open5gs-upf-1", "open5gs-upf-2", "open5gs-upf-3","open5gs-upf-4", "open5gs-upf-5"], last5m=False, Filter="workload"):
    global mongoUrl
    global dbName
    conn = MongoClient(mongoUrl) 
    db = conn[dbName]
    dbname = f"cpu_{Filter}_avg_last_5m" if last5m else f"cpu_{Filter}_avg"


    df = pd.DataFrame(list(db[dbname].find(filter={"workload": {"$in": workloads}}, projection={"_id": 0})))
    df = df.pivot(index="exp", columns="workload", values="avg")
    df = df.reset_index(inplace=False)
    for w in workloads:
        if w not in df.columns:
            break
        df[w] = round(df[w] * 1000, 3)
        
    return df

def plotLatencyPrep(workloads, last5m=False, Filter="workload"):
    global mongoUrl
    global dbName
    conn = MongoClient(mongoUrl) 
    db = conn[dbName]
    dbname = f"latency_{Filter}_avg_last_5m" if last5m else f"latency_{Filter}_avg"

    df = pd.DataFrame(list(db[dbname].find(filter={"workload": {"$in": workloads}}, projection={"_id": 0})))
    #print(df)
    df = df.pivot(index="exp", columns="workload", values="avg")
    df = df.reset_index(inplace=False)
    for w in workloads:
        if w not in df.columns:
            break
        df[w] = round(df[w] * 1000, 1)
        
    return df
    
def plotReceivePrep(workloads=["open5gs-upf-1", "open5gs-upf-2", "open5gs-upf-3","open5gs-upf-4", "open5gs-upf-5"], last5m=False, Experinces=None, Filter="workload"):
    global mongoUrl
    global dbName
    conn = MongoClient(mongoUrl) 
    db = conn[dbName]
    dbname = f"receive_{Filter}_avg_last_5m" if last5m else f"receive_{Filter}_avg"
 
    if Experinces is not None:
        df = pd.DataFrame(list(db[dbname].find(filter={"workload": {"$in": workloads}, "exp": {"$in": Experinces}}, projection={"_id": 0})))
    else:
        df = pd.DataFrame(list(db[dbname].find(filter={"workload": {"$in": workloads}}, projection={"_id": 0})))
        
    df = df.pivot(index="exp", columns="workload", values="avg")
    df = df.reset_index(inplace=False)
    for w in workloads:
        df[w] = round(df[w] / 1024 / 1024, 3)
    
    return df
   
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

def plotData(df, title="Consumo de Rede dos UPFs", output="consumo_rede_upf.png", style="seaborn-v0_8", ylabel="Consumo (Mbps)"):
    print(f"Plotando gráfico barra de {title}")
    plt.figure(figsize=(30, 15))
    plt.style.use(style)

    df.plot(kind="bar", x="exp", stacked=False,  grid=True, figsize=(30, 15), width=0.8)
    df.set_index('exp', inplace=True)
    df_transposed = df.transpose()
    #print(df_transposed)
    
    .yaxis.set_major_locator(MultipleLocator(20))
    ax.yaxis.set_minor_locator(MultipleLocator(4))
    ax.grid(which='major', color='#CCCCCC', linestyle='--')
    ax.grid(which='minor', color='#CCCCCC', linestyle=':')
    
    plt.title(title, fontsize=24, fontweight='bold')
    
    plt.ylim(0, 200)
    plt.xlabel('Experimento', fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', prop={'size': 11}, title="Slices")
    plt.subplots_adjust(bottom=0.1)
    plt.gcf().autofmt_xdate()
    #plt.subplots_adjust(wspace=0.0)  # Ajuste conforme necessário

    
    ax_table = plt.subplot(212) 
    ax_table.axis('tight')
    ax_table.axis('off')
    ax_table.set_position([0.1, 0.05, 0.8, 0.6])
    ax_table.table(cellText=df_transposed.values, rowLabels=df_transposed.index, edges='horizontal', bbox=[0, 0, 1, 0.15], fontsize=16)

    
    # Salvando o gráfico em um arquivo PNG
    plt.savefig(output, bbox_inches='tight')
    #plt.add_Trace(go.Bar(x=df['workload'], y=df['avg'], name='avg'))

    plt.close()
    
def plotBoxPlot(df, title, output, hue="priority"):
    print(f"Plotando gráfico BoxPlot de {title}")
    plt.figure(figsize=(20, 8))
    sns.set_style("whitegrid")
    ax = sns.boxplot(data=df, x="exp", y="value", hue=hue, palette="Set3", linewidth=2)
    #ax.tick_params(axis='y', direction="inout", length=25)
    ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.yaxis.set_minor_locator(MultipleLocator(4))
    ax.grid(which='major', color='#CCCCCC', linestyle='--')
    ax.grid(which='minor', color='#CCCCCC', linestyle=':')
    ax.set_ylim([0, 200])
    plt.legend(title="Slice")

    # Gráfico de disperção
    #ax = sns.stripplot(x = "exp", y ="value", hue="priority" ,data = df)  
    
    plt.title(title, loc="center", fontsize=20)
    plt.xlabel("Experimentos", fontsize=14)
    plt.ylabel("Consumo (Mbps)", fontsize=14)


    # Salvando o gráfico em um arquivo PNG
    plt.savefig(output, bbox_inches='tight')
    #plt.add_Trace(go.Bar(x=df['workload'], y=df['avg'], name='avg'))

    plt.close()
    
# df = plotReceivePrep([f"open5gs-upf-{i:d}" for i in range(1, 6)], False)    
# for style in plt.style.available:
#     df = plotReceivePrep([f"open5gs-upf-{i:d}" for i in range(1, 6)], False) 
#     plotReceive(df, title=f"{style}", output=f"{style}.png", style=style)


def plotExperienceGroups():
    experiences = { "Baseline": [1,2,3,4,5], "CPU": [6,7,8], "Nice": [9,10,11], "Band": [11,12,13], "CPU e Nice": [14,15,16], "CPU e Banda": [17,18,19,20,21,22], "CPU e Nice e Banda": [23,24,25,26]}
    counter = 0
    for k, e in experiences.items():
        counter+=1
        print(f"Plotando gráficos das experiências {e}")
        df = plotReceivePrep([f"open5gs-upf-{i:d}" for i in range(1, 6)], True, e)         
        plotData(df, title=f"Dados recebidos nos UPFs (últimos 5 min) ({k})", output=f"plot_receive_{k}_upf_last5m.png")

        df = plotReceivePrep(["open5gs-upf-1", "others"], True, e, "priority")         
        plotData(df, title=f"Dados recebidos nos UPFs (últimos 5 min) ({k}) com agrupamento", output=f"plot_receive_{k}_upf_group_last5m.png")
        
        df = plotReceivePrep([f"open5gs-upf-{i:d}" for i in range(1, 6)], False, e)         
        plotData(df, title=f"Dados recebidos nos UPFs (últimos 5 min) ({k})", output=f"plot_receive_{k}_upf.png")

        df = plotReceivePrep(["open5gs-upf-1", "others"], False, e, "priority")         
        plotData(df, title=f"Dados recebidos nos UPFs (últimos 5 min) ({k}) com agrupamento", output=f"plot_receive_{k}_upf_group.png")
        
        df = plotReceiveBoxPlot("receive", [f"open5gs-upf-{i:d}" for i in range(1, 2)], e)
        plotBoxPlot(df, title=f"Dados recebidos nos UPFs (últimos 5 min) - {k}", output=f"boxplot_receive_{k}.png")

        df = plotReceiveBoxPlot("receive", [f"open5gs-iperf{i:02d}" for i in range(1, 2)], e)
        plotBoxPlot(df, title=f"Dados recebidos nos IPERFs (últimos 5 min) - {k}", hue="workload", output=f"boxplot_receive_{k}_iperf.png")

        df = plotReceiveBoxPlot("receive", [f"open5gs-upf-{i:d}" for i in range(1, 6)], e)
        plotBoxPlot(df, title=f"Dados recebidos nos UPFs (últimos 5 min) - {k}", hue="priority", output=f"boxplot_receive_{k}_other.png")

        df = plotReceiveBoxPlot("receive", [f"open5gs-iperf{i:02d}" for i in range(1, 6)], e)
        plotBoxPlot(df, title=f"Dados recebidos nos IPERFs (últimos 5 min) - {k}", hue="priority", output=f"boxplot_receive_{k}_other_iperf.png")


# resetDatabase()
# getAll()
aggMongo()
plotExperienceGroups()

df = plotReceivePrep([f"open5gs-upf-{i:d}" for i in range(1, 6)], True, [6,7,8])         
plotData(df, title="Dados recebidos nos UPFs (últimos 5 min)", output="plot_receive_upf_last5m.png")

df = plotReceivePrep(["open5gs-upf-1", "others"], True, [6,7,8], "priority")         
plotData(df, title="Dados recebidos nos UPFs (últimos 5 min) com agrupamento", output="plot_receive_upf_group_last5m.png")

df = plotReceiveBoxPlot("receive", [f"open5gs-upf-{i:d}" for i in range(1, 2)])
plotBoxPlot(df, title="Dados recebidos nos UPFs (últimos 5 min)", output="boxplot_receive.png")

df = plotReceiveBoxPlot("receive", [f"open5gs-iperf{i:02d}" for i in range(1, 2)])
plotBoxPlot(df, title="Dados recebidos nos IPERFs (últimos 5 min)", hue="workload", output="boxplot_receive_iperf.png")

df = plotReceiveBoxPlot("receive", [f"open5gs-upf-{i:d}" for i in range(1, 6)])
plotBoxPlot(df, title="Dados recebidos nos UPFs (últimos 5 min)", hue="priority", output="boxplot_receive_other.png")

df = plotReceiveBoxPlot("receive", [f"open5gs-iperf{i:02d}" for i in range(1, 6)])
plotBoxPlot(df, title="Dados recebidos nos IPERFs (últimos 5 min)", hue="priority", output="boxplot_receive_other_iperf.png")

df = plotReceivePrep([f"open5gs-upf-{i:d}" for i in range(1, 6)], False)
plotData(df, title="Dados recebidos nos UPFs", output="plot_receive_upf.png")
  
df = plotReceivePrep([f"open5gs-upf-{i:d}" for i in range(1, 6)], True)         
plotData(df, title="Dados recebidos nos UPFs (últimos 5 min)", output="plot_receive_upf_last5m.png")


df = plotReceivePrep([f"open5gs-iperf{i:02d}" for i in range(1, 6)], False)
plotData(df, title="Dados recebidos nos IPERFs", output="plot_receive_iperf.png")
  
df = plotReceivePrep([f"open5gs-iperf{i:02d}" for i in range(1, 6)], True)        
plotData(df, title="Dados recebidos nos IPERFs (últimos 5 min)", output="plot_receive_iperf_last5m.png")
 

for n in range(1, 6):
   df = plotReceivePrep(["open5gs-upf-{}".format(n), "open5gs-iperf0{}".format(n)], True)
   plotData(df,  f"Comparação de dados recebidos entre UPF-{n} e IPERF-{n} (últimos 5 min)", f"plot_receive_upf-iperf_slice0{n}.png")

# Plot CPU
df = plotCPUPrep([f"open5gs-upf-{i:d}" for i in range(1, 6)], False)
plotData(df, title="Uso de CPU dos UPFs", output="plot_cpu.png", ylabel="Milicpu (m)")

df = plotCPUPrep([f"open5gs-upf-{i:d}" for i in range(1, 6)], True)
plotData(df, title="Uso de CPU dos UPFs (últimos 5 min)", output="plot_cpu_last5m.png", ylabel="Milicpu (m)")

# Plot Latency
df = plotLatencyPrep([f"open5gs-my5gran0{i:d}" for i in range(1, 6)], False)
plotData(df, title="Latência entre UE e IPERF", output="plot_latency.png", ylabel="Milliseconds (ms)")

df = plotLatencyPrep([f"open5gs-my5gran0{i:d}" for i in range(1, 6)], True)
plotData(df, title="Latência entre UE e IPERF (últimos 5 min)", output="plot_latency_last5m.png", ylabel="Milliseconds (ms)")


 
