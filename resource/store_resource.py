from flask_restful import Resource

from model import Store


class StoreResource(Resource):

    def get(self, name):
        store = Store.find_by_name(name)
        if store:
            return store.json()
        else:
            return {'message': 'Store not found'}, 404

    def post(self, name):
        if Store.find_by_name(name):
            return {'message': 'Store already exists.'}, 400

        store = Store(name)
        try:
            store.persist()
        except Exception:
            return {'message': 'error occurred while creating store'}, 500
        else:
            return store.json(), 201

    def delete(self, name):
        store = Store.find_by_name(name)
        if store:
            try:
                store.delete()
            except Exception:
                return {'message': 'Unable to delete store at this time.'}, 500
        else:
            return {'message': 'Store deleted'}


class StoreListResource(Resource):

    def get(self):
        return {'stores': [store.json() for store in Store.find_all()]}
