import os
import importlib

env = os.environ.get('TELEPICT_ENV', 'dev')

config_module = importlib.import_module('.'.join(['telepict', 'config', env]))
Config = getattr(config_module, f'Config{env.capitalize()}')
Config.TELEPICT_ENV = env
