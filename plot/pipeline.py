


def latencyBoxPlot(experiment="01"):
    return [
        { "$match": { "metadata.type": "latency", "metadata.experiment": experiment }},
        { "$sort": { "metadata.job": 1, "timestamp": 1}},
        { "$project": {
            "_id": 0,
            "timestamp": 1,
            "job": "$metadata.job",
            "experiment": "$metadata.experiment",
            "value": 1,
            }
        }]
    
def latencyStdAllSlices():
    return [
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
    
def latencyStdSlice(slice):
    job = "open5gs-ue{}".format(slice)
    return [
        { "$match": { "metadata.type": "latency", "metadata.job": job}},
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