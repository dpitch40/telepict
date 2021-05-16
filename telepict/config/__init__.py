import os

from .dev import ConfigDev, LoggingConfigDev
from .prod import ConfigProd, LoggingConfigProd
from .test import ConfigTest, LoggingConfigTest

env = os.environ.get('TELEPICT_ENV', 'dev')

Config = globals().get(f'Config{env.capitalize()}', None)
LoggingConfig = globals().get(f'LoggingConfig{env.capitalize()}', None)
