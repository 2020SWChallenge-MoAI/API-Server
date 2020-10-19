from sqlalchemy.sql import func
import database

db = database.db

class User_Book(db.Model):
    __tablename__ = "User_Book"

    id = db.Column(db.Integer(), primary_key=True)
    uid = db.Column(db.Integer(), nullable=False)
    bid = db.Column(db.Integer(), nullable=False)
    read_at = db.Column(db.DateTime, nullable=False, default=func.now())

    def __init__(self, uid, bid):
        self.uid = uid
        self.bid = bid


