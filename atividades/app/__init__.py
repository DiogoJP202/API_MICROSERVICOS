from flask import Flask
from flasgger import Swagger
from .extensions import db
from .config import Config
from .controllers import register_controllers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Swagger(app)

    register_controllers(app)

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app