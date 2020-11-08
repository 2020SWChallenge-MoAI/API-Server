from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
import database


db = database.db

class Work(db.Model):
    __tablename__ = "Work"

    wid = db.Column(mysql.INTEGER, primary_key=True, nullable=False)
    uid = db.Column(mysql.INTEGER, nullable=False)
    bid = db.Column(mysql.INTEGER, nullable=False)
    type = db.Column(mysql.TINYINT, nullable=False)
    created_at = db.Column(mysql.DATETIME, nullable=False, default=func.now())
    updated_at = db.Column(mysql.DATETIME, nullable=False, default=func.now())
    content = db.Column(mysql.LONGTEXT, nullable=False)
    max_depth = db.Column(mysql.INTEGER)
    avg_child_num = db.Column(mysql.INTEGER)
    morethan2child_node_num = db.Column(mysql.INTEGER)
    max_depth_diff = db.Column(mysql.INTEGER)
    template_node_balance = db.Column(mysql.INTEGER)
    user_created_node_num = db.Column(mysql.INTEGER)
    ai_support_num = db.Column(mysql.INTEGER)
    duplicate_node = db.Column(mysql.INTEGER)

    def __init__(self, uid, bid, type, created_at, updated_at, content, max_depth, avg_child_num, morethan2child_node_num, max_depth_diff, template_node_balance, user_created_node_num, ai_support_num, duplicate_node):
        self.uid = uid
        self.bid = bid
        self.type = type
        self.created_at = created_at
        self.updated_at = updated_at
        self.content = content
        self.max_depth = max_depth
        self.avg_child_num = avg_child_num
        self.morethan2child_node_num = morethan2child_node_num
        self.max_depth_diff = max_depth_diff
        self.template_node_balance = template_node_balance
        self.user_created_node_num = user_created_node_num
        self.ai_support_num = ai_support_num
        self.duplicate_node = duplicate_node

