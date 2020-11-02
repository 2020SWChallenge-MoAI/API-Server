from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
import database

db = database.db

class BookSentence(db.Model):
    __tablename__ = "BookSentence"

    sid = db.Column(mysql.INTEGER, primary_key=True)
    bid = db.Column(mysql.INTEGER, nullable=False)
    page = db.Column(mysql.INTEGER, nullable=False)
    sentence = db.Column(mysql.VARCHAR(200), nullable=False)
    rank = db.Column(mysql.INTEGER, nullable=False)
    iid = db.Column(mysql.INTEGER)

    def __init__(self, bid, page, sentence, rank, iid=None):
        self.bid = bid
        self.page = page
        self.sentence = sentence
        self.rank = rank
        self.iid = iid