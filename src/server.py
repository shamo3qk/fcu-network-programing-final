import socket
import threading
import time
from bullet_manager import BulletManager

# 定義總子彈數與實彈數
MAX_LIFE = 3  # 最大生命值
TOTAL_BULLETS = 6  # 總子彈數
LIVE_BULLETS = 1  # 實彈數

# 儲存匹配佇列中的玩家
match_queue = []


# 處理客戶端連線的函數
def handle_client(client_socket):
    global match_queue
    try:
        # 接收玩家名稱
        player_name = client_socket.recv(1024).decode("utf-8")
        print(f"Player {player_name} connected.")

        # 將玩家加入匹配佇列
        match_queue.append((client_socket, player_name))

        # 檢查匹配佇列是否有兩名玩家
        if len(match_queue) >= 2:
            # 取出兩名玩家
            player1 = match_queue.pop(0)
            player2 = match_queue.pop(0)

            # 通知兩名玩家匹配成功並開始遊戲
            player1[0].send("Match found! Starting game...".encode("utf-8"))
            player2[0].send("Match found! Starting game...".encode("utf-8"))
            # 等待一秒
            time.sleep(1)

            # 初始化遊戲狀態
            player1_life = MAX_LIFE
            player2_life = MAX_LIFE
            # print(f"player1_life: {player1_life}, player2_life: {player2_life}")

            # 發送遊戲準備訊息
            player1[0].send(f"Game start! Your life: {player1_life}".encode("utf-8"))
            player2[0].send(f"Game start! Your life: {player2_life}".encode("utf-8"))
            # 等待一秒
            time.sleep(1)

            bullet_manager = BulletManager(TOTAL_BULLETS, LIVE_BULLETS)
            # 開始遊戲邏輯
            game_loop(player1, player2, player1_life, player2_life, bullet_manager)
    except Exception as e:
        print(f"Error: {e}")
        client_socket.close()


def game_loop(player1, player2, player1_life, player2_life, bullet_manager):
    turn = 0  # 0 表示 player1 的回合，1 表示 player2 的回合
    while player1_life > 0 and player2_life > 0:
        current_player = player1 if turn == 0 else player2
        opponent_player = player2 if turn == 0 else player1
        current_life = player1_life if turn == 0 else player2_life
        opponent_life = player2_life if turn == 0 else player1_life

        # 發送遊戲開始訊息，去掉了 Bullet chamber
        current_player[0].send(f"Game start! Your life: {current_life}".encode("utf-8"))
        opponent_player[0].send(
            f"Game start! Your life: {opponent_life}".encode("utf-8")
        )
        time.sleep(1)

        current_player[0].send("Your turn".encode("utf-8"))
        action = current_player[0].recv(1024).decode("utf-8")

        # 根據行動更新遊戲邏輯
        if action == "shoot opponent":
            if bullet_manager.shoot():
                opponent_life -= 1  # 對手生命值 -1
                if opponent_life == 0:
                    current_player[0].send("Game over, You win!".encode("utf-8"))
                    opponent_player[0].send("Game over, You lose!".encode("utf-8"))
                    break
            else:
                turn = 1 - turn  # 換人回合
        elif action == "shoot self":
            if bullet_manager.shoot():
                current_life -= 1  # 自己生命值 -1
                if current_life == 0:
                    current_player[0].send("Game over, You lose!".encode("utf-8"))
                    opponent_player[0].send("Game over, You win!".encode("utf-8"))
                    break
            else:
                turn = 1 - turn  # 換人回合

        # 每回合都發送更新的生命值，去掉了 Bullet chamber
        current_player[0].send(f"Update, Your life: {current_life}".encode("utf-8"))
        opponent_player[0].send(f"Update, Your life: {opponent_life}".encode("utf-8"))

        # 更新玩家生命值
        if turn == 0:
            player1_life = current_life
            player2_life = opponent_life
        else:
            player2_life = current_life
            player1_life = opponent_life


# 設定伺服器
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(5)
    print("Server started on port 9999.")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    start_server()
