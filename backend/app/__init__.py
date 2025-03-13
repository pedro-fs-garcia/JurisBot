from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os

load_dotenv()

# Conectar ao Redis
# redis_client = redis.Redis(host="localhost", port=6379, db=0)
# Configurar Flask-Limiter para proteção contra brute force
limiter = Limiter(key_func=get_remote_address, 
                #   storage_uri="redis://localhost:6379",  # Usa Redis como armazenamento
                  default_limits=["10 per minute"]
                )


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY",'sua-chave-secreta')
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt_secret_key")

    # init_db()

    limiter.init_app(app)

    # from .routes.main_routes import main
    # app.register_blueprint(main)

    return app
