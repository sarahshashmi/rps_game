"""Import packages."""
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
    """Return randomly generated game_id.

    Returns the generated game_id if it doesn't already 
    exist in the table. else, keep re-generating.
    """
    while True:
        game_id = generate_game_id()
        if not db.game.find_one({"game_id": game_id}):
            return game_id

def verify_joining():
    """Validate if the request to join route is valid or not.

    Parameters:
        game_id: game id to join the game

    Responses:
        422: Error response in case request with valid request 
            but unprocessable
        400: Error response in case invalid request data
    """
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
    """Create a new move.

    This function performs following actions:

    (1) If moves data for the game is empty in the document then add this move for round 1.
    (2) If moves data already exist in the document then 
        determine if the last round has 2 moves. 
        If True:
            then add the move to the new round, 
        else 
        (i) add the move to the last round & 
        (ii) increment the round by 1 &
        (iii) determine winner for the round
    
    (3) Set game status to finished if:
        (i) rounds has reached to MAX rounds &
        (ii) last round has both players moves
        (iii) and there's no tie between both players
        else the game will continue
    
    Parameter:
        kargs: keyword args
    
    Returns:
        updated_fields: data to update db 
    """     
    # Initialize variables
    winner = None
    game_status = "in_progress"
    round_finished = False
    updated_fields = {}

    # Extract Kargs
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