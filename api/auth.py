from flask import Blueprint, request, abort, g
from datetime import datetime, timedelta
from functools import wraps
import bcrypt
import jwt

from database import db
from database.user import User
from config import config, secret

auth = Blueprint(name="auth", import_name=__name__)

def signin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get("x-access-token")
        
        if access_token is None:
            abort(401)
        else:
            try:
                payload = jwt.decode(jwt=access_token, key=secret.JWT_SECRET, algorithms=config.JWT_ALGORITHM)
                g.uid = payload["uid"]
            except jwt.ExpiredSignatureError:
                abort(401)
            except jwt.InvalidTokenError:
                abort(401)
            
            return f(*args, **kwargs)

    return decorated_function

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
            "exp": datetime.utcnow() + timedelta(weeks=48)  #seconds=config.JWT_EXP_TIME
        }, secret.JWT_SECRET, algorithm=config.JWT_ALGORITHM).decode("utf-8")

        return {
            "access-token": access_token
        }, 200


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