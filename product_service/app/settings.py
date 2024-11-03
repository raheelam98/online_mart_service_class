# product_service -  product_service/app/settings.py

from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()  

DB_URL = config("DB_URL", cast=Secret)