import os
from flask import Flask

app = Flask(__name__)

path = os.path.dirname(__file__)
path = os.path.join(path, 'config')
path = os.path.join(path, 'config.py')
if os.path.isfile(path):
    app.config.from_pyfile(path)
else:
    print('PLEASE PUT ONE AT api/config.py')
    exit(-1)
