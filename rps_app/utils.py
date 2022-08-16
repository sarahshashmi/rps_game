import random, string
from functools import wraps
from flask import request
from flask.json import jsonify
import json
from rps_app import db

def generate_game_id():
    while True:
        game_id = ''.join(random.choices(string.ascii_lowercase, k=4))

        if not db.game.find_one({"game_id": game_id}):
            return game_id

def determine_winner(p1_move, p2_move):
    if p1_move == "rock" and p2_move == "scissor":
        return("player_1")
    elif p1_move == "scissor" and p2_move == "paper":
        return("player_1")
    elif p1_move == "paper" and p2_move == "rock":
        return("player_1")
    return("player_2")

def verify_joining():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                game_id = kwargs['game_id']
                                    
                # Extract query parameters
                post_data = json.loads(request.data)
                username = post_data.get('username')
                if not username:
                    return jsonify({"error": "missing username"}), 400

                # Return error if the game doesn't exist
                doc = db.game.find_one({"game_id": game_id})
                if not doc:
                    return jsonify({"error": "game doesn't exist"}), 422

                # If player_2 already exists for the given game, 
                # then this endpoint request can't be processed anymore
                if doc.get('player_2'):
                    return jsonify({"error":"bad request"}), 400

                # Return error if Player_2 name is same as Player_1 name
                if username == doc['player_1']['name']:
                    return jsonify({"error": "please choose another username"}), 422
            except:
                return jsonify({"error": "bad request"}), 400
            return fn(*args, **kwargs)
        return decorator
    return wrapper  