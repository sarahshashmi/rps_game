from ast import arg
from flask import request
from flask.json import jsonify
import json
from functools import wraps
from rps_app import db
from rps_app.utils import generate_game_id
from rps_app.utils import determine_winner
from config import Config

def create_new_game():
    while True:
        game_id = generate_game_id()
        if not db.game.find_one({"game_id": game_id}):
            return game_id

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

def create_move(**kargs):
        # If moves for the game already exist in the table then
        # either add this move for player_2 against existing round
        # or create a new round entry for player_1 with this move
        # Also, determine winner for the round if both players moves exist        

        # Initialize variables
        winner = None
        game_status = "in_progress"
        round_finished = False
        updated_fields = {}

        username = kargs["username"]
        game_id = kargs["game_id"]
        move = kargs["move"]
        doc = kargs["doc"]
        
       # Extract document fields
        last_move_by = doc['last_move_by']
        player_1 = doc['player_1']
        player_2 = doc['player_2']
        round = doc['round']
        round_moves = doc['round_moves']
        p1_name = player_1['name']
        p1_score = player_1['score']
        p2_name = player_2['name']
        p2_score = player_2['score']
        
        if round_moves:
            round_entries = round_moves.get(str(round), {})
            if len(round_entries) == 1:
                (p1, p1_move), = round_entries.items()
                round_moves[str(round)][username] = move
                round = int(round) + 1
                round_finished = True
                if p1_move == move:
                    winner = "tie"
                else:
                    # Determine winner of the round
                    winner = determine_winner(p1_move, move)
                    if winner == "player_1":
                        winner = p1_name
                        p1_score += 1
                        updated_fields["player_1.score"] = p1_score
                    else:
                        winner = p2_name
                        p2_score += 1
                        updated_fields["player_2.score"] = p2_score
            else:
                round_moves[str(round)] = {username:move}
        else:
            round_moves = {str(round + 1): {username: move}}
            round = round + 1

        # Set game status to finish if the round reaches to MAX_ROUNDS
        # and the round has both player's moves
        # and there is no tie in score between both the players
        if round_finished and round-1 >= Config.MAX_ROUNDS:
            if p1_score != p2_score:
                game_status = "finished"
                if p1_score > p2_score:
                    winner = p1_name
                else:
                    winner = p2_name

        # update game collection/table
        updated_fields.update({"round": round, 
                        "round_moves": round_moves, 
                        "last_move_by": username, 
                        "status": game_status,
                        "winner": winner, 
                        "round_finished": round_finished})

        return updated_fields