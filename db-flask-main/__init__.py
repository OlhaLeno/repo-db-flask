from flask import Flask
from os import getenv
from urllib.parse import quote_plus
from flasgger import Swagger
from dotenv import load_dotenv
from my_project.db_init import db

load_dotenv()

def create_app():
    app = Flask(__name__)

    db_host = getenv("DB_HOST") or getenv("DB_HOST_AZURE")
    db_user = getenv("DB_USER") or getenv("DB_USERNAME_AZURE")
    db_password = getenv("DB_PASSWORD") or getenv("DB_PASSWORD_AZURE")
    db_name = getenv("DB_NAME")
    db_port = getenv("DB_PORT", "3306")

    if db_host and db_user and db_password and db_name:
        database_url = f"mysql+pymysql://{db_user}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}?ssl_disabled=false&ssl_verify_cert=false&ssl_verify_identity=false"
    else:
        database_url = getenv("DATABASE_URL", "sqlite:///default.db")
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 20,
        "max_overflow": 0,
    }
    
    secret_key = getenv("SECRET_KEY")
    if not secret_key:
        import secrets
        secret_key = secrets.token_hex(32)
        print("WARNING: SECRET_KEY not set, using generated key. Set SECRET_KEY environment variable for production!")
    
    app.config["SECRET_KEY"] = secret_key

    db.init_app(app)
    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Bus Management API",
            "description": "Auto-generated docs for available REST endpoints",
            "version": "1.0.0",
        },
        "host": getenv("API_HOST", "localhost:5000"),
        "schemes": ["http", "https"],
    })

    return app