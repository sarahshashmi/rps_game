# Rock Paper Scissor Game API

## Introduction

The API implements the backend for a Rock Paper Scissors game.

## Features

- A single game can be played between 2 players only.
- System allows multiple pair of players to play the games at the same time.
- The game has unique game_id. The player who creates a new game becomes player_1 in the system. 
Another user who joins the game with the game_id becomes player_2. 
- The game can only be started when both the players join the game. Meaning, the `\play\<move>` endpoint can only be accessed when game has both the players in DB.
- Only player_1 can make the first move and subsequent moves are made turn wise. API doesn't allow player_1 to make the move when it's player_2 turn and vice versa.
- The game has a minimum of 3 rounds. By the end of the 3rd round, the game finishes if there's no tie between both players. Otherwise, the game will continue until there's a winner, incrementing the rounds by 1.
- Once the game is finished, winner name is returned and players can't make the moves anymore.
- The API also facilitates to show all the winner scores. The endpoint returns the no. of won games per user in descending order.

## Design

The API is implemented in `Flask` framework and backed by `MongoDB` database.
Flask extension `Flask-JWT-Extended` is used for authentication purpose.

The API has following 4 endpoints:

- `POST` : `\create_game` : A player can create a game & becomes player_1
- `POST` : `\join_game/<game_id>`: Any player can join the game provided the game_id & becomes player_2
- `POST` : `\play/<move>`: Both the players can make their moves until max round is reached 
- `GET`  : `\get_high_scores`: Games won per player can be shown by accessing this route

API documentation can be found here [here](https://documenter.getpostman.com/view/19594912/VUqmuJPz)


## Installation

- Install Mongodb version v5.0.6
- The service requires Python3.
- To get started, create a virtual environment using Python3 and activate it.
- Then, install the requirements using `pip install -r requirements.txt`

## Getting Started

   - Activate the virtual environment before running command
   - Run the API via `python run.py`.
   - The app can be accessed at `http://127.0.0.1:5000/`

## Extension Points

- [ ] Add tests
- [ ] Add logging
- [ ] Add typehinting
- [ ] Try socket.io
- [ ] Add models
- [ ] Add unique username validation on DB level
- [ ] Create generic response object
- [ ] Improvise API documentation
- [ ] Dockerize the app
