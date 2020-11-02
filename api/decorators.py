from functools import wraps
from functions import *
from flask import request, abort, g
from config import config, secret
import jwt

def bid_validity_chk_required(f):
    @wraps(f)
    def decorated_function(bid, *args, **kwargs):
        if not isValidBid(bid):
            abort(404)
        else:
            return f(bid, *args, **kwargs)
    
    return decorated_function

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