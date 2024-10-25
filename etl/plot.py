import re
import pytz
import numpy as np
import os
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


def getCollection(collection):    
    global mongoUrl   
    global dbName 
    conn = MongoClient(mongoUrl)        
    return conn[dbName][collection]


def plotLineReceivePrep(workloads, exp):
    
    col = getCollection("receive_workload_avg_ts")
    df = pd.DataFrame(list(col.find(filter={"workload": {"$in": workloads}, "exp": exp}, projection={"_id": 0, "avg": 1, "workload": 1, "ts": 1}).sort({"ts": 1})))
    df["avg"] = round(df["avg"] / 1024 / 1024, 3)
    df_pivot = df.pivot(index='ts', columns='workload', values='avg').fillna(0)
    return df_pivot

def plotLineCPUPrep(workloads, exp):
    col = getCollection("cpu_workload_avg_ts")
    df = pd.DataFrame(list(col.find(filter={"workload": {"$in": workloads}, "exp": exp}, projection={"_id": 0, "avg": 1, "workload": 1, "ts": 1}).sort({"ts": 1})))
    df["avg"] = round(df["avg"] * 1000, 1)

    df_pivot = df.pivot(index='ts', columns='workload', values='avg').fillna(0)
    return df_pivot


def plotLine(df, title, x_label, y_label, filename, ylimit=700):
    plt.figure(figsize=(12, 6))
    plt.stackplot(df.index, df.T, labels=df.columns)

    plt.gca().xaxis.set_major_locator(MultipleLocator(240))
    plt.gca().xaxis.set_minor_locator(MultipleLocator(60))
    
    plt.gca().yaxis.set_major_locator(MultipleLocator(ylimit / 10))
    plt.gca().yaxis.set_minor_locator(MultipleLocator(ylimit / 50))
    
    plt.gca().grid(which='major', color='#5b5b5b', linestyle='-', linewidth=0.5)
    plt.gca().grid(which='minor', color='#8c8c8c', linestyle=':', linewidth=0.5)
    
    plt.title(title, loc="center", fontsize=20)
    plt.ylim(0, ylimit)
    plt.xlim(0, 1200)
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    plt.legend(loc='upper left')   
    plt.tight_layout()
    plt.savefig(f"line\\{filename}.pdf")
    plt.savefig(f"line\\{filename}.png")

    plt.close()

if not os.path.exists("line"):
    os.mkdir("line")

for i in range(1, 26):
    df = plotLineReceivePrep([f"open5gs-iperf0{i:d}" for i in range(1, 6)], i)
    plotLine(df, f"Trágefo de dados recebido nos IPERFS (experimento {i})", "Tempo (segundos)", "Taxa de dados (Mbit/s)", f"line_receive_iperf_exp{i}")
    
    df = plotLineCPUPrep([f"open5gs-upf-{i:d}" for i in range(1, 6)], i)
    plotLine(df, f"Uso de CPU nos UPFs (experimento {i})", "Tempo (segundos)", "Uso CPU (milicpu)", f"line_cpu_upf_exp{i}",ylimit=4000)
