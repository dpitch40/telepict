import os

from config.dev import ConfigDev
from config.prod import ConfigProd
from config.test import ConfigTest

env = os.environ['TP_ENV']

Config = globals().get(f'Config{env.capitalize()}', None)
