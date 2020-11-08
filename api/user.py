from datetime import datetime
from functions import isValidBid
from flask import Blueprint, request, abort, g
from sqlalchemy import desc, sql
import json

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

        read_book_bids = getUserReadBookBids(uid)
        wids, monthly_grade = getUserWorkWids(uid)

        return {
            "nickname": user_row.nickname,
            "email": user_row.email,
            "age": user_row.age,
            "profile_img_url": user_row.profile_img_url,
            "profile_text": user_row.profile_text,
            "created_at": user_row.created_at.isoformat(),
            "updated_at": user_row.updated_at.isoformat(),
            "read_book_bids": read_book_bids,
            "wids": wids,
            "monthly_grade": monthly_grade
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

    return {
        "read_book_bids": getUserReadBookBids(uid, num)
    }, 200


@user.route("/work", methods=["GET"])
@signin_required
def getAllUserWork():
    uid = g.uid
    
    return {
        "wids": getUserWorkWids(uid)[0]
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
    
    return {
        "wid": wid,
        "bid": bid,
        "type": type,
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat(),
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

        if "content" not in params.keys():
            abort(400)
        else:
            content = params["content"]

        qresult = Work.query.filter_by(wid=wid).all()
        if len(qresult) == 0:
            abort(400)
        
        try:
            qresult[0].content = content
            qresult[0].updated_at = now

            if type == 0:
                max_depth, avg_child_num, morethan2child_node_num, max_depth_diff, template_node_balance, user_created_node_num, ai_support_num, duplicate_node = gradeMindmap(json.loads(content))

                qresult[0].max_depth = max_depth
                qresult[0].avg_child_num = avg_child_num
                qresult[0].morethan2child_node_num = morethan2child_node_num
                qresult[0].max_depth_diff = max_depth_diff
                qresult[0].template_node_balance = template_node_balance
                qresult[0].user_created_node_num = user_created_node_num
                qresult[0].ai_support_num = ai_support_num
                qresult[0].duplicate_node = duplicate_node

            db.session.commit()

            return {}, 200
        except:
            abort(400)
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
        
        if "content" not in params.keys():
            abort(400)
        else:
            content = params["content"]

            if len(content) == 0:
                abort(400)
        
        try:
            if type == 0:
                max_depth, avg_child_num, morethan2child_node_num, max_depth_diff, template_node_balance, user_created_node_num, ai_support_num, duplicate_node = gradeMindmap(json.loads(content))
                work = Work(uid=uid, bid=bid, type=type, created_at=now, updated_at=now, content=content, max_depth=max_depth, avg_child_num=avg_child_num, morethan2child_node_num=morethan2child_node_num, max_depth_diff=max_depth_diff, template_node_balance=template_node_balance, user_created_node_num=user_created_node_num, ai_support_num=ai_support_num, duplicate_node=duplicate_node)
            else:
                work = Work(uid=uid, bid=bid, type=type, created_at=now, updated_at=now, content=content)
            
            db.session.add(work)
            db.session.commit()
            return {}, 200
        except:
            abort(400)

