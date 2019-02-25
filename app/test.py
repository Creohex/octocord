import os, json
from flask import Flask

import settings


print("test!")
print(settings.func())
print("environ: %s" % os.environ)
print("dir: %s" % os.listdir('/certs'))
