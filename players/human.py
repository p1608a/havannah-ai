import sys
import threading
import time
import numpy as np
from typing import Tuple
from multiprocessing import Value
from helper import get_valid_actions, fetch_remaining_time, HEXAGON_COORDS, CLICK_EVENT


class HumanPlayer:
    def __init__(self, player_number, timer):
        self.player_number = player_number
        self.type = 'human'
        self.player_string = f'Player {player_number}: human'
        self.TLE_MOVE = (-1, -1)
        self.timer = timer

    @staticmethod
    def get_action(inp: str) -> Tuple[int, int]:
        try:
            x, y = map(int, inp.strip().split(','))
            return x, y
        except Exception:
            print("Invalid input format. Use: row,col")
            return -1, -1

    def readline_with_timeout_thread(self, move):
        try:
            inp = input()  # blocking input
            x, y = map(int, inp.strip().split(','))
            move[0].value = x
            move[1].value = y
        except:
            move[0].value = self.TLE_MOVE[0]
            move[1].value = self.TLE_MOVE[1]

    def get_input(self, time_limit) -> Tuple[int, int]:
        print('Enter your move (e.g., 2,3) or click a cell on GUI: ')
        move = (Value('i', -2), Value('i', -2))

        input_thread = threading.Thread(target=self.readline_with_timeout_thread, args=(move,))
        input_thread.daemon = True
        input_thread.start()

        start_time = time.time()

        while time.time() - start_time < time_limit:
            # If user typed move
            if move[0].value >= 0 and move[1].value >= 0:
                return move[0].value, move[1].value

            # If user clicked on GUI
            if CLICK_EVENT[0]:
                try:
                    polygon_id = CLICK_EVENT[0].widget.find_withtag("current")[0]
                    move_coords = HEXAGON_COORDS.get(polygon_id, self.TLE_MOVE)
                    CLICK_EVENT[0] = False
                    print("Clicked Move:", move_coords)
                    return move_coords
                except Exception as e:
                    print("GUI click error:", e)
                    return self.TLE_MOVE

            time.sleep(0.1)  # Don't hog CPU

        print("Time Limit Exceeded")
        return self.TLE_MOVE

    def get_move(self, state: Tuple[np.array]) -> Tuple[int, int]:
        """
        Given the current state returns the next action

        Parameters
        ----------
        state: Tuple[np.array]
            - a numpy array containing the state of the board:
              0 = empty, 1 = player 1, 2 = player 2, 3 = blocked

        Returns
        -------
        Tuple[int, int]: action (row, col)
        """
        valid_actions = get_valid_actions(state, self.player_number)
        action = self.get_input(fetch_remaining_time(self.timer, self.player_number))

        if action == self.TLE_MOVE:
            print('Time Limit Exceeded')
        elif action not in valid_actions:
            print('Invalid Move: Choose from:', valid_actions)
            print('Turning to other player...')
            print("ACTION == ", action)

        return action
