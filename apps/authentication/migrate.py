from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, User, Role
from sqlalchemy_utils import database_exists, create_database, drop_database

dirpath = "/opt/src/authentication/migrations"

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

            # Creates roles
            admin_role = Role(role_name = "admin")
            customer_role = Role(role_name = "customer")
            worker_role = Role(role_name = "worker")

            database.session.add_all([admin_role, customer_role, worker_role])
            database.session.commit()

            # Creates one admin account
            admin = User(
                email = "admin@admin.com",
                password = "1",
                forename = "admin",
                surname = "admin",
                role_id = 1
            )
            database.session.add(admin)
            database.session.commit()
            break

    except Exception as error:
        print(error)
        continue
print("Finished init")
exit(1)