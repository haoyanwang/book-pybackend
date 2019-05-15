from flask import Flask, request
import pymongo

myClient = pymongo.MongoClient("mongodb://localhost:27017/")
myDb = myClient['book']

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
            headers = request.headers.get('Access-Control-Request-Headers')
            if headers:
                response.headers['Access-Control-Allow-Headers'] = headers
        return response

    from app.users.api import init_api
    init_api(app)

    return app
