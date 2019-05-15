# -*- coding: UTF-8 -*-
from app.auth.auths import Auth
from app.users.model import Users
import time
from flask import request, jsonify
from .. import common
from app import myDb

db = myDb['users']
db1 = myDb['book']


def init_api(app):
    @app.route('/api/register', methods=['POST'])
    def reagister():
        """
        用户注册
        :return:json
        """
        username = request.json.get('username')
        password = request.json.get('password')
        user_info = Users.find_by_username(username)
        if user_info.count() == 0:
            user = Users(username, Users.set_password(Users, password))
            result = Users.add_user(user)
            return jsonify(common.trueReturn('成功', '注册成功'))
        else:
            return jsonify(common.falseReturn('失败', '用户名重复'))

    @app.route('/api/login', methods=['POST'])
    def login():
        username = request.json.get('username')
        password = request.json.get('password')
        if (not username or not password):
            return jsonify(common.falseReturn('', '用户名和密码不能为空'))
        else:
            user_info = Users.find_by_username(username)
            if user_info.count() != 0 and Users.check_password(Users, user_info[0]['password'], password):
                login_tiem = int(time.time())
                token = Auth.authenticate(Auth, username, login_tiem)
                return jsonify(common.trueReturn('成功', token))
            else:
                return jsonify(common.falseReturn('失败', '用户名或密码错误'))

    @app.route('/api/test', methods=['GET'])
    def test():
        result = Auth.identify(Auth, request)
        print(result)
        if result['status']:
            r = db1.find({},{"t1":1,"_id":0})
            print(r.count())
            book_cnt = {}
            for i in r:
                if i['t1'] in book_cnt.keys():
                    book_cnt[i['t1']] += 1
                else:
                    book_cnt[i['t1']] = 1
            print(book_cnt)
            return '1'
        else:
            return result
        # if (result['status'] and result['data']):
        #     user = Users.get(Users, result['data'])
        #     returnUser = {
        #         'username': user.username,
        #         'login_time': user.login_time
        #     }
        #     print(returnUser)
        #     result = common.trueReturn(returnUser, "请求成功")
        # return jsonify(result)
