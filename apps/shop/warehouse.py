import io
import csv
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

@application.route("/update", methods = ["POST"])
@role_check(role = "worker")
def update():

    file = request.files["file"]
    if file == None:
        return jsonify(message="Field file missing."), 400

    content = file.stream.read ( ).decode ( "utf-8" )
    stream = io.StringIO ( content )
    reader = csv.reader ( stream )

    # Parse CSV and add all items and theri categories
    line_counter = 0
    items = []
    for row in reader:

        if len(row) != 4:
            return jsonify(message="Incorrect number of values on line "+ line_counter +"."), 400

        if int(row[2]) <= 0:
            return jsonify(message="Incorrect quantity on line "+ line_counter +"."), 400

        if float(row[3]) <= 0:
            return jsonify(message="Incorrect price on line "+ line_counter +"."), 400

        item = {
            "categories": row[0],
            "name":row[1],
            "count":int(row[2]),
            "price":float(row[3])            
        }
        items.append(item)
        line_counter+=1
    
    with Redis ( host = Configuration.REDIS_HOST ) as redis:
        redis.rpush(Configuration.REDIS_PRODUCT_LIST,json.dumps(items))

    return Response()

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug = True, port=5003, host='0.0.0.0')
    