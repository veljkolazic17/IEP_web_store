from crypt import methods
import io
import csv
from sqlalchemy import func
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

@application.route("/productStatistics", methods=["GET"])
@role_check("admin")
def productStatistics():

    statistics = []

    sum_amount_recieved = func.sum(ItemOrder.amount_recieved)
    sum_amount_requested = func.sum(ItemOrder.amount_requested)

    item_orders = ItemOrder.query.group_by(ItemOrder.item_id).with_entities(ItemOrder.item_id, sum_amount_recieved,sum_amount_requested-sum_amount_recieved).all()
    for item in item_orders:
        statistics.append({
            "name": Item.query.filter_by(id=item[0]).first().name,
            "sold": item[1],
            "waiting": item[2]
        })

    return jsonify(statistics=statistics), 200

@application.route("/categoryStatistics", methods=["GET"])
@role_check("admin") 
def categoryStatistics():
    sum_amount_recieved = func.sum(ItemOrder.amount_recieved)
    categories = Category.query.join(CategoryItem, Category.id==CategoryItem.category_id).join(ItemOrder, CategoryItem.item_id==ItemOrder.item_id).group_by(Category.id).order_by(sum_amount_recieved.desc()).order_by(Category.name).with_entities(Category.name).all()
    statistics = []
    for category in categories:
        statistics.append(category[0])
    return jsonify(statistics=statistics), 200

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug = True, port=5000, host='0.0.0.0')
    