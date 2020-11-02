from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
import database

db = database.db

class Book(db.Model):
    __tablename__ = "Book"

    bid = db.Column(mysql.INTEGER, primary_key=True)
    title = db.Column(mysql.VARCHAR(50), nullable=False)
    author = db.Column(mysql.VARCHAR(50))
    publisher = db.Column(mysql.VARCHAR(50))
    category = db.Column(mysql.VARCHAR(50))
    page_num = db.Column(mysql.INTEGER)
    image_num = db.Column(mysql.INTEGER)