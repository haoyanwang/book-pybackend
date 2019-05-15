from werkzeug.security import generate_password_hash, check_password_hash
from app import myDb
from flask import jsonify
from .. import common


db = myDb['users']

class Users():
    # id = db.Column(db.Integer, primary_key=True)
    # email = db.Column(db.String(250), unique=True, nullable=False)
    # username = db.Column(db.String(250), unique=True, nullable=False)
    # password = db.Column(db.String(250))
    # login_time = db.Column(db.Integer)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __str__(self):
        return "Users(username='%s')" % self.username

    def set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, hash, password):
        return check_password_hash(hash, password)

    def add_user(self):
        try:
            obj = {
                'username': self.username,
                'password': self.password
            }
            result = db.insert_one(obj)
            return jsonify(common.trueReturn('success', 'register'))
        except Exception as e:
            return jsonify(common.falseReturn('error', e))

    def find_by_username(username):
        result = db.find({"username": username})
        return result
