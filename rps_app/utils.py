"""Import packages."""
import random, string
from config import Config

def generate_game_id():
    """Return randomly generated id."""
    game_id = ''.join(random.choices(string.ascii_lowercase, k=Config.GAME_STRING_LENGTH))
    return game_id

def determine_winner(p1_move, p2_move):
    """Return player_1 or player_2.

    Return player_1 if player_1 move wins over player_2
    else return player_2
    """
    if p1_move == "rock" and p2_move == "scissor":
        return("player_1")
    elif p1_move == "scissor" and p2_move == "paper":
        return("player_1")
    elif p1_move == "paper" and p2_move == "rock":
        return("player_1")
    return("player_2")