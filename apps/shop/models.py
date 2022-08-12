import datetime
from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

# Many to many ( Category <--> Item )
class CategoryItem(database.Model):
    __tablename__ = "categoryitem"

    # Columns
    id = database.Column(database.Integer, primary_key = True)

    # Foreign keys
    category_id = database.Column(database.Integer, 
        database.ForeignKey("categories.id"), nullable = False)
    item_id = database.Column(database.Integer,
        database.ForeignKey("items.id"), nullable = False)

class Category(database.Model):
    __tablename__ = 'categories'

    # Columns
    id = database.Column(database.Integer, primary_key = True)
    name = database.Column(database.String(256), nullable = False)

    # Relationships
    items = database.relationship("Item",
        secondary = CategoryItem.__table__, back_populates = "categories")

# Many to many ( Item <--> Order )
class ItemOrder(database.Model):
    __tablename__ = "itemorder"

    # Columns
    id = database.Column(database.Integer, primary_key = True)
    status = database.Column(database.Integer, nullable = False)
    amount_recieved = database.Column(database.Integer, nullable = False)
    amount_requested = database.Column(database.Integer, nullable = False)

    # Foreign keys
    item_id = database.Column(database.Integer,
        database.ForeignKey("items.id"), nullable = False)
    order_id = database.Column(database.Integer,
        database.ForeignKey("orders.id"), nullable = False)

class Item(database.Model):
    __tablename__ = "items"

    # Columns
    id = database.Column(database.Integer, primary_key = True)
    name = database.Column(database.String(256), nullable = False)
    price = database.Column(database.Float, nullable = False)
    count = database.Column(database.Integer, nullable = False)

    # Relationships
    categories = database.relationship("Category", 
        secondary = CategoryItem.__table__, back_populates = "items")
    orders = database.relationship("Order",
        secondary = ItemOrder.__table__, back_populates = "items")

class Order(database.Model):
    __tablename__ = "orders"

    # Columns
    id = database.Column(database.Integer, primary_key = True)
    email = database.Column(database.String(256), nullable = False)
    summed_price = database.Column(database.Float, nullable = False, default = 0)
    status = database.Column(database.Integer, nullable = False, default = 1)
    timestamp = database.Column(database.DateTime, nullable = False, default = datetime.datetime.utcnow().isoformat())

    # Relationships
    items = database.relationship("Item",
        secondary = ItemOrder.__table__, back_populates = "orders")