# -*- coding: UTF-8 -*-
from app.auth.auths import Auth
from app.users.model import Users
from flask import request, jsonify
from .. import common
from app import myDb
from app.book.model import Book
import time

db = myDb['book-test-1']
udb = myDb['users']


def init_book_api(app):
    @app.route('/api/book/get_book_type', methods=['GET'])
    def get_book_type():
        auth = Auth.identify(Auth, request)
        if auth['status']:
            r = db.find({}, {"t1": 1, "_id": 0})
            book_cnt = {}
            for i in r:
                if i['t1'] in book_cnt.keys():
                    book_cnt[i['t1']] += 1
                else:
                    book_cnt[i['t1']] = 1
            return jsonify(common.trueReturn(book_cnt, 'success'))
        else:
            return auth

    @app.route('/api/book/book_get_book_t2_type', methods=['GET'])
    def get_book_t2_type():
        auth = Auth.identify(Auth, request)
        t1 = request.args.get('t1')
        if auth['status']:
            r = db.find({"t1": t1}, {"t2": 1, "_id": 0})
            book_cnt = {}
            for i in r:
                if i['t2'] in book_cnt.keys():
                    book_cnt[i['t2']] += 1
                else:
                    book_cnt[i['t2']] = 1
            return jsonify(common.trueReturn(book_cnt, 'success'))
        else:
            return auth

    @app.route('/api/book/get_book_count', methods=['GET'])
    def get_book_count():
        auth = Auth.identify(Auth, request)
        if auth['status']:
            r = db.find().count()
            return jsonify(common.trueReturn(r, 'success'))
        else:
            return auth

    @app.route('/api/book/get_book', methods=['GET'])
    def get_all_book():
        auth = Auth.identify(Auth, request)
        if auth['status']:
            limit = int(request.args.get('limit'))
            offset = int(request.args.get('offset'))
            search = request.args.get('book_name')
            type = request.args.get('book_type')
            if search:
                if type:
                    r = db.find({"book_name": {"$regex": search}, "t1": type}, {"_id": 0}).limit(limit).skip(offset)
                else:
                    r = db.find({"book_name": {"$regex": search}}, {"_id": 0}).limit(limit).skip(offset)
            else:
                if type:
                    r = db.find({"t1": type}, {"_id": 0}).limit(limit).skip(offset)
                else:
                    r = db.find({}, {"_id": 0}).limit(limit).skip(offset)
            book_list = []
            cnt = r.count()
            for i in r:
                book_list.append(i)
            result = {
                'book': book_list,
                'total': cnt
            }
            return jsonify(common.trueReturn(result, 'success'))
        else:
            return auth

    @app.route('/api/book/book_detail/<book_id>', methods=['GET'])
    def book_detail(book_id):
        auth = Auth.identify(Auth, request)
        if auth['status']:
            r = db.find_one({"book_id": book_id}, {"_id": 0})
            Users.add_view_history(auth, r)
            Users.rate_to_book(auth, book_id, 0.1)
            return jsonify(common.trueReturn(r, 'success'))
        else:
            return auth

    @app.route('/api/book/backbook', methods=['POST'])
    def back_book():
        auth = Auth.identify(Auth, request)
        if auth['status']:
            book_name = request.json.get('book_name')
            result = udb.find_one({"username":auth['data']},{"_id":0,"lease_history":1})['lease_history']
            for i in result:
                if i['book']['book_name'] == book_name and i['valid']:
                    i['valid'] = False
                    udb.update_one({"username":auth['data']},{"$set":{"lease_history":result}})
                    return jsonify(common.trueReturn(result,'success'))
        else:
            return auth

    @app.route('/api/book/lease', methods=['POST'])
    def lease():
        auth = Auth.identify(Auth, request)
        if auth['status']:
            duration = int(request.json.get('duration'))
            book_name = request.json.get('book_name')
            current_time = int(time.time() * 1000)
            end_time = 2592000000 * duration + current_time
            book_id = Book.get_bookId_by_bookName(book_name)
            book = db.find_one({"book_name": book_name}, {"_id": 0})
            user_info = Users.find_by_username(auth['data'])[0]
            if 'lease_history' in user_info:
                lease_history_list = []
                for i in user_info['lease_history']:
                    if i['end_time'] > current_time and i['valid']:
                        lease_history_list.append(i['book']['book_id'])
                    else:
                        pass
                if book_id in lease_history_list:
                    return jsonify(common.falseReturn('您正在借此书', '失败'))
                else:
                    result = udb.find_one({"username": auth['data']})['lease_history']
                    book_obj = {
                        "book": book,
                        "lease_time": current_time,
                        "end_time": end_time,
                        "valid": True
                    }
                    result.insert(0, book_obj)
                    udb.update_one({"username": auth['data']}, {"$set": {"lease_history": result}})
                    Users.rate_to_book(auth, book_id, 2)
                    return jsonify(common.trueReturn(result, 'success'))
            else:
                result = []
                book_obj = {
                    "book": book,
                    "lease_time": current_time,
                    "end_time": end_time,
                    "valid":True
                }
                result.append(book_obj)
                udb.update_one({"username": auth['data']}, {"$set": {"lease_history": result}})
                Users.rate_to_book(auth, book_id, 2)
                return jsonify(common.trueReturn(result, 'success'))
        else:
            return auth

    @app.route('/api/book/get_lease_list', methods=['GET'])
    def get_lease_list():
        auth = Auth.identify(Auth, request)
        if auth['status']:
            limit = int(request.args.get('limit'))
            offset = int(request.args.get('offset'))
            result = udb.find_one({"username": auth['data']})
            if 'lease_history' in result:
                result = result['lease_history'][offset:limit + offset]
            else:
                result = []
            lease_list = []
            for i in result:
                if time.time() > i['end_time']:
                    i['expired'] = True
                else:
                    i['expired'] = False
                lease_list.append(i)
            udb.update_one({"username": auth['data']}, {"$set": {"lease_history": result}})
            r = {
                "lease_list": lease_list,
                "total": len(result)
            }
            return jsonify(common.trueReturn(r, 'success'))
        else:
            return auth

    @app.route('/api/book/random', methods=['GET'])
    def random():
        auth = Auth.identify(Auth, request)
        if auth['status']:
            t1 = request.args.get('t1')
            t2 = request.args.get('t2')
            result = []
            if t1 and t2:
                print(123123)
                r = db.aggregate([{"$match": {"t1": t1, "t2": t2}}, {"$sample": {"size": 5}}])
            else:
                print('2xxx')
                r = db.aggregate([{"$sample": {"size": 5}}])
            for i in r:
                i['_id'] = 1
                result.append(i)
            return jsonify(common.trueReturn(result, 'success'))
        else:
            return auth
