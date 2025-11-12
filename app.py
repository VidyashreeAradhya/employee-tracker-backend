from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db
from routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app)
    register_routes(app)

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
