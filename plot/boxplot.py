import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pymongo import MongoClient
import datetime



plt.figure(figsize =(11, 6))

colors = ['#e6f2e4', '#fbf4d9', '#e7f0fe', '#ffe8d9', '#fbe0e3']
line   = ['#61a745', '#e3ca60', '#6e99e5', '#f9a57d', '#ed8793']

conn = MongoClient("mongodb://127.0.0.1:27017")  
db = conn["open5gsNice"]
col = db["ts"]

pipeline = [
    { "$match": { "metadata.type": "latency", "metadata.job": "open5gs-ue01" }},
    { "$sort": { "metadata.experiment": 1, "timestamp": 1}},
    { "$project": {
        "_id": 0,
        "timestamp": 1,
        "job": "$metadata.job",
        "experiment": "$metadata.experiment",
        "value": 1,
    }}
]

cursor = col.aggregate(pipeline)
df = pd.DataFrame(list(cursor))

print(df.describe())

sns.set_theme(style="ticks", palette="pastel")
sns.set_style("whitegrid")
sns.despine(offset=10, trim=True)


ax = sns.boxplot( x = "job", y ="value", data = df, linewidth=.75,  hue="experiment", palette=colors, gap=.1)

#ax = sns.stripplot(x = "job", y ="value", hue="experiment",  data = df, palette=line, size=2)  
#ax = sns.swarmplot(data = df, y ="value", x="job")

plt.title("Latência", loc="center", fontsize=18)
plt.xlabel("Slices")
plt.ylabel("Latência (segundos)")

# Salvando o gráfico em um arquivo PNG
plt.savefig('boxblot_latency.png')

# Fechando a figura para liberar memória
plt.close()

