from flask import Flask
from os import getenv
from urllib.parse import quote_plus
from flasgger import Swagger
from dotenv import load_dotenv
from my_project.db_init import db

# Завантажити змінні з .env файлу
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Читання змінних з .env файлу
    db_host = getenv("DB_HOST")
    db_user = getenv("DB_USER")
    db_password = getenv("DB_PASSWORD")
    db_name = getenv("DB_NAME")
    db_port = getenv("DB_PORT", "3306")

    # Побудова рядка підключення для MySQL
    if db_host and db_user and db_password and db_name:
        database_url = f"mysql+pymysql://{db_user}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}?ssl_verify_cert=false&ssl_verify_identity=false"
    else:
        # Fallback для локальної розробки
        database_url = getenv("DATABASE_URL", "sqlite:///default.db")
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    app.config["SECRET_KEY"] = getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # Initialize extensions
    db.init_app(app)
    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Bus Management API",
            "description": "Auto-generated docs for available REST endpoints",
            "version": "1.0.0",
        },
    })

    return app