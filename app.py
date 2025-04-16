from flask import Flask, render_template, request, jsonify
import pickle
import os

app = Flask(__name__)

# Load Q-table if exists
Q = {}
if os.path.exists("q_table.pkl"):
    with open("q_table.pkl", "rb") as f:
        Q = pickle.load(f)

class TicTacToe:
    def __init__(self):
        self.board = [' '] * 9
        self.done = False
        self.winner = None

    def get_state(self):
        return ''.join(self.board)

    def available_actions(self):
        return [i for i in range(9) if self.board[i] == ' ']

    def check_winner(self):
        wins = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                (0, 3, 6), (1, 4, 7), (2, 5, 8),
                (0, 4, 8), (2, 4, 6)]
        for a, b, c in wins:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] != ' ':
                self.winner = self.board[a]
                self.done = True
                return
        if ' ' not in self.board:
            self.winner = 'Draw'
            self.done = True

    def step(self, action, player):
        if self.board[action] != ' ':
            return self.get_state(), -10, True
        self.board[action] = player
        self.check_winner()
        return self.get_state(), self.reward(player), self.done

    def reward(self, player):
        if self.winner == player:
            return 1
        elif self.winner == 'Draw':
            return 0.5
        elif self.winner and self.winner != player:
            return -1
        return 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    board = data['board']
    user_pos = data['pos']

    game = TicTacToe()
    game.board = board

    if board[user_pos] == ' ':
        game.step(user_pos, 'O')
        if not game.done:
            state = game.get_state()
            if state not in Q:
                Q[state] = [0] * 9
            valid_moves = game.available_actions()
            if valid_moves:
                ai_action = max(valid_moves, key=lambda x: Q[state][x])
                game.step(ai_action, 'X')

    return jsonify({
        'board': game.board,
        'winner': game.winner,
        'done': game.done
    })

if __name__ == '__main__':
    app.run(debug=True)
