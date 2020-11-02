from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
import database

db = database.db

class User_Book(db.Model):
    __tablename__ = "User_Book"

    id = db.Column(mysql.INTEGER, primary_key=True)
    uid = db.Column(mysql.INTEGER, nullable=False)
    bid = db.Column(mysql.INTEGER, nullable=False)
    read_at = db.Column(mysql.DATETIME, nullable=False, default=func.now())

    def __init__(self, uid, bid):
        self.uid = uid
        self.bid = bid


