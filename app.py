from flask import Flask, request
from flask.json import jsonify
import json
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from functools import wraps
from datetime import timedelta
import random
import string

# Create Flask object
app = Flask(__name__)

# Configuration setup
# TODO: CREATE A .env FILE AND STORE IN IT

# Define constants
ACCESS_EXPIRES = timedelta(hours=1)
MAX_ROUNDS = 5
VALID_MOVES = ['rock', 'scissor', 'paper']

# S the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = 'thisismysecret' #change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES

# Setup database 
app.config["MONGO_URI"] = "mongodb://localhost:27017/rps_database"
mongodb_client = PyMongo(app)
db = mongodb_client.db

# Creates JWT object
jwt = JWTManager(app)

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

@app.route("/create_game", methods=["POST"])
def create_game():
    """This endpoint allows clients to create a new game.
    A unique 4 char game_id is randomly generated for the game.
    User accessing this endpoint will become player_1.
    A new game record is inserted into the DB and 
    a JWT access token is generated for the user.

    Parameters:
    * username -> name of the user who creates the game

    Responses:
    * 201 -> Success response with json data
             containing JWT access_token & generated game_id
    * 400 -> Error response in case invalid request data
    """
    try:
        # Extract query parameters
        post_data = json.loads(request.data)
        username = post_data.get('username')
        if not username:
            return jsonify({"error":"missing username"}), 400
        
        # Generate new game id
        game_id = generate_game_id()

        # Insert new record in game collection against generated unique game id
        db.game.insert_one({"game_id": game_id, "player_1": {"name": username, "score": 0}, \
                            "last_move_by": None, "round": 0, "round_finished": False, \
                            "round_moves": {}, 'status': 'new', 'winner': None})

        # Create JWT access token with user identity for and game_id as part of additional claims
        additional_claims = {"game_id": game_id}
        access_token = create_access_token(identity=username, additional_claims=additional_claims)

        # Return success response with json data
        # containing JWT access_token & generated game_id
        return jsonify(access_token=access_token, game_code=game_id), 201
    except:
        return jsonify({'message': 'bad request'}), 400

@app.route("/join_game/<game_id>", methods=["POST"])
@verify_joining()
def join_game(game_id):
    """This endpoint allows clients to join existing game
    game_id is part of the endpoint

    Parameters:
    * username -> name of the user who creates the game

    Responses:
    * 201 -> Success response with json data
             containing JWT access_token & generated game_id
    * 400 -> Error response in case invalid request data
    """
    try:
        # Extract query parameters
        post_data = json.loads(request.data)
        username = post_data.get('username')        
        db.game.update_one({"game_id": game_id}, {'$set':{'player_2': {'name': username, "score": 0}, 'status': 'started'}})

        # Create JWT access token with user identity for and game_id as part of additional claims
        additional_claims = {"game_id": game_id}
        access_token = create_access_token(identity=username, additional_claims=additional_claims)

        # Return success response with json data
        # containing JWT access_token & message
        return jsonify(access_token=access_token, message="Wait for player1 move..."), 201
    except:
        return jsonify({'message': 'Bad request'}), 400

@app.route("/play/<move>", methods=["POST"])
@jwt_required()
def play(move):
    """This endpoint allows clients to make moves for existing game.
    move is part of the endpoint.

    Responses:
    * 201 -> Success response with json data
    * 400 -> Error response in case invalid request data
    * 422 -> Error response in case request with valid request but unprocessable
    """    
    try:
        # Return error response if provided move is invalid
        if move.lower() not in VALID_MOVES:
            return jsonify({"error": "invalid move"}), 400

        # Extract JWT claims
        claims = get_jwt()
        username = get_jwt_identity()
        game_id=claims['game_id']

        # Return error resonse if JWT claims don't have game_id or username
        if not game_id or not username:
            return jsonify({"error": "bad request"}), 400

        # Return error response if provided game_id doesn't exist
        doc = db.game.find_one({"game_id": game_id})
        if not doc:
            return jsonify({"error": "game doesn't exist"}), 422
        
        # Return error response if this game is already finised
        if doc['status'] == "finished":
            return jsonify({"error": "bad request"}), 400

        # Get document fields
        last_move_by = doc['last_move_by']
        player_1 = doc['player_1']
        player_2 = doc['player_2']
        round = doc['round']
        round_moves = doc['round_moves']
        p1_score = player_1['score']
        p2_score = player_2['score']

        # Return error response 
        # if user other than player1 & player2 accesses this endpoint
        if username not in [player_1['name'], player_2['name']]:
            return jsonify({"error": "bad request"}), 422

        # Initialize variables
        updated_fields = {}
        winner = None
        game_status = "in_progress"
        round_finished = False

        # Return error response if the user doesn't have turn yet
        if last_move_by is None and player_1['name'] != username or\
            last_move_by == username:
            return jsonify({"error": "wait for opponent's move"}), 422

        # If moves for the game already exist in the table then
        # either add this move for player_2 against existing round
        # or create a new round entry for player_1 with this move
        # Also, determine winner for the round if both players moves exist
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
                        winner = player_1["name"]
                        p1_score += 1
                        updated_fields["player_1.score"] = p1_score
                    else:
                        winner = player_2["name"]
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
        if round_finished and round-1 >= MAX_ROUNDS:
            if p1_score != p2_score:
                game_status = "finished"
                if p1_score > p2_score:
                    winner = player_1['name']
                else:
                    winner = player_2['name']

        # update game collection/table
        updated_fields.update({"round": round, 
                        "round_moves": round_moves, 
                        "last_move_by": username, 
                        "status": game_status,
                        "winner": winner, 
                        "round_finished": round_finished})

        db.game.update_one({"game_id": game_id}, {"$set": updated_fields})

        # Return success response
        response_data = {"winner": winner, "status": game_status}
        return jsonify(response_data), 201

    except:
        return jsonify({'message': 'bad requests'}), 400

@app.route("/get_high_scores", methods=["GET"])
@jwt_required()
def get_high_scores():
    """This endpoint allows clients get the scores for winners.
    The scores are shown on the basis of no. of games won per user in descending order

    Responses:
    * 200 -> Success json response with scores of winners i.e.
            (total games won per user)
    """
    response_data = {}

    # Aggregate winner documents/rows if game status is finished
    cursor = db.game.aggregate([{"$match": {"status": "finished"}},
                                 {"$group": {"_id":"$winner", "count":{"$sum":1}}},
                                 {"$sort": {"count": 1}}
                                 ])
    if cursor:
        for data in cursor:
            winner = data["_id"]
            games_won = data["count"]
            response_data[winner] = games_won

        # Sort the response by value in descending order
        response_data = dict(sorted(response_data.items(), key=lambda item: item[1], reverse=True))

    # Return response
    return jsonify(response_data=response_data), 200

if __name__ == '__main__':
    # create indexes
    db.game.create_index([("game_id", 1)], unique=True)
    db.game.create_index([("status", 1)])
    
    app.run(debug=True)