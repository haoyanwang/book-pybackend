# -*- coding: UTF-8 -*-
from app.auth.auths import Auth
from app.users.model import Users
import time
from flask import request, jsonify
from .. import common
from app import myDb
from app.book.model import Book
import re

db = myDb['users']


def init_user_api(app):
    @app.route('/api/user/register', methods=['POST'])
    def reagister():
        """
        用户注册
        :return:json
        """
        username = request.form.get('username')
        password = request.form.get('password')
        if len(username) < 5:
            return jsonify(common.falseReturn('fail', '用户名过短'))
        if len(password) < 5:
            return jsonify(common.falseReturn('fail', '密码过短'))
        user_info = Users.find_by_username(username)
        if user_info.count() == 0:
            user = Users(username, Users.set_password(Users, password))
            result = Users.add_user(user)
            return jsonify(common.trueReturn('成功', '注册成功'))
        else:
            return jsonify(common.falseReturn('失败', '用户名重复'))

    @app.route('/api/user/login', methods=['POST'])
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

    @app.route('/api/user/like_book', methods=['POST'])
    def like_book():
        auth = Auth.identify(Auth, request)
        if auth['status']:
            book_name = request.json.get('book_name')
            book_id = Book.get_bookId_by_bookName(book_name)
            like = request.json.get('like')
            result = db.find_one({"username": auth['data']})
            if like:
                if 'like_book_list' in result:
                    if book_name in result['like_book_list']:
                        return jsonify(common.falseReturn('已经喜欢过该书', 'false'))
                    else:
                        result['like_book_list'].append(book_name)
                        db.update_one({"username": auth['data']},
                                      {"$set": {"like_book_list": result['like_book_list']}})
                        Users.rate_to_book(auth, book_id, 0.5)
                        return jsonify(common.trueReturn('成功', 'true'))
                else:
                    like_book_list = []
                    like_book_list.append(book_name)
                    db.update_one({"username": auth['data']}, {"$set": {"like_book_list": like_book_list}})
                    Users.rate_to_book(auth, book_id, 0.5)
                    return jsonify(common.trueReturn('成功', 'true'))
            else:
                result['like_book_list'].remove(book_name)
                db.update_one({"username": auth['data']}, {"$set": {"like_book_list": result['like_book_list']}})
                Users.rate_to_book(auth, book_id, -0.5)
                return jsonify(common.trueReturn('成功', 'true'))
        else:
            return auth

    @app.route('/api/user/like_book_list', methods=['GET'])
    def like_book_list():
        auth = Auth.identify(Auth, request)
        if auth['status']:
            result = db.find_one({"username": auth['data']}, {"like_book_list": 1})
            if 'like_book_list' in result:
                return jsonify(common.trueReturn(result['like_book_list'], 'success'))
            else:
                return jsonify(common.trueReturn([], 'success'))
        else:
            return auth

    @app.route('/api/user/get_view_history', methods=['GET'])
    def get_view_history():
        auth = Auth.identify(Auth,request)
        if auth['status']:
            limit = int(request.args.get('limit'))
            offset = int(request.args.get('offset'))
            result = db.find_one({"username": auth['data']}, {"view_history": 1})['view_history'][offset:limit + offset]
            return jsonify(common.trueReturn(result, 'success'))
        else:
            return auth

    @app.route('/api/user/rank', methods=['GET'])
    def rank():
        r = db.find({},{"_id":0,"view_history":1,"lease_history":1,"like_book_list":1})
        like_list_map = {}
        view_list_map = {}
        lease_list_map = {}
        like_list_arr = []
        view_list_arr = []
        lease_list_arr = []
        for i in r:
            if 'like_book_list' in i:
                for k in i['like_book_list']:
                    if k in like_list_map:
                        like_list_map[k] += 1
                    else:
                        like_list_map[k] = 1

            if 'view_history' in i:
                for k in i['view_history']:
                    if k['book_name'] in view_list_map:
                        view_list_map[k['book_name']] += 1
                    else:
                        view_list_map[k['book_name']] = 1

            if 'lease_history' in i:
                for k in i['lease_history']:
                    if k['book']['book_name'] in lease_list_map:
                        lease_list_map[k['book']['book_name']] += 1
                    else:
                        lease_list_map[k['book']['book_name']] = 1

        for i in like_list_map:
            obj = {
                "key":i,
                "value":like_list_map[i],
                "book_id":Book.get_bookId_by_bookName(i)
            }
            like_list_arr.append(obj)

        for i in view_list_map:
            obj = {
                "key":i,
                "value":view_list_map[i],
                "book_id": Book.get_bookId_by_bookName(i)
            }
            view_list_arr.append(obj)

        for i in lease_list_map:
            obj = {
                "key":i,
                "value":lease_list_map[i],
                "book_id": Book.get_bookId_by_bookName(i)
            }
            lease_list_arr.append(obj)

        result = {
            "like_rank":like_list_arr,
            "view_rank":view_list_arr,
            "lease_rank":lease_list_arr,
        }
        return jsonify(common.trueReturn(result,'success'))

    @app.route('/api/user/detail', methods=['POST','PATCH'])
    def user_detail():
        auth = Auth.identify(Auth, request)
        if auth['status']:
            result = db.find_one({"username": auth['data']}, {"_id": 0})
            if request.method == 'POST':
                return jsonify(common.trueReturn(result,'success'))
            elif request.method == 'PATCH':
                for i in request.json:
                    if request.json[i]:
                        Users.update_user(auth['data'],i,request.json[i])
            return jsonify(common.trueReturn('1','success'))
        else:
            return auth;

    @app.route('/api/user/img', methods=['GET'])
    def user_img():
        auth = Auth.identify(Auth, request)
        if auth['status']:
            result = db.find_one({"username":auth['data']},{"_id":0,"rate_map":1})['rate_map']
            map = {}
            for i in result:
                book = Book.get_book_by_bookId(i)
                body = {
                    "t1":book['t1'],
                    "value":float(result[i])
                }
                if book['t2'] in map:
                    map[book['t2']]['value'] += body['value']
                else:
                    map[book['t2']] = body
            return jsonify(common.trueReturn(map,'success'))
        else:
            return auth