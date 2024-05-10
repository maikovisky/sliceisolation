
from datetime import datetime, timezone


class Grafana:
    def __init__(self, config):
        self.__config = config
        grafana = config.get("dashboard", {"uid": "", "panel": "", "tags": ""})
        self.__uid    = config["dashboard"]["uid"]
        self.__panel  = config["dashboard"]["panel"]
        self.__tags   = config["dashboard"]["tags"]
        
    def addAnnotation(self, text):
        t = datetime.now(timezone.utc)
        
        timeStart = int( t.timestamp() * 1000)
        
        header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body = { "dashboardUID": self.__uid, "time": timeStart, "text": text, "tags": self.__tags  }

        r = requests.post(self.grafanaUrl + "/api/annotations", headers=header, data= json.dumps(body))
        
        return timeStart


def addAnnotation(self, text, startAt = False, endAt = False):
        t = datetime.now(timezone.utc)
        
        if(startAt):
            self.startAt = t
            #print(self.startAt.strftime("%Y-%m-%dT%H:%M:%S.000Z"))

        if(endAt):
            self.endAt = t
            
        timeStart = int( t.timestamp() * 1000)
                    
        header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body = { "dashboardUID": self.dashboardUID, "time": timeStart, "text": text, "tags": self.tags }

        r = requests.post(self.grafanaUrl + "/api/annotations", headers=header, data=json.dumps(body))
        print(text)
        return int( t.timestamp() )   