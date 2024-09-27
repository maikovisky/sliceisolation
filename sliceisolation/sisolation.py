from .settings import settings
import logging, sys

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# handlerStdout = logging.StreamHandler(sys.stdout)
# handlerStdout.setLevel(logging.DEBUG)
# logger.addHandler(handlerStdout)

class sisolation:
    __repeating    = 1
    __timeOnCicle  = 300 
    __timeStartWaiting = 60
    __experiments  = [1, 2]
    __cicle        = [1, 5, 10, 15]
    
    def __init__(self, configfile):
        self.config = settings(configfile)
        self.__experiments = self.config.getExperiments()
        self.__namespace   = self.config.getNamespace()
        running = self.config.getRunning()
        self.__timeOnCicle = running.getTimeOnCicle()
        self.__timeStartWaiting = running.getTimeStartWaiting()
        
    def prerunning(self):
        """Prepare system to running"""
        print("PRE Running")
        
    def __preparingexperiment(self, experiment):
        print("Preparing experiment {}".format(experiment))
        
    def __runcicle(self, experiment, cicle):
        
        # Add PODS
        
        print("Waiting {} seconds".format(self.__timeOnCicle))
        
    def __runexperiment(self, experiment):
        self.__preparingexperiment(experiment["id"])
        print("Run experiment {}".format(experiment["id"]))
        print(experiment["description"])
        print("".ljust(len(experiment["description"]), '-'))
        
        n = 0
        for c in self.__cicle:
            n +=1
            print("Start cicle {}/{} of experiment {}".format(n , len(self.__cicle), experiment["id"]))
            self.__runcicle(experiment, c)
        
        print("End experiment {}\n".format(experiment["id"]))
        
    def run(self):
        """Running experiments"""
        print("Running") 
        for i in range(0, self.__repeating):  
            print("Waiting {} seconds".format(self.__timeStartWaiting))
            print("Repeat {}/{}".format(i + 1, self.__repeating))
            n = 0
            for  e in self.__experiments:
                n += 1
                print("".ljust(len(e["description"]), '='))
                print("Experiment {}/{}".format(n, len(self.__experiments)))
                self.__runexperiment(e)
                
    def posrunning(self):
        """Finish experiments"""
        print("POS Running")
        
        
    def autorunning(self):
        """Running"""
        self.prerunning()
        self.run()
        self.posrunning()
        
    def getGrafana(self):
        return self.config.getGrafana()
