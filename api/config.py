import os
import sys
import logging
from dotenv import load_dotenv

sys.path.append('.')
sys.path.append('..')


load_dotenv()

# disable JWT subject verification (avoid Error: Subject must be a string)
JWT_VERIFY_SUB = False
JSON_SORT_KEYS = False
JWT_SECRET_KEY = os.getenv('JWT_KEY')


IES_NAME = os.getenv('CLI_IES_NAME')
BASE_PATH = ('/' + IES_NAME) if IES_NAME else '/'
BASE_PATH = '/'


# DB config
_user = os.getenv('MYSQL_USER')
_password = os.getenv('MYSQL_PASSWORD')
_db = os.getenv('MYSQL_DATABASE')
_host = os.getenv('MYSQL_SERVER')
_port = os.getenv('MYSQL_SERVER_PORT')

SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{_user}:{_password}@{_host}:{_port}/{_db}'
SQLALCHEMY_TRACK_MODIFICATIONS = False


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
##### END LOGGING CONFIG #####
