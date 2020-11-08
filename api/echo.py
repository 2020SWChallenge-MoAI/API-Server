from flask import Blueprint, request, abort, g
import jwt

from config import config, secret

echo = Blueprint(name="echo", import_name=__name__)

@echo.route("", methods=["GET", "POST"])
def echo_func():
    result = {}

    access_token_result = {}
    access_token = request.headers.get("x-access-token")
    if access_token is not None:
        access_token_result["x-access-token"] = access_token
        try:
            payload = jwt.decode(jwt=access_token, key=secret.JWT_SECRET, algorithms=config.JWT_ALGORITHM, options={"verify_exp": False})
            access_token_result.update(payload)
            access_token_result["validity"] = True
        except:
            access_token_result["validity"] = False
    result["access_token"] = access_token_result

    result["method"] = request.method

    if request.method == "GET":    
        result["params"] = request.args.to_dict()
    elif request.method == "POST":
        result["params"] = request.get_json()
    
    return result, 200

