import os

from .dev import ConfigDev
from .prod import ConfigProd
from .test import ConfigTest

env = os.environ['TP_ENV']

Config = globals().get(f'Config{env.capitalize()}', None)
