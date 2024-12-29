import socket


class Player:
    def __init__(self, name: str, life: int, socket: socket.socket):
        self.name = name
        self.life = life
        self.turn = False
        self.socket = socket

    def send(self, message: str) -> int:
        return self.socket.send(message.encode("utf-8"))

    def recv(self, bufsize: int) -> str:
        return self.socket.recv(bufsize).decode("utf-8")
