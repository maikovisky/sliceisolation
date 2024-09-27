import os, sys
import argparse
sys.path.insert(1, "\\".join(os.path.realpath(__file__).split("\\")[0:-2]))
from sliceisolation.config import * 
# from sliceisolation.grafana import *


parser = argparse.ArgumentParser(prog='Rocketroom', description='Capture log from Rocketchat Rooms and save in Elasticsearch.')
parser.add_argument('-c','--config', help='Load config file', default="config.yaml")
parser.add_argument('-d','--days', help='Number of previous days to capture. (default: %(default)s)', default=1, type=int)
parser.add_argument('--start', help='Capture start day.', default=None)
parser.add_argument('--end', help='End of capture day.', default=None)
parser.add_argument('-n', '--now', action='store_true', default=False)

def __main__():
    logger.info("Start Simulate Slices") 
    args = parser.parse_args()
    config = appConfig(args.config)
    logger.debug(config)



__main__()