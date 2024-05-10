import yaml
#from json_utils import get_attribute

class settings:
    def __init__(self, configFile):
        with open(configFile, 'r') as fConfig:
            config = yaml.safe_load(fConfig)
            
        self.__setMonitoring(config)
        self.open5gs     = config.get("open5gs")
        self.experiments = settingsExperiments(config.get("experiments", {}))
        self.running     = settingsRunning(config.get("running"))
        self.database    = config.get("database", {"mongodb": "mongo://localhost:27017"})
    
    def __setMonitoring(self, config):
        self.__monitoring = config.get("monitoring")
        self.__prometheus = config.get("prometheus")
        self.__grafana    = config.get("grafana")
    
    #
    # Database configs function
    #
    def getDatabaseMongo(self):
        return self.database.get("mongodb", "mongo://localhost:27017")
    
    #
    # Monitoring configs function
    #
    def getPrometheus(self):
        return self.__prometheus
    
    def getGrafana(self):
        return self.__grafana
    
    def getGrafanaUrl(self):
        return self.__grafana.get("url", "")
    
    def getGrafanaDashboard(self):
        return self.__grafana["uid"], self.__grafana["panel"]
    
    #
    # Open5gs configs function
    #
    def getNamespace(self):
        return self.running.getNamespace()
    
    def getOpen5gsCore(self):
        return self.open5gs.getCore()
    
    def getOpen5gsUPFS(self):
        return self.open5gs.getUPFS()
    
    def getOpen5gsUERAMSIMS(self):
        return self.open5gs.getUERAMSIMS()
    
    #
    # Experiments config functions
    #
    def getExperiments(self):
        return self.experiments.getExperiments()
    
    
    #
    # Running config functions
    #
    def getRunning(self):
        return self.running
    
    
class settingsOpen5gs:
    def __init__(self, config):
        self.__config = config
        self.__pods = config.get("pods", {"core": [], "upfs": [], "uransims": []})
        self._core  = self.__pods.get("core", {})
        self._upfs  = self.__pods.get("upfs", {})
        self._uransims  = self.__pods.get("uransims", {})
        
    def getCore(self):
        return self.__core
    
    def getUPFS(self):
        return self.__upfs
    
    def getURANSIMS(self):
        return self.__uransims

class settingsExperiments:
    def __init__(self, config):
        self.__config = config 
        
    def getExperiments(self):
        return self.__config

class settingsRunning:
    def __init__(self, config):
        self.__config = config   
        self.__namespace = config.get("namespace", "open5gs")
        self.__repetition= config.get("repetition", 1)
        
        time = config.get("time", {"on_cicle": 300, "start_waiting": 60})
        self.__on_cicle = time.get("on_cicle", 300)
        self.__start_waiting = time.get("start_waiting", 60)
        
        resource = config.get("resource", {"cpu": 0, "mem": 0})
        self.__cpu = resource.get("cpu", 0)
        self.__mem = resource.get("mem", 0)
        
    def getNamespace(self):
        return self.__namespace
    
    def getRepetition(self):
        return self.__repetition
    
    def getTimeOnCicle(self):
        return self.__on_cicle
    
    def getTimeStartWaiting(self):
        return self.__start_waiting
    
    def getCPU(self):
        return self.__cpu
    
    def getMem(self):
        return self.__mem
    
    