from app import myDb
from app.recommend.model import Recommand
from flask import jsonify
from .. import common,request
from app.auth.auths import Auth
from app.book.model import Book

db = myDb['users']
def init_recommand_api(app):
    @app.route('/api/recommand/get_recommand', methods=['GET'])
    def get_recommand():
        auth = Auth.identify(Auth, request)
        if auth['status']:
            r = Recommand.gen_matrix(Recommand)
            top_n = Recommand.get_top_n(r,5)
            result = []
            for i in top_n.get(auth['data']):
                result.append(Book.get_book_by_bookId(i[0]))
            return jsonify(common.trueReturn(result,'success'))
        else:
            return auth

    @app.route('/api/recommand/get_rate_map', methods=['GET'])
    def get_map():
        auth = Auth.identify(Auth,request)
        if auth['status']:
            result = db.find_one({"username":auth['data']})
            if 'rate_map' in result:
                return jsonify(common.trueReturn(result['rate_map'],'success'))
            else:
                return jsonify(common.falseReturn({},'false'))
        else:
            pass

