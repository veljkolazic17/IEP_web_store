from crypt import methods
import io
import csv
from pickle import NONE
from sys import stdout
from unicodedata import category
from redis import Redis
import json
from flask import Flask, request, Response, jsonify
from sqlalchemy import and_
from decoraters import role_check
from  configuration import Configuration
from models import database, Item, ItemOrder, Category, CategoryItem, Order
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

@application.route("/search", methods = ["GET"])
@role_check(role="customer")
def search():
    arguments = request.args.items()
    category_list = []
    item_list = []

    ITEM_NAME = None
    CATEGORY_NAME = None

    for argument in arguments:
        if argument[0] == "name":
            ITEM_NAME = argument[1]
        elif argument[0] == "category":
            CATEGORY_NAME = argument[1]


    if ITEM_NAME is not None and CATEGORY_NAME is not None:
        category_list = Category.query.join(CategoryItem).filter(Category.name.like(f"%{CATEGORY_NAME}%")).join(Item).filter(Item.name.like(f"%{ITEM_NAME}%")).all()
    elif CATEGORY_NAME is not None:
        category_list = Category.query.join(CategoryItem).filter(Category.name.like(f"%{CATEGORY_NAME}%")).join(Item).all()
    elif ITEM_NAME is not None:
        category_list = Category.query.join(CategoryItem).join(Item).filter(Item.name.like(f"%{ITEM_NAME}%")).all()
    else:
       category_list = Category.query.join(CategoryItem).join(Item).all()

    if ITEM_NAME is not None and CATEGORY_NAME is not None:
        item_list = Item.query.join(CategoryItem).filter(Item.name.like(f"%{ITEM_NAME}%")).join(Category).filter(Item.name.like(f"%{CATEGORY_NAME}%")).all()
    elif ITEM_NAME is not None:
        item_list = Item.query.join(CategoryItem).filter(Item.name.like(f"%{ITEM_NAME}%")).join(Category).all()
    elif CATEGORY_NAME is not None:
        item_list = Item.query.join(CategoryItem).join(Category).filter(Category.name.like(f"%{CATEGORY_NAME}%")).all()
    else:
       item_list = Item.query.join(CategoryItem).join(Category).all()


    categories_list_json = []
    items_list_json = []

    for category in category_list:
        categories_list_json.append(category.name)
    
    for item in item_list:
        items_list_json.append({
            "categories": [category.name for category in item.categories],
            "id": item.id,
            "name": item.name,
            "price": item.price,
            "quantity": item.count
        })

    return jsonify(categories=categories_list_json, products=items_list_json), 200


@application.route("/order", methods = ["POST"])
@role_check(role="customer")
def order():
    requests = request.json.get("requests")

    if requests is None:
        return jsonify(message="Field requests is missing."), 400

    identity = get_jwt_identity()
    order = Order(email = identity)
    summed_price = 0
    database.session.add(order)
    database.session.flush()

    order_completed = False
    for i,order_request in enumerate(requests):
        try:
            id = order_request["id"]
        except:
            return  jsonify(message=f"Product id is missing for request number {i}."), 400
        
        try:
            count = order_request["quantity"]
        except:
            return jsonify(message=f"Product quantity is missing for request number {i}."), 400

        if id is None:
            return jsonify(message=f"Product id is missing for request number {i}."), 400
        if count is None:
            return jsonify(message=f"Product quantity is missing for request number {i}."), 400
        
        try:
            if id < 0:
                return  jsonify(message=f"Invalid product id for request number {i}."), 400
        except:
            return  jsonify(message=f"Invalid product id for request number {i}."), 400

        try:
            if count < 0:
                return jsonify(message=f"Invalid product quantity for request number {i}."), 400
        except:
            return jsonify(message=f"Invalid product quantity for request number {i}."), 400

        item = Item.query.filter_by(id=id).first()

        if item is None:
            return jsonify(message=f"Invalid product for request number {i}."), 400

        amount_recieved = 0
        amount_requested = 0

        if item.count >= count:
            item.count -= count
            amount_recieved = amount_requested = count
            order_completed = True
        else:
            amount_requested = count
            amount_recieved = item.count
            item.count = 0
            order_completed = False
        
        summed_price += count * item.price
        
        item_order = ItemOrder(
            status = 1 if order_completed else 0,
            amount_recieved=amount_recieved,
            amount_requested=amount_requested,
            item_id = item.id,
            order_id = order.id,
            price = item.price
        )

        database.session.add(item_order)
        database.session.flush()
        
    order.status = 1 if order_completed else 0
    order.summed_price = summed_price
    database.session.add(order)
    database.session.commit()
    
    return jsonify(id=order.id), 200


@application.route("/status", methods = ["GET"])
@role_check(role="customer")
def status():
    email = get_jwt_identity()
    orders = Order.query.filter_by(email=email)

    orders_json = []
    for order in orders:
        items_json = []
        for item in order.items:
            items_json.append({
                "categories": [category.name for category in item.categories],
                "name": item.name,
                "price": ItemOrder.query.filter_by(item_id=item.id, order_id=order.id).first().price,
                "received": ItemOrder.query.filter_by(item_id=item.id, order_id=order.id).first().amount_recieved,
                "requested": ItemOrder.query.filter_by(item_id=item.id, order_id=order.id).first().amount_requested
            })
        orders_json.append({
            "products": items_json,
            "price": order.summed_price,
            "status": "COMPLETE" if order.status == 1 else "PENDING",
            "timestamp": order.timestamp.isoformat()
        })

    return jsonify(orders=orders_json), 200
        


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug = True, port=5001, host='0.0.0.0')
    