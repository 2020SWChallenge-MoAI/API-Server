from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
import database


db = database.db

class Work(db.Model):
    __tablename__ = "Work"

    wid = db.Column(mysql.INTEGER, primary_key=True, nullable=False)
    uid = db.Column(mysql.INTEGER, nullable=False)
    bid = db.Column(mysql.INTEGER, nullable=False)
    type = db.Column(mysql.TINYINT, nullable=False)
    created_at = db.Column(mysql.DATETIME, nullable=False, default=func.now())
    updated_at = db.Column(mysql.DATETIME, nullable=False, default=func.now())
    content = db.Column(mysql.LONGTEXT, nullable=False)

    def __init__(self, uid, bid, type, created_at, updated_at, content):
        self.uid = uid
        self.bid = bid
        self.type = type
        self.created_at = created_at
        self.updated_at = updated_at
        self.content = content

