import os

DEBUG = True

# App
APP_NAME = "Ttokdok API Server"
APP_IP = "localhost"
APP_PORT = 7002

# Database
DB_TYPE = "mysql"
DB_DRIVER = "pymysql"
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "api_server"
DB_NAME = "api_server"
DB_CHARSET = "utf8"
#DB_POOL_SIZE = 20  # connection 최대 개수
#DB_POOL_RECYCLE = 500  # 응답 없을 시 connection 끊기까지 대기 시간(sec)
#DB_MAX_OVERFLOW = 20  # connection 모두 사용중일 때 대기 queue에 몇 개의 요청까지 남겨둘 건지

# JWT
JWT_ALGORITHM = "HS256"
JWT_EXP_TIME = 600

# Directory
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')
BOOK_DIR = os.path.join(os.path.dirname(BASE_DIR), 'book/woongjin/raw')

# File
KEYWORD_DATA_FILE_NAME = "keyword-extractor.pkl"

# API Config
DEFAULT_KEYWORD_NUM = 10
DEFAULT_MAIN_SENTENCE_NUM = 5
DEFAULT_MAIN_IMAGE_NUM = 4