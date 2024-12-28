import unittest
import socket
from src.match_maker import MatchMaker


class TestMatchMaker(unittest.TestCase):
    def test_add_player(self):
        match_maker = MatchMaker()
        socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        match_maker.add_player(socket1, "Joe")
        match_maker.add_player(socket2, "Ben")

        self.assertEqual(match_maker.queue, [(socket1, "Joe"), (socket2, "Ben")])

        socket1.close()
        socket2.close()

    def test_get_match_success(self):
        match_maker = MatchMaker()
        socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        match_maker.add_player(socket1, "Joe")
        match_maker.add_player(socket2, "Ben")

        self.assertEqual(match_maker.get_match(), ((socket1, "Joe"), (socket2, "Ben")))

        socket1.close()
        socket2.close()

    def test_get_match_failure(self):
        match_maker = MatchMaker()
        socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        match_maker.add_player(socket1, "Joe")

        self.assertEqual(match_maker.get_match(), (None, None))

        socket1.close()
