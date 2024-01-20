from email import message
from flask import Flask, request
from db import items, stores
from flask_smorest import abort
import uuid

app = Flask(__name__)


@app.get("/store")
def get_stores():
    return {"stores": list(stores.values())}


@app.post("/store")
def create_store():
    request_data = request.get_json()
    if "name" not in request_data:
        abort(404, message='Bad Request. Ensure that "name" is included in the request\'s JSON payload.')

    for store in stores.values():
        if store["name"] == request_data["name"]:
            abort(404, message=f'Bad Request. Store with name {request_data["name"]} already exists.')

    store_id = uuid.uuid4().hex
    new_store = {**request_data, "id": store_id}
    stores[store_id] = new_store
    return new_store, 201


@app.post("/item")
def create_item():
    item_data = request.get_json()
    if (
        "price" not in item_data
        or "store_id" not in item_data
        or "name" not in item_data
    ):
        abort(
            401,
            message='Bad request. Ensure that "price", "store_id" and "name" are included in the request\'s JSON payload.'
        )
    if item_data["store_id"] not in stores:
        abort(404, message= "Store not found")

    for item in items.values():
        if (
            item["store_id"] == item_data["store_id"]
            and item["name"] == item_data["name"]
        ):
            abort(404, message='Item already exists.')


    item_id = uuid.uuid4().hex
    new_item = {**item_data, "id": item_id}
    items[item_id] = new_item # type: ignore
    return new_item, 200


@app.get("/item")
def get_all_items():
    return {"items": list(items.values())}


@app.get("/store/<string:store_id>")
def get_store_items(store_id):
    try:
        return {"store": stores[store_id]}, 200
    except KeyError:
        abort(404, message="Store not found")


@app.get("/item/<string:item_id>") # type: ignore
def get_items_in_store(item_id):
    try:
        return items[item_id], 200
    except KeyError:
        abort(404, message="Item not found")
