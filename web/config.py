import os
import sys
import locale
import logging
import datetime
from dotenv import load_dotenv
from redis import Redis

from web.utils.mixins import get_ies_config

# Config root path and language
try:
    locale.setlocale(locale.LC_ALL, 'es_MX.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C')  # Fallback to a default locale
sys.path.append('./')
load_dotenv()


REDIS_PATH = 'redis://pleyades-redis:6379'

##### LOGGING CONFIG #####
LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'
# GENERAL (ALL) LOGS
logging.basicConfig(
    filename=os.getcwd()+'/logs/GENERALS.log',
    level=logging.DEBUG,
    format=LOG_FORMAT
)
# APP ERROR LOGS
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
file_handler = logging.FileHandler(os.getcwd()+'/logs/ERRORS.log')
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
error_logger.addHandler(file_handler)
# MODEL ERROR LOGS
model_logger = logging.getLogger('model_logger')
model_logger.setLevel(logging.ERROR)
file_handler = logging.FileHandler(os.getcwd()+'/logs/MODEL.log')
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
model_logger.addHandler(file_handler)
##### END LOGGING CONFIG #####


##### SESSION CONFIG #####
SECRET_KEY = os.getenv('SESSION_KEY')
SESSION_TYPE = 'redis'
SESSION_REDIS = Redis.from_url(REDIS_PATH)
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=3)
SESSION_USE_SIGNER = True
SESSION_KEY_PREFIX = 'PLEY_'
#### END SESSION CONFIG #####


#### BABEL LANGS CONFIG ####
BABEL_DEFAULT_LOCALE = 'es'
BABEL_DEFAULT_TIMEZONE = 'UTC'
LANGUAGES = ['en', 'es']
#### END BABEL LANGS CONFIG ####


#### ASYNC TASKS CONFIG ####
CELERY = dict(
    broker_url=REDIS_PATH,
    result_backend=REDIS_PATH,
    task_ignore_result=True,
)
#### END ASYNC TASKS CONFIG ####

#### CUSTOM APP CONFIG ####
IES = get_ies_config()
IES_NAME = os.getenv('CLI_IES_NAME')
BASE_PATH = '/' + IES_NAME if IES_NAME else '/'
APPLICATION_ROOT = os.getenv('APPLICATION_ROOT', '/')
EXCEL_ENABLED = os.getenv('EXCEL', 'false').lower() in ('true', '1', 't')
#### END CUSTOM APP CONFIG ####
