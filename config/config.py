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

# JWT
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXP_TIME = 600  # 10 min
JWT_REFRESH_TOKEN_EXP_TIME = 1209600  # 2 week

# Directory
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")
ASSET_DIR = os.path.join(BASE_DIR, "assets")
BOOK_DIR = os.path.join(ASSET_DIR, "books")
BOOK_TEXT_DIR = os.path.join(os.path.dirname(BASE_DIR), 'book/woongjin/raw') # TODO: BOOK_DIR 제거하고 DB에 넣기

# File
KEYWORD_DATA_FILE_NAME = "keyword-extractor-current"

# API Config
SELECTED_BOOK_BIDS = [8, 10, 21, 22, 31, 38, 40, 41, 55, 90]
DEFAULT_KEYWORD_NUM = 10
DEFAULT_MAIN_SENTENCE_NUM = 10
QNA_QUESTION_VALID_SCORE_THRESHOLD = 0.85  # qna question의 score가 몇 점 이상일 때 valid하다고 볼 것인가?
QNA_ANSWER_VALID_SCORE_THRESHOLD = 0.5  # 주관식 qna answer의 score가 몇 점 이상일 때 valid하다고 볼 것인가?