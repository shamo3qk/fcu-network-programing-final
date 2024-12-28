import threading
import socket
import time
from typing import List, Tuple
from game_logic import start_game


class MatchMaker:
    def __init__(self):
        self.queue: List[Tuple[socket.socket, str]] = []
        self.lock = threading.Lock()

    def add_player(self, player_socket: socket.socket, player_name: str) -> None:
        with self.lock:
            self.queue.append((player_socket, player_name))
            print(f"Player {player_name} added to match queue.")

    def get_match(self):
        with self.lock:
            if len(self.queue) >= 2:
                return self.queue.pop(0), self.queue.pop(0)
            return None, None

    def start_matching(self):
        while True:
            match self.get_match():
                case (player1, player2) if player1 and player2:
                    print("Match found! Starting game...")
                    start_game(player1, player2)
                case _:
                    time.sleep(0.1)
