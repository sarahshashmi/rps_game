from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager

# Create Flask app object
app = Flask(__name__)

# Configure application confgi object
app.config.from_object("config.DevConfig")

# Initialize db
mongodb_client = PyMongo(app)
db = mongodb_client.db

# Creates JWT object
jwt = JWTManager(app)

# Import routes
from rps_app.views.games import games_blueprint

# register our blueprints
app.register_blueprint(games_blueprint)