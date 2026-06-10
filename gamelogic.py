# gamelogic.py
import numpy as np
from helper import get_valid_actions, check_win

class HavannahGameLogic:
    def __init__(self, board_state, layers):
        self.state = board_state
        self.layers = layers
        self.current_player_num = 1
        self.winner = None
        self.game_over = False
        self.winning_path = []
        self.structure_formed = None

    def make_move(self, move: tuple):
        """Attempts to make a move, returns True on success, False on failure."""
        if self.game_over:
            return False

        valid_actions = get_valid_actions(self.state, self.current_player_num)
        if move not in valid_actions:
            print(f"Invalid move {move} for player {self.current_player_num}")
            return False

        # Apply the move
        self.state[move] = self.current_player_num

        # Check for a win
        win, way = check_win(self.state, move, self.current_player_num, self.winning_path)
        if win:
            self.game_over = True
            self.winner = self.current_player_num
            self.structure_formed = way
        else:
            # Switch to the next player
            self.current_player_num = 3 - self.current_player_num
        
        return True

    def get_game_state_json(self):
        """
        Returns the current state in a format friendly for web transfer (JSON).
        This version is robust and converts all potential NumPy numbers to standard Python types.
        """
        
        # Explicitly convert winning_path coordinates to standard Python ints
        serializable_path = [[int(coord[0]), int(coord[1])] for coord in self.winning_path]
        
        # THE FIX: Also ensure 'winner' is a standard Python int, handling the case where it's None.
        serializable_winner = int(self.winner) if self.winner is not None else None
        
        return {
            'board': self.state.tolist(), # .tolist() already handles the board
            'currentPlayer': int(self.current_player_num), # Also cast this for safety
            'gameOver': self.game_over,
            'winner': serializable_winner, # Use the new, safe winner variable
            'winningStructure': self.structure_formed,
            'winningPath': serializable_path, # Use the new, safe list
        }