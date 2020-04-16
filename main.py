#/usr/bin/env/python3
import os, sys, time
from bot import client

if not __name__=="__main__":
    exit()

TOKEN = os.environ["nalgang_TOKEN"]
client.run(TOKEN)
