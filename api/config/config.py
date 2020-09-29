from os.path import dirname, abspath,join

DEBUG = True
BASE_DIR = dirname(dirname(dirname(__file__)))
MODEL_DIR = join(BASE_DIR,'model')
BOOK_DIR = join(dirname(BASE_DIR),'book','woongjin','raw')