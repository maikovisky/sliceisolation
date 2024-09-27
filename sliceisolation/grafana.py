
from datetime import datetime, timezone
import json, requests, time, os
import shutil
#import logging

FORMAT = '%(asctime)s %(clientip)-15s %(user)-8s %(message)s'
#logging.getLogger(__name__)
#logging.basicConfig(level=logging.NOTSET)


class Grafana:
    def __init__(self, config):
        self.__config = config
        __grafana = config.get("dashboard", {"uid": "", "panels": [], "tags": []})
        __rendering = config.get("rendering", {"width": "2000", "height": "600", "tz": "America/Sao_Paulo", 
                                 "theme": "light", "interval": "2m","irate": "2m","resolution": "30s"})
        
        self.__uid    = __grafana.get("uid") #config["dashboard"]["uid"]
        self.__panels = __grafana.get("panels", []) #config["dashboard"]["panel"]
        self.__tags   = __grafana.get("tags", []) #config["dashboard"]["tags"]
        self.__url    = config.get("url")
        self.__width  = __rendering.get("width", "2000")
        self.__height = __rendering.get("height", "600")
        self.__tz     = __rendering.get("tz", "America/Sao_Paulo")
        self.__theme  = __rendering.get("theme", "light")
        self.__irate  = __rendering.get("irate", "2m")
        self.__interval    = __rendering.get("interval", "2m")
        self.__resolution  = __rendering.get("resolution", "30s")
        self.__namespace   = __rendering.get("namespace", "open5gs")
        self.__datasource  = __rendering.get("datasource", "prometheus")
        self.times    = []
        
    def addAnnotation(self, text):
        t = datetime.now(timezone.utc)
        
        timeStart = int( t.timestamp() * 1000)
        self.times.append(timeStart)
        
        header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body = { "dashboardUID": self.__uid, "time": timeStart, "text": text, "tags": self.__tags  }

        r = requests.post(self.__url + "/api/annotations", headers=header, data= json.dumps(body))
        #if(r.status_code >= 300):
            #logging.error("{} Can't add anotation. {}".format(r.status_code, r.text))
            
        return timeStart
    
    
    def getBaseUrl(self):
        base = []
        base.append("var-datasource={}&var-namespace={}&theme={}&tz={}".format(self.__datasource, self.__namespace, self.__theme, self.__tz) )
        base.append("var-resolution=30s&var-intervalo=2m&var-irate=2m&var-interval=2m".format(self.__resolution, self.__interval, self.__irate, self.__interval))
        base.append("width={}&height={}".format(self.__width, self.__height))

        baseUrl = '&'.join(base)
        url = "{}/render/d-solo/{}/open-5g?{}".format(self.__url, self.__uid, baseUrl)
        return url
    
    def downloadImage(self, text, name, path):
        
        url = self.getBaseUrl()
        
        baseUrl = finalUrl = "{}&from={}&to={}&var-experience={}".format(url, timeFrom, timeTo, name)
        for p in self.__panels:
            print(p)
            
            filename = "{}\\{}-{}.png".format(path, name, p["name"])
            print("Create: {}".format(filename))
            response = requests.get(finalUrl, stream=True)
            with open(filename, 'wb') as file:
                shutil.copyfileobj(response.raw, file)
