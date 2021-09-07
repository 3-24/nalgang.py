#!/usr/bin/env/python3
import os
import logging
from bot import client

if not __name__ == "__main__":
    exit()

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO, handlers=[logging.FileHandler('./data/log'), stream_handler])
logging.info('Starting nalgang...')

TOKEN = os.environ["nalgang_TOKEN"]
client.run(TOKEN)
