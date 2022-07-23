from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class User(database.Model):
    __tablename__ = "users"

    # Columns
    id = database.Column(database.Integer, primary_key = True)
    email = database.Column(database.String(256), nullable = False)
    password = database.Column(database.String(256), nullable = False)
    forename = database.Column(database.String(256), nullable = False)
    surname = database.Column(database.String(256), nullable = False)

    # Foreign keys
    role_id = database.Column(database.Integer, 
        database.ForeignKey("roles.id"), nullable = False)

class Role(database.Model):
    __tablename__ = "roles"

    # Columns
    id = database.Column(database.Integer, primary_key = True)
    role_name = database.Column(database.String(256), nullable = False)