

def saveToMongo(df, col, workload, interface=None):
    df2 = df[["ts", "exp", "cicle", workload]].rename(columns={workload: 'value'})
    df2["workload"] = workload
    if interface is not None:
        df2["interface"] = interface
    getDatabase("metrics")[col].insert_many(df2.to_dict("records"))