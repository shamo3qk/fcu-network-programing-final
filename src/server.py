import socket
import threading
from match_maker import MatchMaker

INCOMING_IP_ANY = "0.0.0.0"
SERVER_PORT = 9999


# 處理客戶端連線
def handle_client(client_socket, match_maker):
    try:
        player_name = client_socket.recv(1024).decode("utf-8")
        if not player_name:
            raise ValueError("Player name is empty.")
        print(f"Player {player_name} connected.")

        match_maker.add_player(client_socket, player_name)
    except UnicodeDecodeError:
        print("Error decoding player name.")
        client_socket.send(b"Invalid player name format.")
        client_socket.close()
    except socket.timeout:
        print("Connection timed out.")
        client_socket.send(b"Connection timed out.")
        client_socket.close()
    except socket.error as e:
        print(f"Socket error {e}")
        client_socket.send(b"Socket error occurred.")
        client_socket.close()
    except ValueError as e:
        print(f"Value error: {e}")
        client_socket.send(f"Invalid player name: `{str(e)}`".encode("utf-8"))
        client_socket.close()
    except Exception as e:
        print(f"Unexpected error: {e}")
        client_socket.send(b"An unexpected error occurred.")
        client_socket.close()


# 設定 Matchmaker & 伺服器
def main():
    match_maker = MatchMaker()
    threading.Thread(target=match_maker.start_matching, daemon=True).start()
    print("Matchmaker started.")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((INCOMING_IP_ANY, SERVER_PORT))
    server.listen(5)
    print(f"Server started on port {SERVER_PORT}.")

    try:
        while True:
            try:
                client_socket, addr = server.accept()
                print(f"Accepted connection from {addr}")
                threading.Thread(
                    target=handle_client, args=(client_socket, match_maker)
                ).start()
            except socket.error as e:
                print(f"Socket error: {e}")
                continue
            except Exception as e:
                print(f"Unexcepted error: {e}")
                continue
    except KeyboardInterrupt:
        print("\nShutting down server.")
    except Exception as e:
        print(f"Unexcepted error: {e}")
    finally:
        server.close()
        print("Server terminated.")


if __name__ == "__main__":
    main()
