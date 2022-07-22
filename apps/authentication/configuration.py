from dataclasses import dataclass
from datetime import timedelta
import os

databaseUrl = os.environ["DATABASE_URL"]
user = os.environ["DATABASE_USER"]
password = os.environ["DATABASE_PASSWORD"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{databaseUrl}/authentication"
    JWT_SECRET_KEY = "" # ????
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=10)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)