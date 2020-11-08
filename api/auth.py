from flask import Blueprint, request, abort, g
from datetime import datetime, timedelta
import bcrypt
import jwt

from database import db
from database.user import User
from database.token import Token
from sqlalchemy import desc
from config import config, secret

auth = Blueprint(name="auth", import_name=__name__)

@auth.route("/signin", methods=["POST"])
def sign_in():
    params = request.get_json()

    if "id" not in params.keys():  # no id in request
        abort(400)
    else:
        id = params["id"]
    
    if "pw" not in params.keys():  # no pw in request
        abort(400)
    else:
        pw = params["pw"]
    
    qresult = User.query.filter_by(id=id).all()

    if len(qresult) == 0:
        abort(400)
    else:
        row = qresult[0]

        if not bcrypt.checkpw(pw.encode("utf-8"), row.password.encode("utf-8")):  # id and pw are not matching
            abort(400)

        access_token = jwt.encode({
            "uid": row.uid,
            "exp": datetime.utcnow() + timedelta(seconds=config.JWT_ACCESS_TOKEN_EXP_TIME)
        }, secret.JWT_SECRET, algorithm=config.JWT_ALGORITHM).decode("utf-8")

        refresh_token = jwt.encode({
            "exp": datetime.utcnow() + timedelta(seconds=config.JWT_REFRESH_TOKEN_EXP_TIME)
        }, secret.JWT_SECRET, algorithm=config.JWT_ALGORITHM).decode("utf-8")

        try:
            db.session.add(Token(refresh_token, access_token))
            db.session.commit()

            return {
                "access-token": access_token,
                "refresh-token": refresh_token
            }, 200
        except:
            abort(400)


@auth.route("/id-duplicate-check", methods=["GET"])
def id_duplicate_chk():
    params = request.args.to_dict()

    if "id" not in params.keys():
        abort(400)
    
    id = params["id"]

    qresult = User.query.filter_by(id=id).all()

    if len(qresult) == 0:
        return {}, 200
    else:
        abort(400)
    

@auth.route("/signup", methods=["POST"])
def sign_up():
    params = request.get_json()

    if "id" not in params.keys():
        abort(400)
    else:
        id = params["id"]
    
    if "pw" not in params.keys():
        abort(400)
    else:
        pw = params["pw"]

    if "nickname" not in params.keys():
        abort(400)
    else:
        nickname = params["nickname"]
    
    if "email" not in params.keys():
        abort(400)
    else:
        email = params["email"]

    if "age" not in params.keys():
        abort(400)
    else:
        age = params["age"]
    
    try:
        db.session.add(User(id, pw, nickname, email, age))
        db.session.commit()
        return {}, 200
    except:
        abort(400)


@auth.route("/refresh", methods=["GET"])
def refresh_token():
    access_token = request.headers.get("x-access-token")
    refresh_token = request.headers.get("x-refresh-token")

    if access_token == None or refresh_token == None:
        abort(401)

    try:
        payload = jwt.decode(jwt=access_token, key=secret.JWT_SECRET, algorithms=config.JWT_ALGORITHM, options={"verify_exp": False})
        uid = payload["uid"]
    except jwt.InvalidTokenError:
        abort(401)

    qresult = Token.query.filter_by(refresh_token=refresh_token, access_token=access_token).order_by(desc(Token.created_at)).all()

    if len(qresult) == 0:
        abort(401)

    new_access_token = jwt.encode({
        "uid": uid,
        "exp": datetime.utcnow() + timedelta(seconds=config.JWT_ACCESS_TOKEN_EXP_TIME)
    }, secret.JWT_SECRET, algorithm=config.JWT_ALGORITHM).decode("utf-8")

    qresult[0].access_token = new_access_token
    db.session.commit()

    return {
        "access-token": new_access_token
    }, 200
