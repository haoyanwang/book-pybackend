from werkzeug.security import generate_password_hash, check_password_hash
from app import myDb
from flask import jsonify
from .. import common
import re

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
        result = db.find({"username": username}, {"_id": 0})
        return result

    def rate_to_book(auth, book_id, rate):
        if auth['status']:
            book_id = book_id
            rate = float(rate)
            user_info = Users.find_by_username(auth['data'])
            if 'rate_map' in user_info[0]:
                rate_map = user_info[0]['rate_map']
                if book_id in rate_map:
                    rate_map[book_id] += rate
                else:
                    rate_map[book_id] = rate
                db.update_one({"username": auth['data']}, {"$set": {"rate_map": rate_map}})
            else:
                rate_map = {
                    book_id: rate
                }
                db.update_one({"username": auth['data']}, {"$set": {"rate_map": rate_map}})
            return jsonify(common.trueReturn(Users.find_by_username(auth['data'])[0], 'success'))
        else:
            return auth

    def add_view_history(auth, book):
        if auth['status']:
            user_info = Users.find_by_username(auth['data'])
            if 'view_history' in user_info[0]:
                view_history = user_info[0]['view_history']
                if book in view_history:
                    view_history.remove(book)
                    view_history.insert(0, book)
                else:
                    view_history.insert(0, book)
                db.update_one({"username": auth['data']}, {"$set": {"view_history": view_history}})
            else:
                view_history = []
                view_history.append(book)
                db.update_one({"username":auth['data']},{"$set":{"view_history":view_history}})
        else:
            return auth

    def update_user(username,key,value):
        db.update_one({"username":username},{"$set":{key:value}})
        return True
