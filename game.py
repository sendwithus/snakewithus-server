import json
import requests

from uuid import uuid4

from pymongo import MongoClient

import settings


def get_mongodb():
    client = MongoClient(host=settings.MONGODB_URL)
    return client[settings.MONGODB_DATABASE]


class Game(object):

    document = None
    _MONGODB_COLLECTION_NAME = 'snakewithus'

    def __init__(self, game_id=None, player_urls=None, local_player=None):
        self._mongodb = get_mongodb()
        db = self._get_mongo_collection()

        self.created = False
        self.game_id = game_id

        if not self.game_id:
            self.game_id = self._gen_id()
            self.created = True
            players = []

            if not player_urls:
                player_urls = []

            for url in player_urls:
                player = {
                    'url': url,
                    'id': self._gen_id(),
                    'name': '',
                    'head_img_url': '',
                    queue: []
                }

                players.append(player)

            document = db.insert({
                'id': self.game_id,
                'players': players,
                'local_player': local_player,
                'state': {}
            })
        else:
            self.document = self._fetch_game()

    def _gen_id(self):
        return uuid4().urn

    def _get_mongo_collection(self):
        return self._mongodb[self._MONGODB_COLLECTION_NAME]

    def _fetch_game(self):
        db = self._get_mongo_collection()
        search = db.find({id: self.game_id})
        if len(search) != 1:
            return None

        self.document = search[0]

    def save(self):
        """saves game to mongo"""
        db = self._get_mongo_collection()
        db.save(self.document)

    def tick(self):


        snapshot = self.document.game_state
        self.document.players = [
            {
                url 
                name
                id
                queue: []
                head_img_url
            }
        ]
        
        def apply_player_move(direction):
            # update snapshot board object to reflect move


        snapshot = self.document.game_state


        # post to each client to obtain move
        for url in self.player_urls:
            response = requests.post(url)
            # get dir and pass to apply_player_move

        # resolve collisions / food



        # update mongo store



