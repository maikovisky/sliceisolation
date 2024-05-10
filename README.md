# Slice Isolation 


This project is part of master degree

## Install


```bash
pip install -r requirements.txt
```


## Config

```yaml
monitoring:
  prometheus: http://prometheus
  grafana: 
    url: http://grafana
    dashboard:
      uid: 
      panel: 
```

```yaml
database:
  mongo: mongodb://localhost:27017/open5gs
```

### Open 5GS 


```yaml
open5gs:
  pods:
    core: ["open5gs-nrf", "open5gs-scp", "open5gs-amf", "open5gs-ausf","open5gs-bsf", "open5gs-nssf", "open5gs-pcf","open5gs-udm","open5gs-udr"]
    upfs: ["open5gs-upf-1", "open5gs-upf-2", "open5gs-upf-3", "open5gs-upf-4", "open5gs-upf-5"]
    uransims: ["open5gs-ueransim01", "open5gs-ueransim02", "open5gs-ueransim03", "open5gs-ueransim04", "open5gs-ueransim05"]
```