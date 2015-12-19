# -*- coding: utf-8 -*-
import sys
import json
import os

if len(sys.argv) < 2:
    print("Usage: python3 server.py <master server home directory>")
    sys.exit(1)

home = sys.argv[1]
os.makedirs(home + '/statsdbbackups', exist_ok=True)

try:
    config = json.loads(open(home + '/statsserver.json').read())
except FileNotFoundError:
    config = {}
defaultconfig = json.loads(open('defaultconfig.json').read())


def get(key):
    if key in config:
        return config[key]
    return defaultconfig[key]