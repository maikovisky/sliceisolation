# Slice Isolation 


This project is part of master degree

## Install


```bash
pip install -r requirements.txt
```


## Config

Monitoring and Stats

```yaml
monitoring:
  prometheus: http://prometheus
  grafana: 
    url: http://grafana
    dashboard:
      uid: 
      panel: 
```

Database connection

```yaml
database:
  mongo: mongodb://localhost:27017/open5gs
```

Open5GS pods for Kubernets

```yaml
open5gs:
  pods:
    core: ["open5gs-nrf", "open5gs-scp", "open5gs-amf", "open5gs-ausf","open5gs-bsf", "open5gs-nssf", "open5gs-pcf","open5gs-udm","open5gs-udr"]
    upfs: ["open5gs-upf-1", "open5gs-upf-2", "open5gs-upf-3", "open5gs-upf-4", "open5gs-upf-5"]
    uransims: ["open5gs-ueransim01", "open5gs-ueransim02", "open5gs-ueransim03", "open5gs-ueransim04", "open5gs-ueransim05"]
```

Running

```yaml
running:
  namespace: open5gs
  experiments: [1]
  repetition: 1
  cicle: [1, 5, 10, 15, 20, 25]
  time:
    on_cicle: 300
    start_waiting: 30
  
  # Default values
  resources:
    cpu: 0
    mem: 0
```

Experiments

```yaml
experiments:
  - name: experiment01
    id: 1
    description: Baseline only Slice 01 UE
    slices: 
      - slice: 1
        pod: "open5gs-ue01"
        cicle: [4, 4, 4, 4, 4, 4]

  - name: experiment02
    id: 2
    description: Baseline with Slices 01 and 02
    slices: 
      - slice: 1
        pod: "open5gs-ue01"
        cicle: [4, 4, 4, 4, 4, 4]
      - slice: 2
        pod: "open5gs-ue02"
```