from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt
)
from werkzeug.security import safe_str_cmp

from blacklist import BLACKLIST
from model import User

_user_parser_ = reqparse.RequestParser()
_user_parser_.add_argument(
    'username',
    type=str,
    required=True,
    help='username must be provided'
)
_user_parser_.add_argument(
    'password',
    type=str,
    required=True,
    help='password must be provided'
)


class UserResource(Resource):

    def get(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            return user.json()
        return {'message': 'User not found.'}, 400

    def delete(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            user.delete()
        return {'message': 'User deleted.'}


class RegisterUser(Resource):

    def post(self):
        data = _user_parser_.parse_args()
        try:
            if User.find_by_username(data['username']):
                return {'message': 'User already exists'}, 400
            user = User(**data)
            user.persist()
        except Exception:
            return {'message': 'User could not be saved'}, 500
        else:
            return {'message': 'User created'}, 201


class UserLoginResource(Resource):

    def post(self):
        data = _user_parser_.parse_args()

        user = User.find_by_username(data['username'])

        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)

            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        return {'message': 'Invalid credentials'}, 401


class UserLogoutResource(Resource):

    @jwt_required
    def post(self):
        # blacklist the unique identifier for JWT - jti
        jti = get_raw_jwt()['jti']
        BLACKLIST.add(jti)
        return {'message': 'Successfully logged out.'}, 200


class TokenRefresh(Resource):

    @jwt_refresh_token_required
    def post(self):
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id, fresh=False)
        return {'access_token': new_token}, 200

