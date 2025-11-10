from flask import Flask, jsonify, request              # to create flask app and handle requests
from flask_sqlalchemy import SQLAlchemy                # to connect flask with database
from flask_marshmallow import Marshmallow              # to convert complex data types to JSON
from flask_migrate import Migrate                      # to handle database migrations
from config import Config                             # import configuration class (ensure config.py exists)

# ----------------------------------------------------
# App Configuration
# ----------------------------------------------------
app = Flask(__name__)

# Load database configurations from Config class
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)  # <-- Added this line to enable migrations

# ----------------------------------------------------
# Routes
# ----------------------------------------------------
@app.route('/')
def home():
    return "Employee Tracker API is running!"


# ----------------------------------------------------
# Import routes after db initialization
# ----------------------------------------------------
from routes import *

# ----------------------------------------------------
# Run the App
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
