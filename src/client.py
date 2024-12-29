import socket
import threading
import arcade
from enum import IntEnum

# 伺服器 IP & Port
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999

# 設定視窗
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Russian Roulette"


class PlayerState(IntEnum):
    DISCONNECTED = 0
    IN_LOBBY = 1
    MATCHING = 2
    IN_GAME = 3
    IN_END_SCREEN = 4

    def next_state(self):
        return STATE_TRANSITIONS.get(self, PlayerState.DISCONNECTED)


# 玩家的狀態流轉
STATE_TRANSITIONS = {
    PlayerState.DISCONNECTED: PlayerState.IN_LOBBY,
    PlayerState.IN_LOBBY: PlayerState.MATCHING,
    PlayerState.MATCHING: PlayerState.IN_GAME,
    PlayerState.IN_GAME: PlayerState.IN_END_SCREEN,
    PlayerState.IN_END_SCREEN: PlayerState.IN_LOBBY,
}


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.player_name = ""
        self.life = 0
        self.state = PlayerState.DISCONNECTED
        self.turn = False
        self.client_socket = None
        self.bullet_chamber = []
        self.message = "Connecting to server..."
        # self.action_handlers = {
        #     "Game start!": self.handle_game_start,
        #     "Game over": self.handle_game_over,
        #     "Your turn": self.handle_your_turn,
        # }

    def setup(self):
        # 嘗試連線到伺服器
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((SERVER_IP, SERVER_PORT))
            self.state = self.state.next_state()
            self.message = "Enter your name and press 'Start Matching'"
        except Exception as e:
            self.message = f"Unable to connect to server. Retrying... {e}"
            threading.Timer(5.0, self.setup).start()

    def draw_lobby_ui(self):
        arcade.draw_text("Name:", 20, SCREEN_HEIGHT - 80, arcade.color.WHITE, 18)
        arcade.draw_rectangle_filled(
            200, SCREEN_HEIGHT - 80, 200, 30, arcade.color.WHITE
        )
        arcade.draw_text(
            self.player_name, 110, SCREEN_HEIGHT - 90, arcade.color.BLACK, 18
        )
        arcade.draw_text(
            "Press 'Enter' to start matching",
            20,
            SCREEN_HEIGHT - 120,
            arcade.color.WHITE,
            18,
        )

    def draw_game_ui(self):
        arcade.draw_text(
            f"Your life: {self.life}",
            20,
            SCREEN_HEIGHT - 80,
            arcade.color.WHITE,
            18,
        )
        arcade.draw_text(
            f"Bullet chamber: {self.bullet_chamber}",
            20,
            SCREEN_HEIGHT - 120,
            arcade.color.WHITE,
            18,
        )
        if self.turn:
            arcade.draw_text(
                "Your turn! Press '1' to shoot opponent, '2' to shoot yourself",
                20,
                SCREEN_HEIGHT - 160,
                arcade.color.WHITE,
                18,
            )

    def draw_end_screen_ui(self):
        arcade.draw_text(
            "Press 'q' to return to lobby",
            SCREEN_WIDTH / 3,
            SCREEN_HEIGHT - 200,
            arcade.color.WHITE,
            18,
        )

    def on_draw(self):
        arcade.start_render()
        arcade.set_background_color(arcade.color.BLACK)
        arcade.draw_text(
            f"Command: {self.message}", 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 18
        )

        match self.state:
            case PlayerState.IN_LOBBY:
                self.draw_lobby_ui()
            case PlayerState.IN_GAME:
                self.draw_game_ui()
            case PlayerState.IN_END_SCREEN:
                self.draw_end_screen_ui()

    def on_lobby_key_press(self, key, modifiers):
        """處理大廳狀態的按鍵輸入"""
        match key:
            case arcade.key.ENTER:
                if self.player_name:
                    self.client_socket.send(self.player_name.encode("utf-8"))
                    self.state = self.state.next_state()
                    self.message = "Matching..."
                    threading.Thread(target=self.handle_command).start()
            case arcade.key.BACKSPACE:
                self.player_name = self.player_name[:-1]
            case arcade.key.SPACE:
                self.player_name += " "
            case arcade.key.Q:
                self.close()
            case _:
                self.player_name += chr(key)

    def on_game_key_press(self, key, modifiers):
        """處理遊戲中狀態的按鍵輸入"""
        match key:
            case arcade.key.KEY_1:
                self.client_socket.send("0".encode("utf-8"))
                self.turn = False
            case arcade.key.KEY_2:
                self.client_socket.send("1".encode("utf-8"))
                self.turn = False
            case arcade.key.Q:
                self.close()

    def on_end_screen_key_press(self, key, modifiers):
        match key:
            case arcade.key.Q:
                self.state = PlayerState.IN_LOBBY

    def on_key_press(self, key, modifiers):
        match self.state:
            case PlayerState.IN_LOBBY:
                self.on_lobby_key_press(key, modifiers)
            case PlayerState.IN_GAME:
                if self.turn:
                    self.on_game_key_press(key, modifiers)
            case PlayerState.IN_END_SCREEN:
                self.on_end_screen_key_press(key, modifiers)

    def handle_command(self):
        """
        持續從伺服器接收指令，並根據指令更新遊戲狀態
        """
        while True:
            try:
                message = self.client_socket.recv(1024).decode("utf-8")
                if "Game start!" in message:
                    self.state = PlayerState.IN_GAME
                    parts = message.split(", ")
                    if len(parts) > 1:
                        try:
                            self.life = int(parts[1].split(": ")[1])  # 確保是有效的數字
                        except ValueError:
                            self.message = (
                                f"Error in life value format: {parts[1].split(': ')[1]}"
                            )
                            return
                elif "Your turn" in message:
                    self.turn = True
                elif "Update" in message:
                    parts = message.split(", ")
                    if len(parts) > 1:
                        try:
                            self.life = int(parts[1].split(": ")[1])  # 確保是有效的數字
                        except ValueError:
                            self.message = (
                                f"Error in life value format: {parts[1].split(': ')[1]}"
                            )
                            return
                elif "Game over" in message:
                    self.message = message
                    self.state = PlayerState.IN_END_SCREEN
                    self.player_name = ""
                self.message = message
            except Exception as e:
                self.message = f"Connection lost. {e}"
                break


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
