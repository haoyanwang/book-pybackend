# -*- coding: UTF-8 -*-
from flask import Flask
from flask_pymongo import PyMongo
import json
import base64
import hashlib
import time
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

app = Flask(__name__)
app.config.update(MONGO_DBNAME='book')
mongo = PyMongo(app)


def generate_auth_token(user_id, user_role, expires):
    s = Serializer(
        secret_key=app.config['SECRET_KEY'],
        salt=app.config['AUTH_SALT'],
        expires_in=expires)
    timestamp = time.time()
    print s.dumps(
        {'user_id': user_id,
         'user_role': user_role,
         'iat': timestamp})


@app.route('/')
def hello_world():
    online_user = mongo.db.book.find_one()
    print(online_user)
    print(online_user['book_name'])
    online_user['_id'] = '1'
    return json.dumps(online_user)


@app.route('/test')
def test():
    generate_auth_token(1, 'admin', 10000)
    return '1'


if __name__ == '__main__':
    app.run(debug=True)
