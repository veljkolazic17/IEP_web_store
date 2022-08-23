from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database
from sqlalchemy_utils import database_exists, create_database, drop_database

dirpath = "/opt/src/store/migrations"

# This app is only used once at start of initialization of database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

# Waiting until database is ready for connection and usage
while True:
    try:
        if (database_exists(application.config["SQLALCHEMY_DATABASE_URI"])):
            drop_database(application.config["SQLALCHEMY_DATABASE_URI"])

        create_database(application.config["SQLALCHEMY_DATABASE_URI"])
        database.init_app(application)

        # Init data
        with application.app_context() as context:
            init()
            migrate(message="Production migration")
            upgrade()
            break

    except Exception as error:
        print(error)
        continue
print("Finished init")