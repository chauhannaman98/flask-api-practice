from flask import Flask, request
from db import items, stores
import uuid

app = Flask(__name__)


@app.get("/store")
def get_stores():
    return {"stores": list(stores.values())}


@app.post("/store")
def create_store():
    request_data = request.get_json()
    store_id = uuid.uuid4().hex
    new_store = {**request_data, "id": store_id}
    stores[store_id] = new_store
    return new_store, 201


@app.post("/item")
def create_item():
    item_data = request.get_json()
    if item_data["store_id"] not in stores:
        return {"message": "Store not found"}, 404
    item_id = uuid.uuid4().hex
    new_item = {**item_data, "id": item_id}
    items[item_id] = new_item # type: ignore
    return new_item, 200


@app.get("/item")
def get_all_items():
    return {"items": list(items.values())}


@app.get("/store/<string:store_id>/")
def get_store_items(store_id):
    try:
        return {"store": stores[store_id]}, 200
    except KeyError:
        return {"message": "Store not found"}, 404


@app.get("/item/<string:item_id>") # type: ignore
def get_items_in_store(item_id):
    try:
        return items[item_id], 200
    except KeyError:
        return {"message": "Item not found"}, 404
