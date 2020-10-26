from sqlalchemy.sql import func
import bcrypt
import database

db = database.db

class Book(db.Model):
    __tablename__ = "Book"

    bid = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50))
    publisher = db.Column(db.String(50))
    category = db.Column(db.String(50))
    page_num = db.Column(db.Integer())
    book_cover_url = db.Column(db.String(50))