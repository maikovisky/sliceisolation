import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pymongo import MongoClient


conn = MongoClient("mongodb://127.0.0.1:27017")  
db = conn["open5gsNice"]
col = db["ts"]

pipeline = [
    #{ "$match": { "metadata.type": "latency", "metadata.experiment": {"$in": ["01", "02", "03", "04", "05"] }}},
    { "$match": { "metadata.type": "latency"}},
    { "$group": { 
            "_id": {"experiment": "$metadata.experiment", "job": "$metadata.job"},  
            "std": { "$stdDevPop": "$value" },
            "avg": { "$avg": "$value" },
            "percentile": { "$percentile": { "input": "$value", "p": [ 0.25, 0.5, 0.75 ], "method": 'approximate'}},
            "iqr": { "$percentile": { "input": "$value", "p": [ 0.25, 0.5, 0.75 ], "method": 'approximate'}},
            "count": {"$count": {}}
        } 
    },
    { "$project": {
        "_id": 0,
        "experiment": "$_id.experiment",
        "slice": { "$substr": [ "$_id.job", 10,-2] },
        "count": 1,
        "std": 1,
        "avg": 1,
        "p25": {"$arrayElemAt": [ "$percentile", 0 ]},
        "p50": {"$arrayElemAt": [ "$percentile", 1 ]},
        "p75": {"$arrayElemAt": [ "$percentile", 2 ]},
        "iqr": { "$subtract": [{"$arrayElemAt": [ "$percentile", 2 ]}, {"$arrayElemAt": [ "$percentile", 0 ]}] }
    }},
    #{ "$match": { "slice": "01"}},
    { "$project": {
        "experiment": 1,
        "slice": 1,
        "count": 1,
        "std": 1,
        "avg": 1,
        "outlierlower": {"$subtract": ["$p50", {"$multiply": ["$iqr", 1.5]}]},
        "outlierhight": {"$add": ["$p50", {"$multiply": ["$iqr", 1.5]}]}
    }},
    {"$sort": {"experiment": 1, "slice": 1}}
]

cursor = col.aggregate(pipeline)
df = pd.DataFrame(list(cursor))

#print(df.to_latex())

colors = ['#e6f2e4', '#fbf4d9', '#e7f0fe', '#ffe8d9', '#fbe0e3']
line   = ['#61a745', '#e3ca60', '#6e99e5', '#f9a57d', '#ed8793']
plt.figure(figsize =(11, 6))
#fig.tight_layout()


ax = sns.barplot(df, x="experiment", y="avg", hue="slice", palette=line, estimator="sum", errorbar=None)
ax.bar_label(ax.containers[0], fontsize=9, fmt="%0.3f");
ax.bar_label(ax.containers[1], fontsize=9, fmt="%0.3f");
ax.bar_label(ax.containers[2], fontsize=9, fmt="%0.3f");
ax.bar_label(ax.containers[3], fontsize=9, fmt="%0.3f");
ax.bar_label(ax.containers[4], fontsize=10, fmt="%0.3f");

plt.title("Média de latência", loc="center", fontsize=18)
plt.xlabel("Slices")
plt.ylabel("Latência (segundos)")
plt.grid()
# Salvando o gráfico em um arquivo PNG
plt.savefig('barplot_avg_latency.png', bbox_inches='tight')

# Fechando a figura para liberar memória
plt.close()