import socket
import threading
import arcade

# 設定視窗
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Russian Roulette"

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.player_name = ""
        self.message = "Connecting to server..."
        self.connected = False
        self.matching = False
        self.client_socket = None
        self.game_started = False
        self.life = 0
        self.bullet_chamber = []
        self.turn = False

    def setup(self):
        # 嘗試連線到伺服器
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(('127.0.0.1', 9999))
            self.connected = True
            self.message = "Enter your name and press 'Start Matching'"
        except Exception as e:
            self.message = f"Unable to connect to server. Retrying... {e}"
            threading.Timer(5.0, self.setup).start()

    def on_draw(self):
        arcade.start_render()
        # 背景顏色
        arcade.set_background_color(arcade.color.BLACK)
        # 顯示訊息
        arcade.draw_text(self.message, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 18)
        if self.connected and not self.matching:
            # 顯示輸入框和提示文字
            arcade.draw_text("Name:", 20, SCREEN_HEIGHT - 80, arcade.color.WHITE, 18)
            arcade.draw_rectangle_filled(200, SCREEN_HEIGHT - 80, 200, 30, arcade.color.WHITE)
            arcade.draw_text(self.player_name, 110, SCREEN_HEIGHT - 90, arcade.color.BLACK, 18)
            arcade.draw_text("Press 'Enter' to start matching", 20, SCREEN_HEIGHT - 120, arcade.color.WHITE, 18)
        elif self.game_started:
            # 顯示遊戲開始後的訊息
            arcade.draw_text(f"Your life: {self.life}", 20, SCREEN_HEIGHT - 80, arcade.color.WHITE, 18)
            arcade.draw_text(f"Bullet chamber: {self.bullet_chamber}", 20, SCREEN_HEIGHT - 120, arcade.color.WHITE, 18)
            if self.turn:
                arcade.draw_text("Your turn! Press '1' to shoot opponent, '2' to shoot yourself", 20, SCREEN_HEIGHT - 160, arcade.color.WHITE, 18)

    def on_key_press(self, key, modifiers):
        if self.connected and not self.matching:
            if key == arcade.key.ENTER:
                if self.player_name:
                    self.client_socket.send(self.player_name.encode('utf-8'))
                    self.matching = True
                    self.message = "Matching..."
                    threading.Thread(target=self.receive_messages).start()
            elif key == arcade.key.BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif key == arcade.key.SPACE:
                self.player_name += " "
            else:
                self.player_name += chr(key)
        elif self.game_started and self.turn:
            if key == arcade.key.KEY_1:
                self.client_socket.send("shoot opponent".encode('utf-8'))
                self.turn = False
            elif key == arcade.key.KEY_2:
                self.client_socket.send("shoot self".encode('utf-8'))
                self.turn = False

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if "Game start!" in message:
                    self.game_started = True
                    parts = message.split(", ")
                    if len(parts) > 1:
                        try:
                            self.life = int(parts[1].split(": ")[1])  # 確保是有效的數字
                        except ValueError:
                            self.message = f"Error in life value format: {parts[1].split(': ')[1]}"
                            return
                elif "Your turn" in message:
                    self.turn = True
                elif "Update" in message:
                    parts = message.split(", ")
                    if len(parts) > 1:
                        try:
                            self.life = int(parts[1].split(": ")[1])  # 確保是有效的數字
                        except ValueError:
                            self.message = f"Error in life value format: {parts[1].split(': ')[1]}"
                            return
                elif "Game over" in message:
                    self.message = message
                    self.game_started = False
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