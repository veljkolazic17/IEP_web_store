from dataclasses import dataclass
from datetime import timedelta
import os

# Environment variables (default values if not present)
# Variables are added thorugh dockerfile; not NULL when run througn docker, otherwise default values are present
databaseUrl = os.environ.get("DATABASE_URL") or "storedb"
user = os.environ.get("ROOT_USER")  or "root"
password = os.environ.get("ROOT_PASSWORD") or "root"
jwt_secret_key = os.environ.get("JWT_SECRET_KEY") or "backupkey117"
redis_host = os.environ.get('REDIS_HOST') or 'redis'
redis_product_list = os.environ.get("REDIS_PRODUCT_LIST") or 'items'

# Configuration class used only in this app
class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{databaseUrl}/store"
    JWT_SECRET_KEY = jwt_secret_key
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    REDIS_HOST = redis_host
    REDIS_PRODUCT_LIST = redis_product_list