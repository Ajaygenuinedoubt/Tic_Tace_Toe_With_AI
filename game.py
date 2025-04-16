import streamlit as st
import numpy as np
import random
import pickle
import os
from streamlit.components.v1 import html

# Q-Table
Q = {}

# Game Environment
class TicTacToe:
    def __init__(self):
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
            return self.get_state(), -10, True
        self.board[action] = player
        self.check_winner()
        return self.get_state(), self.reward(player), self.done

# Q-Learning setup
alpha, gamma, epsilon = 0.5, 0.9, 0.1

def train_q_learning(episodes=10000):
    global Q
    env = TicTacToe()
    for _ in range(episodes):
        state = env.reset()
        done = False
        while not done:
            if state not in Q:
                Q[state] = [0] * 9
            if random.random() < epsilon:
                action = random.choice(env.available_actions())
            else:
                action = max(env.available_actions(), key=lambda x: Q[state][x])
            next_state, reward, done = env.step(action, 'X')
            if next_state not in Q:
                Q[next_state] = [0] * 9
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
st.set_page_config(page_title="RL Tic Tac Toe", page_icon="🎮", layout="centered")
st.title("🎮 Tic Tac Toe with Q-Learning AI")
st.markdown("You play as **O**, the AI plays as **X**.")

load_q_table()

# Sound toggle
play_sound = st.checkbox("🔊 Enable Sound Effects", value=True)

# Session state
if 'game' not in st.session_state:
    st.session_state.game = TicTacToe()
if 'ai_started' not in st.session_state:
    st.session_state.ai_started = False

def play_audio(sound_type):
    if not play_sound: return
    sound_map = {
        'click': 'https://www.fesliyanstudios.com/play-mp3/387',
        'win': 'https://www.fesliyanstudios.com/play-mp3/4381',
        'lose': 'https://www.fesliyanstudios.com/play-mp3/4382',
        'draw': 'https://www.fesliyanstudios.com/play-mp3/4383'
    }
    html(f"""
    <audio autoplay>
        <source src="{sound_map[sound_type]}" type="audio/mp3">
    </audio>
    """, height=0)

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
        play_audio("click")
        if not game.done:
            ai_move()

# AI starts first
if not st.session_state.ai_started:
    ai_move()
    st.session_state.ai_started = True

# Render Board with Animations
st.markdown("""
<style>
.tic-button {
    font-size: 32px !important;
    height: 80px !important;
    width: 80px !important;
    border: 3px solid #00ffe1 !important;
    background-color: #0f1117;
    color: white !important;
    transition: 0.2s ease-in-out;
}
.tic-button:hover {
    background-color: #00ffe1;
    color: #000;
}
</style>
""", unsafe_allow_html=True)

cols = st.columns(3)
for i in range(9):
    with cols[i % 3]:
        cell = st.session_state.game.board[i]
        if st.button(cell if cell != ' ' else ' ', key=str(i), help=f"Click to place O", type="primary"):
            user_move(i)

# Outcome
if st.session_state.game.done:
    winner = st.session_state.game.winner
    if winner == 'O':
        st.success("🎉 You Win!")
        play_audio("win")
    elif winner == 'X':
        st.error("💻 AI Wins!")
        play_audio("lose")
    else:
        st.info("🤝 It's a Draw!")
        play_audio("draw")

    if st.button("🔁 Play Again"):
        st.session_state.game = TicTacToe()
        st.session_state.ai_started = False
