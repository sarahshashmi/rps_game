"""Import packages."""
from distutils.command.config import config
from flask import request, Blueprint
from flask.json import jsonify
import json
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from rps_app import db
from config import Config
from rps_app.services.games import create_new_game
from rps_app.services.games import verify_joining
from rps_app.services.games import create_move

games_blueprint = Blueprint('games', __name__)

@games_blueprint.route("/create_game", methods=["POST"])
def create_game():
    """Endpoint for client to Create a new game.

    This endpoint allows clients to create a new game.
    A unique 4 char game_id is randomly generated for the game.
    User accessing this endpoint will become player_1.
    A new game record is inserted into the DB and 
    a JWT access token is generated for the user.

    Parameters:
        username: name of the user who creates the game

    Responses:
        201: Success response with json data
                containing JWT access_token & generated game_id
        400: Error response in case invalid request data
    """
    try:
        # Extract query parameters
        post_data = json.loads(request.data)
        username = post_data.get('username')
        if not username:
            return jsonify({"error":"missing username"}), 400
        
        # Create a new game
        game_id = create_new_game()

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

@games_blueprint.route("/join_game/<game_id>", methods=["POST"])
@verify_joining()
def join_game(game_id):
    """Endpoint for client to join an existing game.

    This endpoint allows clients to join existing game
    game_id is part of the endpoint

    Parameters:
        username: name of the user who creates the game

    Responses:
        201: Success response with json data
             containing JWT access_token & generated game_id
        400: Error response in case invalid request data
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

@games_blueprint.route("/play/<move>", methods=["POST"])
@jwt_required()
def play(move):
    """Endpoint for client to make a move.
    
    This endpoint allows clients to make moves for existing game.
    move is part of the endpoint.

    Responses:
        201: Success response with json data
        400: Error response in case invalid request data
        422: Error response in case request with valid request 
            but unprocessable
    """    
    try:
        # Return error response if provided move is invalid
        if move.lower() not in Config.VALID_MOVES:
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
            return jsonify({"error": "bad requestff"}), 400
  
        # Return error response if user other than player1 
        # or player2 accesses this endpoint
        if username not in [doc['player_1']['name'], doc['player_2']['name']]:
            return jsonify({"error": "bad requestaa"}), 422

        # Return error response if the user doesn't have turn yet
        if doc['last_move_by'] is None and doc['player_1']['name'] != username or\
            doc['last_move_by'] == username:
            return jsonify({"error": "wait for opponent's move"}), 422
    
        # create move data and insert move to DB
        args= {"username":username, "game_id":game_id, "move":move, "doc": doc}
        data = create_move(**args)
        db.game.update_one({"game_id": game_id}, {"$set": data})

        # Return success response
        response_data = {"winner": data["winner"], "status": data["status"]}
        return jsonify(response_data), 201

    except Exception as e:
        return jsonify({'message': 'bad requestsyyy'}), 400

@games_blueprint.route("/get_high_scores", methods=["GET"])
@jwt_required()
def get_high_scores():
    """Endpoint for client to get winner scores.
    
    This endpoint allows clients get the scores for winners.
    The scores are shown on the basis of no. of games won per user in descending order

    Responses:
        200: Success json response with scores of winners i.e.
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