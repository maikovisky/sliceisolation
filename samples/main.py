from sliceisolation.sisolation import sisolation 


si = sisolation("config.yaml")

si.prerunning()

si.run()

si.posrunning()