# coding: utf-8

"""
Lingobarter will try to read configurations from environment variables
so you dont need this local_settings.py file if you have env vars.

1. You can set as a file

export LINGOBARTER_SETTINGS='/path/to/settings.py'

2. You can set individual values

export LINGOBARTER_MONGODB_DB="lingobarter_db"
export LINGOBARTER_MONGODB_HOST='localhost'
export LINGOBARTER_MONGODB_PORT='$int 27017'

Or just fill your values in this file and rename it to 'local_settings.py'
We recommend you to use local_settings.py to locally configure your lingobarter,
local_settings.py has been already added to .gitignore list.
"""

# MONGO
MONGODB_DB = "lingobarter_db"
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_USERNAME = None
MONGODB_PASSWORD = None

# Debug and toolbar
DEBUG = True
DEBUG_TOOLBAR_ENABLED = False

# Logger
LOGGER_ENABLED = True
LOGGER_LEVEL = 'DEBUG'
LOGGER_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
LOGGER_DATE_FORMAT = '%d.%m %H:%M:%S'
