from flask import Flask, render_template, request, redirect, url_for, jsonify
import random

app = Flask(__name__)

# Initialize game variables
def initialize_game():
    board = [[None for _ in range(7)] for _ in range(8)]  # 8 rows × 7 columns
    blocked_spaces = random.sample([(r, c) for r in range(8) for c in range(7)], 5)
    for r, c in blocked_spaces:
        board[r][c] = "Blocked"
    return board, blocked_spaces, "Player 1"

board, blocked_spaces, current_player = initialize_game()

# Helper to check win conditions
def check_winner(board):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for r in range(8):
        for c in range(7):
            if board[r][c] in ["Player 1", "Player 2"]:
                for dr, dc in directions:
                    try:
                        if all(
                            0 <= r + i * dr < 8 and
                            0 <= c + i * dc < 7 and
                            board[r + i * dr][c + i * dc] == board[r][c]
                            for i in range(4)
                        ):
                            return board[r][c]
                    except IndexError:
                        continue
    return None

@app.route("/")
def index():
    return render_template("index.html", board=board, current_player=current_player, blocked_spaces=blocked_spaces)

@app.route("/play/<int:column>", methods=["POST"])
def play(column):
    global board, current_player

    # Find the lowest available row in the chosen column
    for row in range(7, -1, -1):  # Iterate bottom-up
        if board[row][column] is None:
            board[row][column] = current_player
            winner = check_winner(board)
            if winner:
                return jsonify({"winner": winner})
            current_player = "Player 2" if current_player == "Player 1" else "Player 1"
            return jsonify({"board": board, "current_player": current_player})
    return jsonify({"error": "Column is full"}), 400

@app.route("/reset", methods=["POST"])
def reset():
    global board, blocked_spaces, current_player
    board, blocked_spaces, current_player = initialize_game()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
