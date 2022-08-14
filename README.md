# Rock Paper Scissor Game API

## Introduction

This API implements the backend for a Rock Paper Scissors game.

### Tasks
- A single game can include multiple rounds
- It should be possible for multiple pair of players to play games at the same time
- The backend should check whether a move is actually possible and report a failure if it is not
- Some basic authentication mechanism should work and endpoints should be checked against it (i.e. if it’s Player1’s turn, Player2 should not be able to make the move)
- Assume that the frontend polls about updates, i.e. it manually checks the API regularly if there are any updates (i.e. the other player has made a move, if a game has been finished, etc.)
- The won games should be stored per user and there should be an API endpoint to get a high score list

## Design

The API has following 4 endpoints:

`POST` : `\create_game` 
`POST` : `\join_game/<game_id>`
`POST` : `\play/<move>`
`GET`  : `\get_high_scores`

The API is backed by a MongoDB database.

## Getting Started

Install Mongodb version v5.0.6

This service requires Python3. To get started, create a virtual environment using Python3.

Then, install the requirements using `pip install -r requirements.txt`.

Finally, run the API via `python app.py`.

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