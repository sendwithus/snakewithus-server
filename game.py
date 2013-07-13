import requests

from uuid import uuid4


class Game(object):

    def __init__(self, game_id=None):
        if not game_id:
            self.game_id = uuid4().urn
            self.created = True
        else:
            pass
            # hit datastore and pull game data for id
        self.player_urls = []
        self.local_player = None

    def tick(self):
        for url in self.player_urls:
            response = requests.post()
