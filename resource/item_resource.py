from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    jwt_optional,
    get_jwt_claims,
    get_jwt_identity,
    fresh_jwt_required
)

from model import Item, Store


class ItemResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'price',
        type=float,
        required=True,
        help='This field cannot be left blank.'
    )
    parser.add_argument(
        'store_id',
        type=int,
        required=True,
        help='Every item needs a store id.'
    )

    @jwt_required
    def get(self, name):
        item = Item.find_by_name(name)
        if item:
            return {'item': item.json()}
        else:
            return {'message': 'item not found'}, 404

    @fresh_jwt_required
    def post(self, name):
        if Item.find_by_name(name):
            return {'message': 'item already exists'}

        data = ItemResource.parser.parse_args()

        if Store.find_by_id(data['store_id']) is None:
            return {'message': 'invalid store_id'}

        item = Item(name, data['price'], data['store_id'])
        try:
            item.persist()
        except Exception:
            return {'message': 'error occurred while creating item'}, 500
        else:
            return item.json(), 201

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401

        item = Item.find_by_name(name)
        if item is None:
            return {'message': 'item does not exist'}, 400

        try:
            item.delete()
        except Exception:
            return {'message': 'error occurred while deleting item'}, 500
        else:
            return {'message': 'item deleted'}

    def put(self, name):
        data = ItemResource.parser.parse_args()

        item = Item.find_by_name(name)
        if item is None:
            item = Item(name, data['price'], data['store_id'])
        else:
            item.price = data['price']
            item.store_id = data['store_id']

        item.persist()
        return item.json(), 201


class ItemListResource(Resource):

    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = Item.find_all()
        if user_id:
            return {'items': [item.json() for item in items]}, 200

        return {
            'items': [item.name for item in items],
            'message': 'More data available if you log in.'
        }, 200
