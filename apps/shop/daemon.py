import json
from sys import stdout
from unicodedata import name
from redis import Redis
from flask import Flask, request, Response, jsonify
from models import database, Item, ItemOrder, Order, Category, CategoryItem
from sqlalchemy import and_
from decoraters import role_check
from configuration import Configuration

application = Flask(__name__)

if __name__ == "__main__":
    print("Daemon started!")
    stdout.flush()

    application.config.from_object(Configuration)
    database.init_app(application)

    with Redis ( host = Configuration.REDIS_HOST ) as redis:
        while True:
            with application.app_context():
                items = json.loads(redis.blpop(Configuration.REDIS_PRODUCT_LIST)[1])

                for item in items:
                    query_item = Item.query.filter_by(name=item["name"]).first()
                    categories = item["categories"].split("|")
                    
                    if query_item is None:

                        new_item = Item(
                            name = item["name"],
                            price = item["price"],
                            count = item["count"]
                        )

                        database.session.add(new_item)
                        database.session.commit()

                        for category in categories:
                            category_id = None
                            query_category = Category.query.filter_by(name=category).first()

                            if query_category is None:
                                new_category = Category(name=category)
                                database.session.add(new_category)
                                database.session.commit()
                                category_id = new_category.id
                            else:
                                category_id = query_category.id

                            database.session.add(CategoryItem(
                                category_id=category_id,
                                item_id=new_item.id
                            ))
                            database.session.commit()
                    else:
                        if len(query_item.categories) != len(categories):
                            continue
                        error = False
                        for category_obj in query_item.categories:
                            found = False
                            for category_name in categories:
                                if category_name == category_obj.name:
                                    found = True
                                    break            
                            if found == False:
                                error = True
                                break
                        if error == True:
                            continue

                        new_price = (query_item.count * query_item.price + item["count"] * item["price"])/(query_item.count + item["count"])
                        query_item.price = new_price
                        query_item.count += item["count"]
                        database.session.add(query_item)
                        database.session.commit()
                
                pass
