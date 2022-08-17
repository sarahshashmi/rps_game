from datetime import timedelta

class Config:
    """Base config."""
    SECRET_KEY = "thisismysecret" #change this!"
    JWT_SECRET_KEY = SECRET_KEY
    DEBUG = True
    TESTING = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    MAX_ROUNDS = 3
    VALID_MOVES = ['rock', 'scissor', 'paper']
    GAME_STRING_LENGTH = 4

class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    MONGO_URI = "mongodb://localhost:27017/rps_database_dev"

class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    MONGO_URI = "mongodb://localhost:27017/rps_database"