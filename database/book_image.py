from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
import database

db = database.db

class BookImage(db.Model):
    __tablename__ = "BookImage"

    iid = db.Column(mysql.INTEGER, primary_key=True)
    bid = db.Column(mysql.INTEGER, nullable=False)
    uri = db.Column(mysql.VARCHAR(100), nullable=False)
    rank = db.Column(mysql.INTEGER, nullable=False)

    def __init__(self, bid, uri, rank):
        self.bid = bid
        self.uri = uri
        self.rank = rank