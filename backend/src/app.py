# backend/src/app.py
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, send
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

# Initialize games pool
games_pool = {}

# Helper function to check for a winner
def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] != ' ':
            return row[0]

    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != ' ':
            return board[0][col]

    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]

    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]

    return None

# Route to start a new game or join an existing one
@app.route('/join_game', methods=['POST'])
def join_game():
    player_name = request.json['player_name']
    # print(player_name)

    # Check if there are available games in the pool
    if not games_pool:
        game_id = 1
        game_state = {
            'board': [[' ' for _ in range(3)] for _ in range(3)],
            'player1': player_name,
            'player2': None,
            'current_player': player_name,
            'winner': None,
            'game_over': False
        }
        games_pool[game_id] = game_state
    else:
        # Try to assign the player to an existing game
        game_assigned = False
        for game_id, game_state in games_pool.items():
            if game_state['player2'] is None:
                game_state['player2'] = player_name
                game_state['current_player'] = game_state['player1']  # Player1 starts the game
                game_assigned = True
                break
        
        # If all games are full, create a new game
        if not game_assigned:
            game_id = max(games_pool.keys()) + 1
            game_state = {
                'board': [[' ' for _ in range(3)] for _ in range(3)],
                'player1': player_name,
                'player2': None,
                'current_player': player_name,
                'winner': None,
                'game_over': False
            }
            games_pool[game_id] = game_state
    # print(games_pool)
    return jsonify({'message': 'Joined game successfully', 'game_id': game_id, 'current_player': game_state['current_player']})

# Route to make a move
@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.json
    game_id = data['game_id']
    player_name = data['player_name']
    row = data['row']
    col = data['col']
    game_id = int(game_id)
    game_state = games_pool.get(game_id)
    print(game_state)
    # if second player is not joined
    if not game_state:
        return jsonify({'message': 'Game not found. Please join a game first.'}), 400

    if not game_state['player2']:
            return jsonify({'message': 'Waiting for the second player to join.'}), 400

    if game_state['game_over']:
        return jsonify({'message': 'The game is already over.'}), 400

    if player_name != game_state['current_player']:
        return jsonify({'message': 'It is not your turn. You are player ' + player_name + ' and the turn belongs to ' + game_state['current_player']}), 400

    if game_state['board'][row][col] != ' ':
        return jsonify({'message': 'Invalid move. The cell is already taken.'}), 400

    if player_name == game_state['player1']:
        marker = 'X'
        game_state['current_player'] = game_state['player2']
    else:
        marker = 'O'
        game_state['current_player'] = game_state['player1']

    game_state['board'][row][col] = marker
    winner = check_winner(game_state['board'])
    if winner:
        game_state['winner'] = winner
        game_state['game_over'] = True
        return jsonify({'message': f'Player {winner} wins!', 'winner': winner})

    if all([cell != ' ' for row in game_state['board'] for cell in row]):
        game_state['game_over'] = True
        return jsonify({'message': 'It\'s a draw!'})

    # Send message to other player
    other_player = 'player1' if games_pool[game_id]['player1'] != player_name else 'player2'
    send({'row': row, 'col': col}, room=games_pool[game_id][other_player])

    return jsonify({'message': 'Move made', 'current_player': game_state['current_player']})

# Route to get the current game state
@app.route('/get_game_state/<int:game_id>', methods=['GET'])
def get_game_state(game_id):
    game_state = games_pool.get(game_id)
    if not game_state:
        return jsonify({'message': 'Game not found.'}), 400
    return jsonify(game_state)

# WebSocket event handler for new connections
@socketio.on('connect')
def handle_connect():
    print('Client connected')

# WebSocket event handler for disconnects
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    app.debug = True
    socketio.run(app, port=8081)
