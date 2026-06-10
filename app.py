# app.py
import numpy as np
import copy
from flask import Flask, render_template, request, jsonify
from gamelogic import HavannahGameLogic
from helper import get_random_board
from players.ai import AIPlayer
from players.random import RandomPlayer

app = Flask(__name__)

games = {}

@app.route('/')
def index():
    """Serves the main game page (index.html)."""
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    data = request.json
    mode = data.get('mode', 'human_vs_ai')
    dim = int(data.get('dim', 4))
    
    initial_board = get_random_board(dim, 0)
    game_logic = HavannahGameLogic(board_state=copy.deepcopy(initial_board), layers=dim)
    
    game_id = "game_" + str(len(games) + 1)
    
    ai_player = None
    if mode == 'human_vs_ai':
        ai_player = AIPlayer(player_number=2, timer=[60, 60])
    elif mode == 'human_vs_random':
        ai_player = RandomPlayer(player_number=2, timer=[60, 60])
    # For 'human_vs_human', ai_player remains None, which is correct.

    games[game_id] = {
        'logic': game_logic,
        'mode': mode,
        'initial_board': initial_board,
        'ai_player': ai_player
    }
    
    response = game_logic.get_game_state_json()
    response['gameId'] = game_id
    
    return jsonify(response)

@app.route('/api/reset_game', methods=['POST'])
def reset_game():
    """Resets the game to its initial state."""
    game_id = request.json.get('gameId')
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404

    game_session = games[game_id]
    
    game_session['logic'] = HavannahGameLogic(
        board_state=copy.deepcopy(game_session['initial_board']),
        layers=game_session['logic'].layers
    )

    return jsonify(game_session['logic'].get_game_state_json())


@app.route('/api/make_move', methods=['POST'])
def make_move():
    data = request.json
    game_id = data.get('gameId')
    move = tuple(data.get('move'))

    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404

    game_session = games[game_id]
    game = game_session['logic']
    ai_player = game_session['ai_player']
    
    if not game.make_move(move):
        return jsonify({'error': 'Invalid move', **game.get_game_state_json()}), 400

    if game.game_over:
        return jsonify(game.get_game_state_json())

    # This logic now correctly handles all modes.
    # If ai_player is None (like in human_vs_human), this block is skipped.
    if ai_player and not game.game_over:
        ai_move = ai_player.get_move(game.state)
        game.make_move(ai_move)

    return jsonify(game.get_game_state_json())


import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
