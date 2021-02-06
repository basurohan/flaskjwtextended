from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from db import db
from blacklist import BLACKLIST
from resource import (
    ItemResource,
    ItemListResource,
    RegisterUser,
    StoreResource,
    StoreListResource,
    UserResource,
    UserLoginResource,
    UserLogoutResource,
    TokenRefresh
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.secret_key = 'secret_key'  # OR app.config['JWT_SECRET_KEY'] = 'secret_key'
api = Api(app)

db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)


@jwt.user_claims_loader
def add_claim_to_jwt(identity):
    if identity == 1:
        return {'is_admin': True}
    else:
        return {'is_admin': False}


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'Token has expired',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': 'Signature verification failed',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback():
    return jsonify({
        'description': 'Request does not contain an access token.',
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        'description': 'The token is not fresh.',
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'description': 'The token has been revoked.',
        'error': 'token_revoked'
    }), 401


api.add_resource(UserResource, '/user/<int:user_id>')
api.add_resource(UserLoginResource, '/login')
api.add_resource(UserLogoutResource, '/logout')
api.add_resource(RegisterUser, '/register')
api.add_resource(TokenRefresh, '/refresh')

api.add_resource(StoreResource, '/store/<string:name>')
api.add_resource(StoreListResource, '/stores')

api.add_resource(ItemResource, '/item/<string:name>')
api.add_resource(ItemListResource, '/items')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
