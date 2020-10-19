from sqlalchemy.sql import func
import bcrypt
import database

db = database.db

class User(db.Model):
    __tablename__ = "User"

    uid = db.Column(db.Integer(), primary_key=True, nullable=False)
    id = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    nickname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer(), nullable=False)
    profile_img_url = db.Column(db.String(100))
    profile_text = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now())

    def __init__(self, id, password, nickname, email, age, profile_img_url="", profile_text=""):
        self.id = id
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.nickname = nickname
        self.email = email
        self.age = age
        self.profile_img_url = profile_img_url
        self.profile_text = profile_text


