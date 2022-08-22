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

                        query_item = Item(
                            name = item["name"],
                            price = item["price"],
                            count = item["count"]
                        )

                        database.session.add(query_item)
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
                                item_id=query_item.id
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
                        database.session.flush()
                        
                
                        item_orders = ItemOrder.query.join(Order, Order.id==ItemOrder.order_id).filter(and_(ItemOrder.item_id==query_item.id, ItemOrder.status==0)).order_by(Order.timestamp).all()
                        for item_order in item_orders:
                            if item_order.amount_requested - item_order.amount_recieved <= query_item.count:
                                query_item.count -= item_order.amount_requested - item_order.amount_recieved
                                item_order.amount_recieved = item_order.amount_requested
                                item_order.status = 1
                                database.session.add(item_order)
                                database.session.flush()


                                orders = ItemOrder.query.filter(and_(ItemOrder.order_id == item_order.order_id, ItemOrder.status==0)).all()

                                if len(orders) == 0:
                                    order = Order.query.filter(Order.id==item_order.order_id).first()
                                    order.status = 1
                                    database.session.add(order)
                                    database.session.flush()
                                    
                            else:
                                item_order.amount_recieved += query_item.count 
                                query_item.count = 0
                                database.session.add(item_order)
                                break

                        database.session.add(query_item)
                        database.session.commit()
