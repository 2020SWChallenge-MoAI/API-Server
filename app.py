import os
import sys
import logging
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from database import db
from config import config
from functions import *

from api import book, auth, user, echo, demo

app = Flask(config.APP_NAME)
CORS(app)

# JSON 한글 깨짐 방지
app.config["JSON_AS_ASCII"] = False

# DB
app.config["SQLALCHEMY_DATABASE_URI"] = getDBURI()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Turn off default logger
if not config.DEBUG:
    app.logger.disable = True
    logging.getLogger("werkzeug").disabled = True
    sys.modules["flask.cli"].show_server_banner = lambda *x: None

# routing
app.register_blueprint(book.book, url_prefix="/api/book")
app.register_blueprint(auth.auth, url_prefix="/api/auth")
app.register_blueprint(user.user, url_prefix="/api/user")
app.register_blueprint(echo.echo, url_prefix="/api/echo")
app.register_blueprint(demo.demo, url_prefix="/api/demo")

app.run(host=config.APP_IP, port=config.APP_PORT, debug=config.DEBUG)