import os

from .dev import ConfigDev
from .prod import ConfigProd
from .test import ConfigTest

env = os.environ.get('TELEPICT_ENV', 'dev')

Config = globals().get(f'Config{env.capitalize()}', None)
Config.TELEPICT_ENV = env
