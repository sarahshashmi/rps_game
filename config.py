from datetime import timedelta

"""Flask configuration."""
from os import environ, path
# from dotenv import load_dotenv

# basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, '.env'))

class Config:
    """Base config."""
    # SECRET_KEY = environ.get('SECRET_KEY')
    SECRET_KEY = "thisismysecret" #change this!"
    JWT_SECRET_KEY = SECRET_KEY
    DEBUG = True
    TESTING = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    MAX_ROUNDS = 5
    VALID_MOVES = ['rock', 'scissor', 'paper']

class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    MONGO_URI = "mongodb://localhost:27017/rps_database_dev"
    # DATABASE_URI = environ.get('DEV_DATABASE_URI')

class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    MONGO_URI = "mongodb://localhost:27017/rps_database"
    # DATABASE_URI = environ.get('PROD_DATABASE_URI')