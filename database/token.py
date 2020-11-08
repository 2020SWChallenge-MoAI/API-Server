from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
import database

db = database.db

class Token(db.Model):
    __tablename__ = "Token"

    tid = db.Column(mysql.INTEGER, primary_key=True)
    refresh_token = db.Column(mysql.VARCHAR(300))
    access_token = db.Column(mysql.VARCHAR(300))
    created_at = db.Column(mysql.DATETIME, default=func.now())

    def __init__(self, refresh_token, access_token):
        self.refresh_token = refresh_token
        self.access_token = access_token