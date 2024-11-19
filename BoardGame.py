#Example Flask App for a hexaganal tile game
#Logic is in this python file

from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Constants
ROWS = 7
COLS = 8
BLOCKED_COUNT = 5


class Connect4Game:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        """Initialize the game state."""
        self.board = [['' for _ in range(COLS)] for _ in range(ROWS)]
        self.blocked_positions = self._generate_blocked_positions()
        self.current_player = 'Player 1'
        self.winner = None

    def _generate_blocked_positions(self):
        """Randomly choose blocked positions."""
        blocked = random.sample(range(ROWS * COLS), BLOCKED_COUNT)
        return {(pos // COLS, pos % COLS) for pos in blocked}

    def place_chip(self, column):
        """Place a chip in the selected column."""
        if self.winner:
            return {'error': 'Game over. Please restart to play again.'}

        chip = 'Blue' if self.current_player == 'Player 1' else 'Black'

        # Place the chip in the lowest available row in the column
        for row in range(ROWS - 1, -1, -1):
            if (row, column) not in self.blocked_positions and self.board[row][column] == '':
                self.board[row][column] = chip
                if self.check_winner(row, column, chip):
                    self.winner = self.current_player
                elif self.is_draw():
                    self.winner = 'Draw'
                else:
                    self.current_player = 'Player 2' if self.current_player == 'Player 1' else 'Player 1'
                return {'board': self.board, 'current_player': self.current_player, 'winner': self.winner}

        return {'error': 'Column is full'}

    def is_draw(self):
        """Check if the board is full."""
        return all(
            self.board[row][col] != '' or (row, col) in self.blocked_positions
            for row in range(ROWS)
            for col in range(COLS)
        )

    def check_winner(self, row, col, chip):
        """Check if the current move results in a win."""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # Right, Down, Diagonal Down-Right, Diagonal Down-Left

        for dr, dc in directions:
            count = 1  # Count the current chip
            for step in [1, -1]:  # Check both directions
                r, c = row + step * dr, col + step * dc
                while 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == chip:
                    count += 1
                    r += step * dr
                    c += step * dc
            if count >= 4:
                return True
        return False


# Initialize a single game instance
game = Connect4Game()


@app.route('/')
def index():
    """Render the game board."""
    return render_template(
        'index.html',
        board=game.board,
        blocked=list(game.blocked_positions),
        current_player=game.current_player
    )


@app.route('/move', methods=['POST'])
def move():
    """Handle a player's move."""
    data = request.json
    column = data.get('column')

    if column is None or not (0 <= column < COLS):
        return jsonify({'error': 'Invalid column'}), 400

    result = game.place_chip(column)
    return jsonify(result)


@app.route('/reset', methods=['POST'])
def reset():
    """Reset the game."""
    game.reset_game()
    return jsonify({'board': game.board, 'current_player': game.current_player, 'blocked': list(game.blocked_positions)})


if __name__ == '__main__':
    app.run(debug=True)
