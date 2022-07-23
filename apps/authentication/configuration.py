from dataclasses import dataclass
from datetime import timedelta
import os

# Environment variables (default values if not present)
databaseUrl = os.environ["DATABASE_URL"] or "authenticationdb"
user = os.environ["ROOT_USER"]  or "root"
password = os.environ["ROOT_PASSWORD"] or "root"
jwt_secret_key = os.environ["JWT_SECRET_KEY"] or "backupkey117"

# Configuration class used only in this app
class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{databaseUrl}/authentication"
    JWT_SECRET_KEY = jwt_secret_key
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)