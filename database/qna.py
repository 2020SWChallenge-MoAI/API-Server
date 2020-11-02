from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
import database

db = database.db

class QnA(db.Model):
    __tablename__ = "QnA"

    qid = db.Column(mysql.INTEGER, primary_key=True)
    uid = db.Column(mysql.INTEGER, nullable=False)
    bid = db.Column(mysql.INTEGER, nullable=False)
    question = db.Column(mysql.VARCHAR(200), nullable=False)
    type = db.Column(mysql.TINYINT, nullable=False)
    answer = db.Column(mysql.VARCHAR(200), nullable=False)
    created_at = db.Column(mysql.DATETIME, nullable=False, default=func.now())

    def __init__(self, uid, bid, question, type, answer):
        self.uid = uid
        self.bid = bid
        self.question = question
        self.type = type
        self.answer = answer