from os.path import abspath, dirname, join
from flask import request, Response
from keyext import KeywordExtractor, preprocess

from api import app

base_dir = app.config['BASE_DIR']
model_dir = app.config['MODEL_DIR']
book_dir = app.config['BOOK_DIR']

extractor = KeywordExtractor()

@app.before_first_request
def load():
    extractor.load(join(model_dir,'extractor.pkl'))
    print('Extractor Loaded')


@app.route('/keywords/<bid>', methods=['GET'])
def extract(bid):
    with open(join(book_dir,f'{bid}.txt')) as f:
        books = "".join(f.readlines())

    keywords = extractor.recommend_from_sentences(preprocess(books), num=5)
    print(keywords)
    return {"keywords": keywords}, 200