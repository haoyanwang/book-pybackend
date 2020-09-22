# -*- coding: UTF-8 -*-
import jwt, datetime, time
from app import myDb
from .. import config,common
from app.users.model import Users

db = myDb['users']


class Auth():
    @staticmethod
    def encode_auth_token(username, login_time):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=10),
                'iat': datetime.datetime.utcnow(),
                'data': {
                    'username': username,
                    'login_time': login_time,
                }
            }
            return jwt.encode(
                payload,
                config.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            # payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), leeway=datetime.timedelta(seconds=10))
            payload = jwt.decode(auth_token, config.SECRET_KEY, options={'verify_exp': False})
            if ('data' in payload and 'username' in payload['data']):
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError as e:
            return 'Token过期'
        except jwt.InvalidTokenError as e:
            return '无效Token'

    def authenticate(self, username, login_time):
        """
        :param password:
        :return: json
        """
        print(username)
        token = str(self.encode_auth_token(username, login_time), encoding='utf-8')
        return token

    def identify(self, request):
        """
        用户鉴权
        :return: list
        """
        auth_header = request.headers.get('Authorization')
        payload = self.decode_auth_token(auth_header)
        user = Users.find_by_username(payload['data']['username'])
        if user.count() == 0:
            result = common.falseReturn('', '找不到该用户信息')
        else:
            result = common.trueReturn(user[0]['username'], '请求成功')
        print(result)
        return result