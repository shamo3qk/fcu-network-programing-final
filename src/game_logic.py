import time
from bullet_manager import BulletManager

# 定義總子彈數與實彈數
MAX_LIFE = 3  # 最大生命值
TOTAL_BULLETS = 6  # 總子彈數
LIVE_BULLETS = 1  # 實彈數


def start_game(player1, player2):
    """執行遊戲邏輯"""
    player1_socket, player1_name = player1
    player2_socket, player2_name = player2

    try:
        # 初始化遊戲狀態
        player1_life = MAX_LIFE
        player2_life = MAX_LIFE

        # 通知玩家匹配成功
        player1_socket.send(
            f"Match found! Your opponent: {player2_name}".encode("utf-8")
        )
        player2_socket.send(
            f"Match found! Your opponent: {player1_name}".encode("utf-8")
        )
        time.sleep(1)

        # 發送初始生命值
        player1_socket.send(f"Game start! Your life: {player1_life}".encode("utf-8"))
        player2_socket.send(f"Game start! Your life: {player2_life}".encode("utf-8"))

        # 初始化遊戲
        bullet_manager = BulletManager(TOTAL_BULLETS, LIVE_BULLETS)

        # 開始遊戲邏輯循環
        game_loop(player1, player2, player1_life, player2_life, bullet_manager)

    except Exception as e:
        print(f"Error during game: {e}")
        player1_socket.close()
        player2_socket.close()


def game_loop(player1, player2, player1_life, player2_life, bullet_manager):
    turn = 0  # 0 表示 player1 的回合，1 表示 player2 的回合
    while player1_life > 0 and player2_life > 0:
        current_player = player1 if turn == 0 else player2
        opponent_player = player2 if turn == 0 else player1
        current_life = player1_life if turn == 0 else player2_life
        opponent_life = player2_life if turn == 0 else player1_life

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
                # 擊中對方，延續行動
            else:
                # 對對方發射空彈，換人
                turn = 1 - turn
        elif action == "shoot self":
            if bullet_manager.shoot():
                current_life -= 1  # 自己生命值 -1
                if current_life == 0:
                    current_player[0].send("Game over, You lose!".encode("utf-8"))
                    opponent_player[0].send("Game over, You win!".encode("utf-8"))
                    break
                # 對自己發射實彈，換人
                turn = 1 - turn
            else:
                # 對自己開空彈，延續行動
                pass

        # 每回合都發送更新的生命值
        current_player[0].send(f"Update, Your life: {current_life}".encode("utf-8"))
        opponent_player[0].send(f"Update, Your life: {opponent_life}".encode("utf-8"))

        # 更新玩家生命值
        if turn == 0: # player1 的回合
            player1_life = current_life
            player2_life = opponent_life
        else: # player2 的回合
            player2_life = current_life
            player1_life = opponent_life