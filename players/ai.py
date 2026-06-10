import time
import math
import random
import numpy as np
from typing import Tuple
from helper import get_valid_actions, check_win, fetch_remaining_time, get_neighbours


# =========================
# MCTS NODE
# =========================
class MCTSNode:
    def __init__(self, state, player_to_move, parent=None, move=None):
        self.state = state
        self.player_to_move = player_to_move  # IMPORTANT FIX
        self.parent = parent
        self.move = move

        self.children = []
        self.visits = 0
        self.wins = 0

        self.untried_moves = get_valid_actions(state)

    def expand(self, move, new_state, next_player):
        child = MCTSNode(
            new_state,
            player_to_move=next_player,
            parent=self,
            move=move
        )
        self.children.append(child)
        return child

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, exploration_weight=1.2):
        best_score = -float("inf")
        best_child = None

        for child in self.children:
            if child.visits == 0:
                score = float("inf")
            else:
                exploitation = child.wins / child.visits
                exploration = exploration_weight * math.sqrt(
                    math.log(self.visits + 1) / child.visits
                )
                score = exploitation + exploration

            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)

    def is_terminal(self):
        if len(get_valid_actions(self.state)) == 0:
            return True

        if self.move is None:
            return False

        return (
            check_win(self.state, self.move, 1)[0] or
            check_win(self.state, self.move, 2)[0]
        )

    # =========================
    # SIMULATION (ROLLOUT)
    # =========================
    def Simulation(self, root_player):
        current_state = self.state.copy()
        current_player = self.player_to_move

        while True:
            valid_moves = get_valid_actions(current_state)

            if not valid_moves:
                return 0.5  # draw

            move = self._nearest_neighbor_preference(
                valid_moves,
                current_state
            )

            current_state[move] = current_player

            win, _ = check_win(current_state, move, current_player)
            if win:
                return 1 if current_player == root_player else 0

            current_player = 3 - current_player

    def _nearest_neighbor_preference(self, valid_moves, state):
        if self.move is None or random.random() < 0.5:
            return random.choice(valid_moves)

        neighbors = get_neighbours(state.shape[0], self.move)
        close_moves = [m for m in valid_moves if m in neighbors]

        return random.choice(close_moves) if close_moves else random.choice(valid_moves)


# =========================
# AI PLAYER
# =========================
class AIPlayer:
    def __init__(self, player_number: int, timer):
        self.player_number = player_number
        self.type = 'ai'
        self.player_string = f'Player {player_number}: ai'
        self.timer = timer

    def get_move(self, state: np.array) -> Tuple[int, int]:

        moves = get_valid_actions(state)

        opponent = 3 - self.player_number

        # -------------------------
        # 1. Immediate win check
        # -------------------------
        for move in moves:
            new_state = state.copy()
            new_state[move] = self.player_number

            if check_win(new_state, move, self.player_number)[0]:
                return move

        # -------------------------
        # 2. Block opponent win
        # -------------------------
        for move in moves:
            new_state = state.copy()
            new_state[move] = opponent

            if check_win(new_state, move, opponent)[0]:
                return move

        # -------------------------
        # 3. MCTS
        # -------------------------
        root = MCTSNode(state, player_to_move=self.player_number)

        start_time = time.time()
        time_limit = fetch_remaining_time(self.timer, self.player_number) * 0.9

        max_iterations = 1000
        iterations = 0

        while time.time() - start_time < time_limit and iterations < max_iterations:

            node = self._select(root)

            if not node.is_terminal() and node.untried_moves:
                node = self._expand(node)

            result = node.Simulation(self.player_number)
            node.backpropagate(result)

            iterations += 1

        # -------------------------
        # 4. Choose best move
        # -------------------------
        if root.children:
            best_child = root.best_child(exploration_weight=0)
            return best_child.move

        return random.choice(moves)

    # =========================
    # SELECTION
    # =========================
    def _select(self, node):
        while not node.is_terminal():
            if not node.is_fully_expanded():
                return node
            node = node.best_child()
        return node

    # =========================
    # EXPANSION
    # =========================
    def _expand(self, node):
        move = random.choice(node.untried_moves)
        node.untried_moves.remove(move)

        new_state = node.state.copy()
        new_state[move] = node.player_to_move

        next_player = 3 - node.player_to_move

        return node.expand(move, new_state, next_player)
