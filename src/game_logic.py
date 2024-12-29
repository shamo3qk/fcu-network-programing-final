import time
from queue import Queue
from bullet_manager import BulletManager
from player import Player

# 定義總子彈數與實彈數
MAX_LIFE = 3  # 最大生命值
TOTAL_BULLETS = 6  # 總子彈數
LIVE_BULLETS = 1  # 實彈數


class Game:
    def __init__(self, player1: Player, player2: Player, bullet_manager: BulletManager):
        self.players = [player1, player2]
        self.bullet_manager = bullet_manager
        self.turn = 0  # 初始回合
        self.action_handlers = {
            "shoot opponent": self.handle_shoot_opponent,
            "shoot self": self.handle_shoot_self,
        }

    def handle_shoot_opponent(self) -> bool:
        opponent_player = self.get_opponent_player()

        self.switch_turn()
        if self.bullet_manager.shoot():
            opponent_player.life -= 1
            return opponent_player.life == 0
        return False

    def handle_shoot_self(self) -> bool:
        current_player = self.get_current_player()

        if self.bullet_manager.shoot():
            current_player.life -= 1
            self.switch_turn()
            return current_player.life == 0
        return False

    def get_current_player(self) -> Player:
        return self.players[self.turn]

    def get_opponent_player(self) -> Player:
        return self.players[1 - self.turn]

    def switch_turn(self):
        self.turn = (self.turn + 1) % len(self.players)

    def process_action(self, action: str) -> bool:
        handler = self.action_handlers.get(action)
        if handler:
            return handler()
        self.get_current_player().send("Invalid action!")
        return False


def start_game(player1, player2):
    """執行遊戲邏輯"""
    player1_socket, player1_name = player1
    player2_socket, player2_name = player2
    player1 = Player(player1_name, MAX_LIFE, player1_socket)
    player2 = Player(player2_name, MAX_LIFE, player2_socket)

    try:
        # 通知玩家匹配成功
        player1.send(f"Match found! Your opponent: {player2.name}")
        player2.send(f"Match found! Your opponent: {player1.name}")
        time.sleep(1)

        # 發送初始生命值
        player1.send(f"Game start! Your life: {player1.life}")
        player2.send(f"Game start! Your life: {player2.life}")

        # 初始化遊戲
        bullet_manager = BulletManager(TOTAL_BULLETS, LIVE_BULLETS)

        # 開始遊戲邏輯循環
        game_loop(player1, player2, bullet_manager)

    except Exception as e:
        print(f"Error during game: {e}")
        player1_socket.close()
        player2_socket.close()


def game_loop(player1: Player, player2: Player, bullet_manager: BulletManager):
    event_queue = Queue()
    game = Game(player1, player2, bullet_manager)

    while all(player.life > 0 for player in game.players):
        current_player = game.get_current_player()
        opponent_player = game.get_opponent_player()

        current_player.send("Your turn")
        action = current_player.recv(1024)

        event_queue.put((game.turn, action))

        while not event_queue.empty():
            turn, action = event_queue.get()
            if game.process_action(action):
                current_player.send("Game over, You win!")
                opponent_player.send("Game over, You lose!")
                return

            for player in game.players:
                player.send(f"Update, Your life: {player.life}")
