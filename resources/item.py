import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import items

blp = Blueprint("items", __name__, description="Operations in Items")

@blp.route('/item/<string:item_id>')
class Item(MethodView):
    def get(self, item_id):
        try:
            return items[item_id], 200
        except KeyError:
            abort(404, message="Item not found")

    def delete(self, item_id):
        try:
            del items[item_id]
            return {"message": "Item has been deleted."}
        except KeyError:
            abort(404, message="Unable to find the item.")

    def put(self, item_id):
        item_data = request.get_json()
        if (
            "price" not in item_data
            or "name" not in item_data
        ):
            abort(
                400,
                message='Bad request. Ensure that "price" and "name" are included in the request\'s JSON payload.'
            )
        try:
            item = items[item_id]
            # print(item)
            item |= item_data
            return item
        except KeyError:
            abort(404, message= "Store not found")


@blp.route("/item")
class ItemList(MethodView):
    def get(self):
        return {"items": list(items.values())}

    def post(self):
        item_data = request.get_json()
        # Here not only we need to validate data exists,
        # But also what type of data. Price should be a float,
        # for example.
        if (
            "price" not in item_data
            or "store_id" not in item_data
            or "name" not in item_data
        ):
            abort(
                400,
                message="Bad request. Ensure 'price', 'store_id', and 'name' are included in the JSON payload.",
            )
        for item in items.values():
            if (
                item_data["name"] == item["name"]
                and item_data["store_id"] == item["store_id"]
            ):
                abort(400, message=f"Item already exists.")

        item_id = uuid.uuid4().hex
        item = {**item_data, "id": item_id}
        items[item_id] = item

        return item