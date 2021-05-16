import os

from .dev import ConfigDev, LoggingConfigDev, LOG_LEVEL as LogLevelDev
from .prod import ConfigProd, LoggingConfigProd, LOG_LEVEL as LogLevelProd
from .test import ConfigTest, LoggingConfigTest, LOG_LEVEL as LogLevelTest

env = os.environ.get('TELEPICT_ENV', 'dev')

Config = globals().get(f'Config{env.capitalize()}', None)
LoggingConfig = globals().get(f'LoggingConfig{env.capitalize()}', None)
LOG_LEVEL = globals().get(f'LogLevel{env.capitalize()}', None)
