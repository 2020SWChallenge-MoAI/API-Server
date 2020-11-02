from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
import bcrypt
import database

db = database.db

class User(db.Model):
    __tablename__ = "User"

    uid = db.Column(mysql.INTEGER, primary_key=True, nullable=False)
    id = db.Column(mysql.VARCHAR(50), unique=True, nullable=False)
    password = db.Column(mysql.VARCHAR(60), nullable=False)
    nickname = db.Column(mysql.VARCHAR(100), nullable=False)
    email = db.Column(mysql.VARCHAR(100), nullable=False)
    age = db.Column(mysql.INTEGER, nullable=False)
    profile_img_url = db.Column(mysql.VARCHAR(100))
    profile_text = db.Column(mysql.VARCHAR(100))
    created_at = db.Column(mysql.DATETIME, nullable=False, default=func.now())
    updated_at = db.Column(mysql.DATETIME, nullable=False, default=func.now())

    def __init__(self, id, password, nickname, email, age, profile_img_url="", profile_text=""):
        self.id = id
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.nickname = nickname
        self.email = email
        self.age = age
        self.profile_img_url = profile_img_url
        self.profile_text = profile_text


