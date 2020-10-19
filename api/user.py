from datetime import datetime
from flask import Blueprint, request, abort, g
from sqlalchemy import desc

from database import db
from database.user import User
from database.user_book import User_Book
from api.auth import signin_required
from config import config

user = Blueprint(name="user", import_name=__name__)

@user.route("", methods=["GET"])
@signin_required
def getUserInfo():
    uid = g.uid

    user_qresult = User.query.filter_by(uid=uid).all()

    if len(user_qresult) == 0:
        abort(400)
    else:
        row = user_qresult[0]

        user_book_qresult = User_Book.query.filter_by(uid=uid).order_by(desc(User_Book.read_at)).all()
        read_book_bids = []
        appeared_bids = []
        for item in user_book_qresult:
            if item.bid not in appeared_bids:
                read_book_bids.append({
                    "bid": item.bid,
                    "read_at": item.read_at
                })
                appeared_bids.append(item.bid)

        return {
            "nickname": row.nickname,
            "email": row.email,
            "age": row.age,
            "profile_img_url": row.profile_img_url,
            "profile_text": row.profile_text,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
            "read_book_bids": read_book_bids
        }, 200
