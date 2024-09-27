import confuse
import logging, ecs_logging

template = {
    "monitoring": {
        "prometheus": str,
        "grafana": {
            "url": str,
            "rendering": {
                "width": 2000,
                "height": 660,
                "tz": "America/Sao_Paulo",
                "theme": "light",
                "interval": "2m",
                "irate": "2m",
                "resolution": "30s",
                "namespace": "open5gs"
            },
            "dashboard": {
                "uid": str,
                "panels": confuse.Sequence({
                    "name": str,
                    "panelId": int
                })
            }
        }
    },
    "pathbase": str,
    "database": {
        "mongo": str
    },
    "open5gs": {
        "pods": {
            "core": list,
        },
        "slices": confuse.Sequence({
            "id": int,
            "upf": str
        })
    },
    "experiments": confuse.Sequence({
        "name": str,
        "id": int,
        "description": str,
        "slices": confuse.Sequence({
            "slice": int,
            "pod": str,
            "cicle": confuse.Optional(subtemplate=list, default=None)
        })
    })
    
}


FORMAT='[%(levelname)s] %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'
#format = logging.Formatter(fmt=FORMAT)
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('simulateslices.json')
handler.setFormatter(ecs_logging.StdlibFormatter())
logger.addHandler(handler)

def appConfig(filename):
    config = confuse.Configuration('sliceBenchmarch', __name__)
    config.set_file(filename)
    config.set_env(prefix='')

    return config.get(template)


