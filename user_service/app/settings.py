# user_service_auth - app/settings.py

from starlette.config import Config
from starlette.datastructures import Secret
from datetime import timedelta

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()  

# Database configuration
DB_URL = config("DB_URL", cast=Secret)

ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=60)


# JWT settings
ALGORITHM = config.get("ALGORITHM")
SECRET_KEY = config("SECRET_KEY", cast=str)              


#ACCESS_TOKEN_EXPIRE_MINUTES= timedelta(days=int(config.get("ACCESS_TOKEN_EXPIRE_MINUTES")))