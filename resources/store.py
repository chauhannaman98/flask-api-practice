import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import stores
from schema import StoreSchema

blp = Blueprint("stores", __name__, description="Operations in Stores")

@blp.route('/store/<string:store_id>')
class Store(MethodView):
    def get(self, store_id):
        try:
            return {"store": stores[store_id]}, 200
        except KeyError:
            abort(404, message="Store not found")

    def delete(self, store_id):
        try:
            del stores[store_id]
            return {"message": "Store has been deleted."}
        except KeyError:
            abort(404, message="Unablet to find the store.")

@blp.route("/store")
class StoreList(MethodView):
    def get(self):
        return {"stores": list(stores.values())}

    @blp.arguments(StoreSchema)
    def post(self, store_data):
        for store in stores.values():
            if store_data["name"] == store["name"]:
                abort(400, message=f"Store already exists.")

        store_id = uuid.uuid4().hex
        store = {**store_data, "id": store_id}
        stores[store_id] = store

        return store
