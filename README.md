# Rock Paper Scissor Game API

## Introduction

The API implements the backend for a Rock Paper Scissors game.

## Features

- A single game can be played between 2 players only but multiple players can play the games at the same time. 
- No 2 players can have same names in a single game.
- The game has unique game_id. The player who creates a new game becomes player1 in the system. 
Another user who joins the game with the game_id becomes player2. 
- The game can only be started when both the players join the game. Meaning, the `\play\<move>` endpoint can only be accessed when game has both the players in DB.
- Only player1 can make the first move and subsequent moves are made turn wise. API doesn't allow player1 to make the move when it's player2 turn and vice versa.
- The game has maximum 5 rounds if there's no tie between both players. Otherwise, the game will contintue.
- Once the game is finished, winner name is returned and players can't make the moves anymore.
- The API also facilitates to show all the winner scores. Here score means, if playerA won 5 games and playerB has won 1 game then 5 & 1 are the scores that will be shown in descending order per user.

## Design

The API is implemented in Flask framework and backed by MongoDB database.
Flask-JWT-Extended is used for authentication purpose.

The API has following 4 endpoints:

- `POST` : `\create_game` : A player can create a game & becomes player1
- `POST` : `\join_game/<game_id>`: Any player can join the game provided the game_id
- `POST` : `\play/<move>`: Both the players can make their moves until max round is reached 
- `GET`  : `\get_high_scores`: Games won per player can be shown by accessing this route

API documentation can be found <here>

## Installation

- Install Mongodb version v5.0.6
- The service requires Python3.
- To get started, create a virtual environment using Python3 and activate it.
- Then, install the requirements using `pip install -r requirements.txt`

## Getting Started

   - Activate the virtual environment before running command
   - Run the API via `python app.py`.
   - The app can be accessed at `http://127.0.0.1:5000/`

## Extension Points

- [ ] Add tests
- [ ] Add logging
- [ ] Add typehinting
- [ ] Add missing comments, docstring
- [ ] Restructure project. Separate out modules including views, models, tests
- [ ] Add config for different environments & execution modes
- [ ] Create separate file for env variables
- [ ] Try socket.io
- [ ] Add API documentation
