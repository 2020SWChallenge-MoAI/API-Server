from datetime import datetime
from functions import deleteWorkThumbnail, isValidBid, saveWorkThumbnail
import os
import base64
from flask import Blueprint, request, abort, g
from sqlalchemy import desc, sql

from functions import *

from .decorators import signin_required

from database import db
from database.user import User
from database.work import Work
from database.book import Book
from database.user_book import User_Book

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
        user_row = user_qresult[0]

        user_book_qresult = User_Book.query.filter_by(uid=uid).order_by(desc(User_Book.read_at)).all()
        read_book_bids = []
        appeared_bids = []
        for user_book_row in user_book_qresult:
            if user_book_row.bid not in appeared_bids:
                read_book_bids.append({
                    "bid": user_book_row.bid,
                    "read_at": user_book_row.read_at
                })
                appeared_bids.append(user_book_row.bid)
        
        work_qresult = Work.query.filter_by(uid=uid).order_by(desc(Work.updated_at)).all()
        wids = []
        for work_row in work_qresult:
            wids.append(work_row.wid)

        return {
            "nickname": user_row.nickname,
            "email": user_row.email,
            "age": user_row.age,
            "profile_img_url": user_row.profile_img_url,
            "profile_text": user_row.profile_text,
            "created_at": user_row.created_at,
            "updated_at": user_row.updated_at,
            "read_book_bids": read_book_bids,
            "wids": wids
        }, 200


@user.route("/book", methods=["GET"])
@signin_required
def getUserReadBook():
    uid = g.uid

    params = request.args.to_dict()
    
    num = -1
    if "num" in params.keys():
        try:
            num = int(params["num"])
        except ValueError:
            num = -1
        
        if num <= 0:
            num = -1

    qresult = User_Book.query.filter_by(uid=uid).order_by(desc(User_Book.read_at)).all()
    read_book_bids = []
    appeared_bids = []
    for row in qresult:
        if row.bid not in appeared_bids:
            read_book_bids.append({
                "bid": row.bid,
                "read_at": row.read_at
            })
            appeared_bids.append(row.bid)
        
        if num != -1 and len(read_book_bids) == num:
            break
    
    if num != -1:
        read_book_bids = read_book_bids[:num]

    return {
        "read_book_bids": read_book_bids
    }, 200


@user.route("/work", methods=["GET"])
@signin_required
def getAllUserWork():
    uid = g.uid
    
    qresult = Work.query.filter_by(uid=uid).order_by(desc(Work.updated_at)).all()

    wids = []
    for row in qresult:
        wids.append(row.wid)
    
    return {
        "wids": wids
    }, 200


@user.route("/work/<int:wid>", methods=["GET"])
@signin_required
def getUserWork(wid):
    uid = g.uid
    
    qresult = Work.query.filter_by(wid=wid, uid=uid).all()
    if len(qresult) == 0:
        abort(400)
    
    row = qresult[0]
    wid = row.wid
    bid = row.bid
    type = row.type
    created_at = row.created_at
    updated_at = row.updated_at
    content = row.content

    thumbnail_path = os.path.join(config.WORK_DIR, str(uid), getWorkName(bid, updated_at, type))
    thumbnail = convertFileToBase64(thumbnail_path)
    
    return {
        "wid": wid,
        "bid": bid,
        "type": type,
        "created_at": created_at,
        "updated_at": updated_at,
        "thumbnail": thumbnail,
        "content": content
    }, 200


@user.route("/work/save", methods=["POST"])
@signin_required
def saveUserWork():
    uid = g.uid

    params = request.get_json()
    now = datetime.now()

    if "wid" in params.keys(): # update
        try:
            wid = int(params["wid"])
        except:
            abort(400)

        if "thumbnail" not in params.keys():
            abort(400)
        else:
            thumbnail = params["thumbnail"]

        if "content" not in params.keys():
            abort(400)
        else:
            content = params["content"]

        qresult = Work.query.filter_by(wid=wid).all()

        if len(qresult) == 0:
            abort(400)

        target = qresult[0]

        try:
            saveWorkThumbnail(uid=target.uid, bid=target.bid, type=target.type, updated_at=now, thumbnail=thumbnail)
        except:
            deleteWorkThumbnail(uid=target.uid, bid=target.bid, type=target.type, updated_at=now)  # delete currently saved file if exists
            abort(400)

        deleteWorkThumbnail(uid=target.uid, bid=target.bid, type=target.type, updated_at=target.updated_at)  # delete previously saved file if exists

        target.content = content
        target.updated_at = now
        db.session.commit()

        return {}, 200
    else: # create
        if "bid" not in params.keys():
            abort(400)
        else:
            try:
                bid = int(params["bid"])
            except:
                abort(400)

            if not isValidBid(bid):
                abort(400)

        if "type" not in params.keys():
            abort(400)
        else:
            try:
                type = int(params["type"])
            except:
                abort(400)

            if type not in [0, 1, 2, 3]:
                abort(400)
        
        if "thumbnail" not in params.keys():
            abort(400)
        else:
            thumbnail = params["thumbnail"]
        
        if "content" not in params.keys():
            abort(400)
        else:
            content = params["content"]

            if len(content) == 0:
                abort(400)

        try:
            saveWorkThumbnail(uid=uid, bid=bid, type=type, updated_at=now, thumbnail=thumbnail)
        except:
            deleteWorkThumbnail(uid=uid, bid=bid, type=type, updated_at=now)  # delete currently saved file if exists
            abort(400)

        try:
            db.session.add(Work(uid=uid, bid=bid, type=type, created_at=now, updated_at=now, content=content))
            db.session.commit()
            return {}, 200
        except:
            abort(400)

