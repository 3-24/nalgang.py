#!/usr/bin/env/python3
import os
import sys
import logging
from bot import client

# change working dir as script dir to get fixed relative access to data
os.chdir(sys.path[0])
if not os.path.exists("data"):
    os.makedirs("data")

if not __name__ == "__main__":
    exit()

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO, handlers=[logging.FileHandler('./data/log'), stream_handler])
logging.info('Starting nalgang...')

TOKEN = os.environ["nalgang_TOKEN"]
client.run(TOKEN)
