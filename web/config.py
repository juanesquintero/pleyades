import os
import sys
import locale
import logging
from dotenv import load_dotenv

from utils.mixins import obtener_ies_config

# Config root path and language
locale.setlocale(locale.LC_ALL, 'es_MX.UTF-8')
sys.path.append('./')
load_dotenv()


'''LOGGING CONFIGURATION'''
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

'''END LOGGING CONFIGURATION'''


SECRET_KEY = os.getenv('SESSION_KEY')


# IES config
IES = obtener_ies_config()
IES_NAME = os.getenv('CLI_IES_NAME')
BASE_PATH = '/'  # base_path = ('/' + ies_name) if ies_name else '/'
EXCEL_ENABLED = os.getenv('EXCEL', 'false').lower() in ('true', '1', 't')


BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'UTC'
LANGUAGES = ['en', 'es']  # Example languages
