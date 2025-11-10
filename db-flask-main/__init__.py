from flask import Flask, jsonify
from os import getenv
from urllib.parse import quote_plus
from flasgger import Swagger
from flask_cors import CORS
from my_project.db_init import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Load .env for local development
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    db_host = getenv("DB_HOST") or getenv("DB_HOST_AZURE")
    db_user = getenv("DB_USER") or getenv("DB_USERNAME_AZURE")
    db_password = getenv("DB_PASSWORD") or getenv("DB_PASSWORD_AZURE")
    db_name = getenv("DB_NAME")
    db_port = getenv("DB_PORT", "3306")
    
    logger.info(f"DB Configuration: host={db_host}, user={db_user}, db={db_name}, port={db_port}")

    if db_host == 'mysql':
        database_url = f"mysql+pymysql://{db_user}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}"
        ssl_args = {}
    elif db_host:
        # Azure MySQL requires SSL
        database_url = f"mysql+pymysql://{db_user}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}"
        ssl_args = {"ssl": {"ssl_mode": "REQUIRED"}}
    else:
        database_url = getenv("DATABASE_URL", "sqlite:///default.db")
        ssl_args = {}
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 20,
        "max_overflow": 0,
        "connect_args": ssl_args
    }
    
    secret_key = getenv("SECRET_KEY")
    if not secret_key:
        import secrets
        secret_key = secrets.token_hex(32)
    
    app.config["SECRET_KEY"] = secret_key
    db.init_app(app)
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Bus Management API",
            "version": "1.0.0",
            "description": "REST API for Bus Management System"
        },
        "schemes": ["https", "http"],
        "host": getenv("SWAGGER_HOST", ""),
    }
    
    swagger_config = {
        "headers": [],
        "specs": [{"endpoint": 'apispec', "route": '/apispec.json'}],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }
    
    Swagger(app, template=swagger_template, config=swagger_config)
    return app