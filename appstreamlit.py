import streamlit as st
import numpy as np
import random
import pickle
import os

# Q-Table
Q = {}

# Game Environment
class TicTacToe:
    def __init__(self):  # ✅ Corrected constructor
        self.reset()

    def reset(self):
        self.board = [' '] * 9
        self.done = False
        self.winner = None
        return self.get_state()

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
                return True
        if ' ' not in self.board:
            self.done = True
            self.winner = 'Draw'
        return False

    def reward(self, player):
        if self.winner == player:
            return 1
        elif self.winner == 'Draw':
            return 0.5
        elif self.winner and self.winner != player:
            return -1
        return 0

    def step(self, action, player):
        if self.board[action] != ' ':
            return self.get_state(), -10, True  # Invalid move
        self.board[action] = player
        self.check_winner()
        return self.get_state(), self.reward(player), self.done

# Q-Learning setup
alpha = 0.5
gamma = 0.9
epsilon = 0.1

def train_q_learning(episodes=10000):
    global Q
    env = TicTacToe()
    for _ in range(episodes):
        state = env.reset()
        done = False
        while not done:
            if state not in Q:
                Q[state] = [0] * 9
            # Choose action
            if random.random() < epsilon:
                action = random.choice(env.available_actions())
            else:
                q_vals = Q[state]
                action = max(env.available_actions(), key=lambda x: q_vals[x])
            next_state, reward, done = env.step(action, 'X')
            if next_state not in Q:
                Q[next_state] = [0] * 9
            # Opponent (random)
            if not done:
                opp_action = random.choice(env.available_actions())
                next_state, reward, done = env.step(opp_action, 'O')
                if next_state not in Q:
                    Q[next_state] = [0] * 9
            Q[state][action] += alpha * (reward + gamma * max(Q[next_state]) - Q[state][action])
            state = next_state

    with open("q_table.pkl", "wb") as f:
        pickle.dump(Q, f)

def load_q_table():
    global Q
    if os.path.exists("q_table.pkl"):
        with open("q_table.pkl", "rb") as f:
            Q = pickle.load(f)
    else:
        train_q_learning()

# Streamlit Setup
st.title("Tic Tac Toe with Reinforcement Learning")
st.markdown("Play as for Human *O*, AI plays as **X**")

load_q_table()

# Session state
if 'game' not in st.session_state:
    st.session_state.game = TicTacToe()
if 'ai_started' not in st.session_state:
    st.session_state.ai_started = False

def ai_move():
    game = st.session_state.game
    state = game.get_state()
    if state not in Q:
        Q[state] = [0] * 9
    q_vals = Q[state]
    valid_moves = game.available_actions()
    action = max(valid_moves, key=lambda x: q_vals[x])
    game.step(action, 'X')

def user_move(pos):
    game = st.session_state.game
    if not game.done and game.board[pos] == ' ':
        game.step(pos, 'O')
        if not game.done:
            ai_move()

# Trigger AI to start first if needed
if not st.session_state.ai_started:
    ai_move()
    st.session_state.ai_started = True

# Display the board
cols = st.columns(3)
for i in range(9):
    with cols[i % 3]:
        cell = st.session_state.game.board[i]
        if st.button(cell if cell != ' ' else ' ', key=str(i)):
            user_move(i)

# Show result
if st.session_state.game.done:
    winner = st.session_state.game.winner
    if winner == 'O':
        st.success("You Win!")
    elif winner == 'X':
        st.error("AI Wins!")
    else:
        st.info("It's a Draw!")
    if st.button("Play Again"):
        st.session_state.game = TicTacToe()
        st.session_state.ai_started = False
