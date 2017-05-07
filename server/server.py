from flask import Flask
from flask import request
from flask import jsonify
from pprint import pprint
from random import choice
import json
import random
from database_client import DatabaseClient, get_current_epoch_datetime
from bson.objectid import ObjectId
import pymongo

# These remain constant throughout every game
TILE_UNKNOWN = 0
TILE_HIT = 1
TILE_MISS = 2

app = Flask(__name__)
db = DatabaseClient()

def get_auth_error_json():
    """Return the authention error (JSON format)"""
    return jsonify({"status" : "error", "error-id": 5, "description": "Invalid auth key."})

def get_other_player(current_player, player_list):
    """Return the name of the opponent of the given player, given the current player and the list of both players"""
    return player_list[1] if current_player == player_list[0] else player_list[0]

def get_player_id(player_name):
    """Return the player id (as an ObjectId), given the player name"""
    player_data = db.get_objects("players", {"name":player_name})
    for data in player_data:
        if data['name'] == player_name:
            return data["_id"]

def generate_auth_key():
    """Generate and return key used to authenticate players"""
    return str(random.getrandbits(128))

def player_authenticate(player_name, auth_key):
    """Check whether the given authentication key corresponds to the saved one"""
    player_id = get_player_id(player_name)
    player = db.get_object_by_id("players", player_id)
    if player is None:
        return False
    if player['key'] == auth_key:
        return True
    else:
        return False

def game_change_state(game_id, game_state):
    """Change the state of a game"""
    game_data = db.get_object_by_id("games", ObjectId(game_id))
    game_data["state"] = game_state
    db.update_object_by_id("games", ObjectId(game_id), game_data)
    return True

def check_if_game_won(game_id_obj):
    """Loads data on the game from file, and checks to see if either player has hit all of the ships of the other player.
    If they have, it updates the save file to say the game is done and who the winner is.
    It also updates the player's statistics data.
    It returns a tuple of (boolean:game_won, string:game_winner)
    If the game is not won yet the game_winner field should read None (python) or null (JSON)"""

    # Get game data from the database
    game = db.get_object_by_id("games", game_id_obj)
    player_data = game["players"]
    player_list = player_data.keys()

    # Initialise variables
    game_finished = False
    winning_player = None
    losing_player = None

    # Loop through the two players and check if someone won
    for curr_player in player_list:
        other_player = get_other_player(curr_player, player_list)

        # Assume the player has won, and try to find a square for which that isn't the case
        player_won = True
        for y in xrange(len(player_data[curr_player]["visible_board"])):
            for x in xrange(len(player_data[curr_player]["visible_board"][0])):
                # Check if there is any square on the board that has a ship but has not been hit
                if(player_data[other_player]["ships"][x][y] and player_data[curr_player]["visible_board"][x][y] != TILE_HIT):
                    player_won = False
                    break

            if not player_won:
                break

        if player_won:
            game_finished = True
            winning_player = curr_player
            losing_player = other_player
            break

    if game_finished:
        # Update the game data with information on who won
        game["winner"] = winning_player
        game["done"] = game_finished
        db.update_object_by_id("games", game_id_obj, game)

        # Get player data of the winning player
        winner_id = get_player_id(winning_player)
        winner_data = db.get_object_by_id("players", winner_id)

        # Get stats data of the winning player
        winner_stats = {}
        if "stats" in winner_data:
            winner_stats = winner_data["stats"]

        # Increment the number of games the winning player has finished
        if "games_finished" in winner_stats:
            winner_stats["games_finished"] = winner_stats["games_finished"]+1
        else:  
            winner_stats["games_finished"] = 1

        # Increment the number of games the winning player has won
        if "games_won" in winner_stats:
            winner_stats["games_won"] = winner_stats["games_won"] + 1
        else:
            winner_stats["games_won"] = 1

        # Update the database with the stats information of the winning player
        winner_data["stats"] = winner_stats
        db.update_object_by_id("players", winner_id, winner_data)

        # Get player data of the losing player
        loser_id = get_player_id(losing_player)
        loser_data = db.get_object_by_id("players", loser_id)

        # Get stats data of the losing player
        loser_stats = {}
        if "stats" in loser_data:
            loser_stats = loser_data["stats"]

        # Increment the number of games the losing player has finished
        if "games_finished" in loser_stats:
            loser_stats["games_finished"] = loser_stats["games_finished"] + 1
        else:
            loser_stats["games_finished"] = 1

        # Update the database with the stats information of the losing player
        loser_data["stats"] = loser_stats
        db.update_object_by_id("players", loser_id, loser_data)

    return (game_finished, winning_player)

@app.route('/game/<string:game_id_str>/<string:player_name>/<string:auth_key>')
def game(game_id_str, player_name, auth_key):
    """Get metadata about the game"""

    if not player_authenticate(player_name, auth_key):
        return get_auth_error_json()

    # Get game data from the database and assign it to variables
    game = db.get_object_by_id("games", ObjectId(game_id_str))
    name = game['name']
    players = game["players"]
    player_names = []
    for player in players:
        player_names.append(player)
    game_finished = game["done"]
    game_winner = game["winner"]

    return jsonify({"status" : "ok", "name" : name, "players": player_names, "done" : game_finished, "winner": game_winner})

@app.route('/game/new/<string:player_name>/<string:player2_name>/<string:auth_key>')
def game_new(player_name, player2_name, auth_key):
    """Start a new game"""

    if not player_authenticate(player_name, auth_key):
        return get_auth_error_json()

    # Create the game object and assign values to it
    game = {}
    game["name"] = "Game: " + player_name + " vs. " + player2_name
    game["done"] = False
    game["winner"] = None
    game["turn"] = choice([player_name, player2_name])
    game["start_datetime"] = get_current_epoch_datetime()
    game["state"] = 1
    game["ships_placed"] = [0, 0, 0, 0, 0]

    player_data = {}
    for player in [player_name, player2_name]:
        player_data[player] = {}

        # Construct the ship array
        ship_array = list()
        for x in xrange(10):
            col = list()
            for y in xrange(10):
                col.append(choice([True, False]))
            ship_array.append(col)
        player_data[player]["ships"] = ship_array

        # Construct the visible board array
        visible_board = []
        for x in xrange(10):
            col = []
            for y in xrange(10):
                col.append(0)
            visible_board.append(col)
        player_data[player]["visible_board"] = visible_board

    # Update the database with information on the new game
    game["players"] = player_data
    game_id_obj = db.add_object("games", game)

    for name in [player_name, player2_name]:
        # Get player data from the database
        player_id = get_player_id(name)
        player_data = db.get_object_by_id("players", player_id)

        # Return error if player doesn't exist
        if player_data is None:
            return jsonify({"status": "error", "error-id": 6, "description": "Opponent player does not exist."})

        if('active_games' in player_data):
            # Check if the palyer has a list of active games in their info
            player_data['active_games'].append(game_id_obj)
        else:
            # Create a new list of active games with this new game in it
            player_data['active_games'] = [game_id_obj]

        # Update the database with the new player information
        db.update_object_by_id("players", player_id, player_data)

    return jsonify({"status" : "ok", "players": [player_name, player2_name], "turn" : game["turn"], "game_id": str(game_id_obj)})

@app.route('/game/<string:game_id_str>/get_turn/<string:player_name>/<string:auth_key>')
def game_get_turn(game_id_str, player_name, auth_key):
    """Check whose turn it is"""

    if not player_authenticate(player_name, auth_key):
        return get_auth_error_json()

    # Get game data from the database
    game = db.get_object_by_id("games", ObjectId(game_id_str))
    turn = game['turn']

    return jsonify({"status" : "ok", "turn": turn})

@app.route('/game/<string:game_id_str>/get_board/<string:player_name>/<string:auth_key>')
def game_get_board(game_id_str, player_name, auth_key):
    """Get the state of the game: your shots, your ship locations, and your opponent's shots"""

    if not player_authenticate(player_name, auth_key):
        return get_auth_error_json()

    # Get game data from the database
    print "Game board requested for game " + game_id_str + "/" + str(player_name)
    game = db.get_object_by_id("games", ObjectId(game_id_str))
    players_data = game['players']

    # Create a response object which includes the visible board of a player
    response = {}
    response[player_name] = players_data[player_name]
    opponent_id = get_other_player(player_name, players_data.keys())
    response[opponent_id] = {}
    response[opponent_id]["visible_board"] = players_data[opponent_id]["visible_board"]

    return jsonify({"status" : "ok", "data" : response})

@app.route('/game/<string:game_id_str>/make_shot/<string:player_name>/<int:x>/<int:y>/<string:auth_key>')
def game_make_shot(game_id_str, player_name, x, y, auth_key):
    """Updates the game with a new shot for a given player, and checks to see if it's a hit or not.
    Triggers a check to see if they have won or not.
    Checks to see if it's actually their turn and if their shot is valid and has not been tried already.
    Returns whether or not their shot hit an enemy battleship"""

    if not player_authenticate(player_name, auth_key):
        return get_auth_error_json()

    print "Player " + str(player_name) + " making shot in game #" + game_id_str + " at pos " + str(x) + ", " + str(y)

    # Get game data from the database
    game_data = db.get_object_by_id("games", ObjectId(game_id_str))
    game_state = game_data["state"]

    # Check if the game is in the ship placing state
    if game_state != 2:
        return jsonify({"status": "error", "type": "ships-not-placed"})

    current_turn = game_data["turn"]

    if(game_data["done"]):
        return jsonify({"status" : "error", "error-id": 3, "description" : "Game already finished."})
    if(current_turn != player_name):
        return jsonify({"status" : "error", "error-id": 2, "description" : "Other player's turn."})

    player_board = game_data["players"][player_name]["visible_board"]

    # Check if coordinates are within index and if that shot was already made
    if(x < 0 or y < 0 or x >= len(player_board) or y >= len(player_board[0])):
        return jsonify({"status" : "error", "error-id": 1, "description" : "List index out of bounds."})
    if(player_board[x][y] != TILE_UNKNOWN):
        return jsonify({"status" : "error", "error-id": 0, "description" : "Already made a shot in this location."})
    
    
    # Get the name of the opponent player and then get their ship locations
    opponent_player_name = get_other_player(player_name, game_data["players"].keys())
    opponent_data = game_data["players"][opponent_player_name]

    # Check if there is a ship in that location, either True or False
    hit = opponent_data["ships"][x][y]

    # Update the player's view of the game (visible board)
    player_board[x][y] = TILE_HIT if hit else TILE_MISS

    # Assign the new board and new turn info to game data
    game_data["players"][player_name]["visible_board"] = player_board
    game_data["turn"] = opponent_player_name
    print "It is now " + str(opponent_player_name) + "'s turn"

    # Update the database with the new player information
    db.update_object_by_id("games", ObjectId(game_id_str), game_data)

    # Check if the game has been won
    check_if_game_won(ObjectId(game_id_str))

    return jsonify({"status": "ok", "hit" : hit})


@app.route('/game/<string:game_id_str>/place_ship/<string:player_name>/<string:ship_length>/<string:ship_direction>/<int:x>/<int:y>/<string:auth_key>')
def game_place_ship(game_id_str, player_name, ship_length, ship_direction, x, y, auth_key):
    """Place a ship of a type at coordinates"""

    if not player_authenticate(player_name, auth_key):
        return get_auth_error_json()

    # Get game data from the database
    game_data = db.get_object_by_id("games", ObjectId(game_id_str))

    game_state = game_data["state"]

    # Check if game is in the ship placing state
    if game_state != 1:
        return jsonify({"status": "error", "error-id" : 7, "description": "ships-placed"})

    # Get id of the oponent
    players_data = game_data['players']
    opponent_id = get_other_player(player_name, players_data.keys())

    ships = game_data["players"][player_name]["ships"]
    ships_placed_opponent = game_data["players"][opponent_id]["ships_placed"]
    ships_placed = game_data["players"][player_name]["ships_placed"]
    board_size = 10
    state = 2

    # Check to see if ship of a given length can be placed
    if ships_placed[ship_length] == int(float(board_size)/ship_length):
        return jsonify({"status": "error", "error-id":8, "description":"No more ships of this length can be placed"})

    # Check to see if the ship can be placed
    if x > board_size - 1 or x < 0 or y > board_size - 1 or y < 0:
        return jsonify({"status": "error", "error-id":9, "description":"Ship out of bounds"}) # Top-left segment of ship outside board
    if ship_direction == 0:
        if y + ship_length - 1 > board_size:
            return jsonify({"status": "error", "error-id":9, "description":"Ship out of bounds"}) # Ship outside board (horizontally)
    if ship_direction == 1:
        if x + ship_length - 1 > board_size:
            return jsonify({"status": "error", "error-id":9, "description":"Ship out of bounds"}) # Ship outside board (vertically)
    for i in range(0, ship_length):
        if ship_direction == 0:
            if ships[y+i] == True:
                return jsonify({"status": "error", "error-id":10, "description":"Ship already in this position."}) # Ship already there
        if ship_direction == 1:
            if ships[x+i] == True:
                return jsonify({"status": "error", "error-id":10, "description":"Ship already in this position."}) # Ship already there

    # Place the ship
    for i in range(0,ship_length):
        if ship_direction == 0:
            game_data["players"][player_name]["ships"][y+i] = True
        if ship_direction == 1:
            game_data["players"][player_name]["ships"][x+i] = True

    # Update the record of ships that have been placed
    ships_placed[ship_length] += 1
    game_data["players"][player_name]["ships_placed"] = ships_placed

    # Check if all ships of player have been placed and if so, change the state of the game
    for i in range(1,5):
        if ships_placed[i] < int(float(board_size)/i):
            state = 1

    # Check if all ships of oponent have been placed and if so, change the state of the game
    for i in range(1,5):
        if ships_placed_opponent[i] < int(float(board_size)/i):
            state = 1

    if state == 2:
        game_change_state(game_id, 2)

    # Save the new data to database
    db.update_object_by_id("games", ObjectId(game_id), game_data)

    return jsonify({"status": "ok"})

@app.route('/player/login/<string:player_name>/<string:player_password>')
def player_login(player_name, player_password):
    """Check if the given name and password corresponds to the saved one and return the authentication key"""
    
    # Get player data from the database
    player_id = get_player_id(player_name)
    player = db.get_object_by_id("players", player_id)

    if player is None:
        # If player doesn't exist, create a new player
        auth_key = generate_auth_key()
        new_player = {
            "name": player_name,
            "password":player_password, 
            "active_games":[],
            "stats":{"games_finished":0, "games_won":0}, 
            "key":auth_key
        }
        db.add_object("players", new_player)
        return jsonify({"status":"ok", "new_player":True, "key":auth_key})

    # Check if the given password mathes the one in the database
    if player['password'] == player_password:
        # If so, generate new authentication key, put it in the database and return it to the client
        auth_key = generate_auth_key()
        player['key'] = auth_key
        db.update_object_by_id("players", player_id, player)
        return jsonify({"status" : "ok", "new_player" : False, "key" : auth_key})
    else:
        return jsonify({"status":"error", "error-id" : 4, "description" : "Incorrect password."})

@app.route('/player/<string:player_name>/get_games/<string:auth_key>')
def player_get_games(player_name, auth_key):
    """Get a list of all active games of a player"""

    if not player_authenticate(player_name, auth_key):
        return get_auth_error_json()

    # Get player data from the database
    player_id_obj = get_player_id(player_name)
    player_data = db.get_object_by_id("players", player_id_obj)

    if player_data is None:
        return jsonify({"status" : "ok", "active_games": []})
    active_game_id_objs = player_data["active_games"]

    # The game ids are all stored as IdObjects rather than strings,
    # We want to return them as strings so they can be parsed by the client more easily
    active_game_id_strs = []

    # Construct the list of active games
    for id_obj in active_game_id_objs:
        active_game_id_strs.append(str(id_obj))

    return jsonify({"status":"ok", "active_games": active_game_id_strs})

@app.route('/player/<string:player_name>/get_stats/<string:auth_key>')
def player_get_stats(player_name, auth_key):
    """Get stats of a player"""

    if not player_authenticate(player_name, auth_key):
        return get_auth_error_json()

    # Get player data from the database
    player_id_obj = get_player_id(player_name)
    player_data = db.get_object_by_id("players", player_id_obj)
    player_stats = player_data["stats"]
    
    return jsonify({"status":"ok", "stats" : player_stats})

@app.route('/public/leaderboard')
def public_leaderboard():
    # Construct the leaderboard array from the players info in the database sorted by the number of games won
    players = db.get_objects("players", {"stats": {"$exists": True, "$ne": {}}}).sort("stats.games_won", pymongo.DESCENDING)
    results = []
    position = 1

    # Format the leadeboard array
    for player in players:
        results.append({"name" : player["name"], "games_finished:" : player["stats"]["games_finished"], "games_won": player["stats"]["games_won"], "position":position})
        position += 1

    return jsonify({"status":"ok", "leaderboard":results})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
